"""Stripe billing — checkout sessions, webhook handling, entitlement activation.

Backend-first and safe:
- when Stripe is not configured (no secret key), the service runs in offline
  'mock' mode: it never calls Stripe and never moves real money, but the full
  state machine (checkout -> webhook -> entitlement) is still exercisable for
  CLI smoke tests;
- when configured, it creates real Checkout Sessions and verifies webhook
  signatures with the Stripe SDK;
- webhook handling is idempotent (events are de-duplicated by Stripe event id);
- secrets are never logged in full.
"""

from __future__ import annotations

import json
import hashlib
import hmac
import logging
from dataclasses import dataclass
from pathlib import Path

from .config import Settings
from .storage import LocalStore

logger = logging.getLogger("pricinglibrary_rag.billing")

# Stripe events we act on.
_COMPLETED = "checkout.session.completed"
_REVOCATIONS = {
    "customer.subscription.deleted": "canceled",
    "charge.refunded": "revoked_refund",
    "refund.created": "revoked_refund",
    "charge.dispute.created": "revoked_chargeback",
}
_PLANS = ("starter", "student", "pro")
STARTER_KIT_PRODUCT_ID = "market-finance-starter-kit"


class BillingError(RuntimeError):
    """Raised for invalid plans, missing config, or webhook verification errors."""


@dataclass(frozen=True)
class CheckoutSession:
    id: str
    url: str
    plan: str
    mode: str  # 'live' (real Stripe) | 'mock' (offline, no charge)


@dataclass(frozen=True)
class ProductCheckoutSession:
    id: str
    url: str
    product_id: str
    mode: str  # always 'payment'; one-shot purchases never mutate subscriptions


@dataclass(frozen=True)
class ProductArtifact:
    path: Path
    manifest: dict


def _redact(secret: str | None) -> str:
    if not secret:
        return "absent"
    return f"{secret[:4]}...{secret[-2:]} (len {len(secret)})"


class BillingService:
    def __init__(self, settings: Settings, store: LocalStore) -> None:
        self.settings = settings
        self.store = store
        self._stripe = None
        if settings.billing_configured or settings.starter_kit_checkout_configured:
            import stripe  # imported lazily so the package is optional

            stripe.api_key = settings.stripe_secret_key
            self._stripe = stripe

    # --- introspection ----------------------------------------------------
    @property
    def configured(self) -> bool:
        return self.settings.billing_configured

    def config_summary(self) -> dict:
        return {
            "configured": self.configured,
            "mode": "live" if self.configured else "mock",
            "checkout_mode": self.settings.billing_checkout_mode,
            "plans": [p for p in _PLANS if p in self.settings.stripe_prices]
            or list(_PLANS),
            "webhook_secret_present": bool(self.settings.stripe_webhook_secret),
            "identity_required": self.settings.security_enforced,
            "starter_kit": {
                "checkout_configured": self.settings.starter_kit_checkout_configured,
                "price_present": bool(self.settings.starter_kit_price_id),
                "bundle_path_present": self.settings.starter_kit_bundle_path is not None,
                "manifest_path_present": self.settings.starter_kit_manifest_path is not None,
            },
        }

    def _price_for(self, plan: str) -> str:
        plan = (plan or "").strip().lower()
        if plan not in _PLANS:
            raise BillingError(f"unknown plan '{plan}'. Valid plans: {', '.join(_PLANS)}")
        price = self.settings.stripe_prices.get(plan)
        if not price and self.configured:
            raise BillingError(
                f"no Stripe price configured for plan '{plan}'. Set STRIPE_PRICE_{plan.upper()}."
            )
        return price or f"price_mock_{plan}"

    # --- checkout ---------------------------------------------------------
    def create_checkout_session(
        self,
        plan: str,
        *,
        email: str | None = None,
        user_id: str | None = None,
        success_url: str | None = None,
        cancel_url: str | None = None,
    ) -> CheckoutSession:
        if self.settings.security_enforced and not self.settings.source_rights_cleared:
            raise BillingError("commercial source-rights clearance is required before production checkout")
        price = self._price_for(plan)
        success_url = success_url or self.settings.billing_success_url
        cancel_url = cancel_url or self.settings.billing_cancel_url

        if not self.configured:
            # Offline mock: deterministic fake session, NO Stripe call, NO charge.
            logger.info(
                "[billing] mock checkout plan=%s (Stripe not configured: key=%s)",
                plan,
                _redact(self.settings.stripe_secret_key),
            )
            sid = f"cs_mock_{plan}"
            return CheckoutSession(
                id=sid,
                url=f"{cancel_url}#mock-checkout-{plan}",
                plan=plan,
                mode="mock",
            )

        params = {
            "mode": self.settings.billing_checkout_mode,
            "line_items": [{"price": price, "quantity": 1}],
            "success_url": success_url,
            "cancel_url": cancel_url,
            "metadata": {
                "plan": plan,
                **({"user_id": user_id} if user_id else {}),
                **({"email": email} if email else {}),
            },
            "allow_promotion_codes": True,
        }
        if user_id:
            params["client_reference_id"] = user_id
        if email:
            params["customer_email"] = email
        session = self._stripe.checkout.Session.create(**params)
        logger.info("[billing] live checkout created id=%s plan=%s", session.id, plan)
        return CheckoutSession(id=session.id, url=session.url, plan=plan, mode="live")

    def create_product_checkout_session(
        self,
        product_id: str,
        *,
        user_id: str,
        email: str | None = None,
    ) -> ProductCheckoutSession:
        product_id = (product_id or "").strip().lower()
        if product_id != STARTER_KIT_PRODUCT_ID:
            raise BillingError("unknown one-shot product")
        if not user_id:
            raise BillingError("authenticated user identity is required")
        if self.settings.security_enforced and not self.settings.source_rights_cleared:
            raise BillingError("commercial source-rights clearance is required before production checkout")
        if not self.settings.starter_kit_checkout_configured or self._stripe is None:
            raise BillingError(
                "starter kit checkout is unavailable; configure STRIPE_SECRET_KEY and STRIPE_PRICE_STARTER_KIT"
            )
        # Refuse to sell a missing, incomplete, or corrupted artifact.
        self.product_artifact(product_id)
        metadata = {"product_id": product_id, "user_id": user_id}
        params = {
            "mode": "payment",
            "line_items": [{"price": self.settings.starter_kit_price_id, "quantity": 1}],
            "success_url": self.settings.starter_kit_success_url,
            "cancel_url": self.settings.starter_kit_cancel_url,
            "client_reference_id": user_id,
            "metadata": metadata,
            "payment_intent_data": {"metadata": metadata},
            "allow_promotion_codes": True,
        }
        if email:
            params["customer_email"] = email
        session = self._stripe.checkout.Session.create(**params)
        logger.info(
            "[billing] one-shot checkout created id=%s product_id=%s user_id=%s",
            session.id,
            product_id,
            user_id,
        )
        return ProductCheckoutSession(
            id=session.id,
            url=session.url,
            product_id=product_id,
            mode="payment",
        )

    def product_artifact(self, product_id: str) -> ProductArtifact:
        product_id = (product_id or "").strip().lower()
        if product_id != STARTER_KIT_PRODUCT_ID:
            raise BillingError("unknown one-shot product")
        bundle_path = self.settings.starter_kit_bundle_path
        manifest_path = self.settings.starter_kit_manifest_path
        if bundle_path is None or manifest_path is None:
            raise BillingError("starter kit bundle and manifest paths are not configured")
        if not bundle_path.is_file() or not manifest_path.is_file():
            raise BillingError("starter kit bundle or manifest is missing")
        try:
            raw_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise BillingError("starter kit manifest is unreadable or invalid JSON") from exc
        if not isinstance(raw_manifest, dict):
            raise BillingError("starter kit manifest must be a JSON object")
        if raw_manifest.get("ready") is not True:
            raise BillingError("starter kit manifest is not ready")
        if raw_manifest.get("product_id") != product_id:
            raise BillingError("starter kit manifest product_id mismatch")
        version = raw_manifest.get("version")
        if not isinstance(version, str) or not version.strip():
            raise BillingError("starter kit manifest version is missing")
        if raw_manifest.get("deliverable_count") != 7:
            raise BillingError("starter kit manifest must contain exactly 7 deliverables")
        deliverables = raw_manifest.get("deliverables")
        if (
            not isinstance(deliverables, list)
            or len(deliverables) != 7
            or any(not isinstance(item, dict) or item.get("complete") is not True for item in deliverables)
        ):
            raise BillingError("starter kit manifest deliverables are incomplete")
        if raw_manifest.get("missing") not in (None, []):
            raise BillingError("starter kit manifest reports missing files")
        declared_bundle = raw_manifest.get("bundle")
        if not isinstance(declared_bundle, dict):
            raise BillingError("starter kit manifest bundle section is missing")
        declared_name = declared_bundle.get("path")
        if (
            not isinstance(declared_name, str)
            or Path(declared_name).name != declared_name
            or declared_name != bundle_path.name
        ):
            raise BillingError("starter kit manifest filename mismatch")
        declared_sha = str(declared_bundle.get("sha256") or "").strip().lower()
        if len(declared_sha) != 64 or any(ch not in "0123456789abcdef" for ch in declared_sha):
            raise BillingError("starter kit manifest sha256 is missing or invalid")
        digest = hashlib.sha256()
        size_bytes = 0
        try:
            with bundle_path.open("rb") as handle:
                for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                    digest.update(chunk)
                    size_bytes += len(chunk)
        except OSError as exc:
            raise BillingError("starter kit bundle cannot be read") from exc
        if not hmac.compare_digest(digest.hexdigest(), declared_sha):
            raise BillingError("starter kit bundle checksum mismatch")
        declared_size = declared_bundle.get("size")
        if declared_size != size_bytes:
            raise BillingError("starter kit bundle size mismatch")
        manifest = dict(raw_manifest)
        manifest["version"] = version.strip()
        manifest["missing"] = []
        manifest["bundle"] = {
            "path": bundle_path.name,
            "size": size_bytes,
            "sha256": declared_sha,
        }
        return ProductArtifact(path=bundle_path, manifest=manifest)

    def product_entitlement(self, user_id: str, product_id: str) -> dict:
        entitlement = self.store.get_product_entitlement(user_id, product_id)
        active = bool(entitlement and entitlement.get("status") == "active")
        return {
            "user_id": user_id,
            "product_id": product_id,
            "active": active,
            "status": entitlement.get("status") if entitlement else None,
        }

    def product_availability(self, product_id: str) -> dict:
        product_id = (product_id or "").strip().lower()
        checkout_configured = (
            product_id == STARTER_KIT_PRODUCT_ID
            and self.settings.starter_kit_checkout_configured
        )
        artifact_ready = False
        version = None
        if product_id == STARTER_KIT_PRODUCT_ID:
            try:
                artifact = self.product_artifact(product_id)
                artifact_ready = True
                version = artifact.manifest["version"]
            except BillingError:
                # Public readiness is deliberately non-diagnostic: no paths,
                # checksums, provider state, or validation reason are exposed.
                pass
        return {
            "product_id": product_id,
            "sale_ready": bool(checkout_configured and artifact_ready and self.settings.commercial_content_ready),
            "checkout_configured": bool(checkout_configured),
            "artifact_ready": artifact_ready,
            "version": version,
        }

    # --- webhook ----------------------------------------------------------
    def handle_webhook(self, payload: bytes, sig_header: str) -> dict:
        """Verify, de-duplicate and process a Stripe webhook. Returns a summary."""
        secret = self.settings.stripe_webhook_secret
        if not secret:
            raise BillingError(
                "webhook secret missing. Set STRIPE_WEBHOOK_SECRET to verify signatures."
            )
        import stripe

        raw = payload.decode("utf-8") if isinstance(payload, (bytes, bytearray)) else str(payload)
        # Verify the signature only (no StripeObject), then parse the JSON
        # ourselves — robust across SDK versions and trivially serializable.
        try:
            stripe.WebhookSignature.verify_header(raw, sig_header, secret, tolerance=300)
        except Exception as exc:  # SignatureVerificationError
            logger.warning("[billing] webhook signature rejected: %s", type(exc).__name__)
            raise BillingError(f"invalid webhook signature: {exc}") from exc
        try:
            event = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise BillingError(f"invalid webhook payload: {exc}") from exc

        event_id = event.get("id") or ""
        event_type = event.get("type") or ""

        if event_id and self.store.billing_event_seen(event_id):
            logger.info("[billing] duplicate event %s ignored", event_id)
            return {"handled": False, "duplicate": True, "type": event_type, "id": event_id}

        result: dict = {"handled": False, "type": event_type, "id": event_id}
        obj = (event.get("data") or {}).get("object") or {}

        if event_type == _COMPLETED:
            metadata = obj.get("metadata") or {}
            user_id = metadata.get("user_id") or obj.get("client_reference_id")
            product_id = metadata.get("product_id")
            email = (
                obj.get("customer_email")
                or (obj.get("customer_details") or {}).get("email")
                or metadata.get("email")
            )
            plan = metadata.get("plan") or "starter"
            if product_id:
                if product_id != STARTER_KIT_PRODUCT_ID:
                    result["error"] = "unknown product_id"
                elif not user_id:
                    result["error"] = "no authenticated identity on product session"
                elif obj.get("mode") != "payment" or obj.get("payment_status") != "paid":
                    result["error"] = "one-shot checkout is not a paid payment session"
                elif not obj.get("payment_intent"):
                    result["error"] = "one-shot checkout has no payment intent"
                else:
                    self.store.upsert_product_entitlement(
                        user_id,
                        product_id,
                        status="active",
                        stripe_customer_id=obj.get("customer"),
                        stripe_checkout_session_id=obj.get("id"),
                        stripe_payment_intent_id=obj.get("payment_intent"),
                        source="stripe:checkout.completed",
                    )
                    logger.info(
                        "[billing] product entitlement granted user_id=%s product_id=%s",
                        user_id,
                        product_id,
                    )
                    result.update(
                        {
                            "handled": True,
                            "kind": "product",
                            "user_id": user_id,
                            "product_id": product_id,
                            "status": "active",
                        }
                    )
            elif not email or (self.settings.security_enforced and not user_id):
                logger.warning("[billing] %s without authenticated identity; entitlement withheld", _COMPLETED)
                result["error"] = "no authenticated identity on session"
            else:
                self.store.upsert_entitlement(
                    email,
                    plan,
                    user_id=user_id,
                    status="active",
                    stripe_customer_id=obj.get("customer"),
                    stripe_subscription_id=obj.get("subscription"),
                    source="stripe:checkout.completed",
                )
                logger.info("[billing] entitlement granted user_id=%s plan=%s", user_id or "legacy-local", plan)
                result.update(
                    {
                        "handled": True,
                        "user_id": user_id,
                        "email": email,
                        "plan": plan,
                        "status": "active",
                    }
                )

        elif event_type in _REVOCATIONS:
            metadata = obj.get("metadata") or {}
            user_id = metadata.get("user_id")
            product_id = metadata.get("product_id")
            customer_id = obj.get("customer")
            subscription_id = obj.get("subscription")
            payment_intent_id = obj.get("payment_intent")
            if event_type == "customer.subscription.deleted":
                subscription_id = obj.get("id") or subscription_id

            charge = obj.get("charge")
            if isinstance(charge, dict):
                charge_meta = charge.get("metadata") or {}
                user_id = user_id or charge_meta.get("user_id")
                product_id = product_id or charge_meta.get("product_id")
                customer_id = customer_id or charge.get("customer")
                payment_intent_id = payment_intent_id or charge.get("payment_intent")
            elif isinstance(charge, str) and self._stripe is not None:
                try:
                    charge_obj = self._stripe.Charge.retrieve(charge)
                    customer_id = customer_id or charge_obj.get("customer")
                    charge_meta = charge_obj.get("metadata") or {}
                    user_id = user_id or charge_meta.get("user_id")
                    product_id = product_id or charge_meta.get("product_id")
                    payment_intent_id = payment_intent_id or charge_obj.get("payment_intent")
                except Exception as exc:  # provider failure must not grant rights
                    logger.warning("[billing] unable to resolve charge %s: %s", charge, type(exc).__name__)

            product_entitlement = self.store.find_product_entitlement_for_stripe(
                product_id=product_id,
                user_id=user_id,
                payment_intent_id=payment_intent_id,
            )
            if product_entitlement:
                status = _REVOCATIONS[event_type]
                self.store.revoke_product_entitlement(
                    product_entitlement,
                    status=status,
                    source=f"stripe:{event_type}",
                )
                result.update(
                    {
                        "handled": True,
                        "kind": "product",
                        "user_id": product_entitlement.get("user_id"),
                        "product_id": product_entitlement.get("product_id"),
                        "status": status,
                    }
                )
            elif product_id == STARTER_KIT_PRODUCT_ID:
                result["error"] = "no matching starter kit payment entitlement"
            else:
                entitlement = self.store.find_entitlement_for_stripe(
                    user_id=user_id,
                    customer_id=customer_id,
                    subscription_id=subscription_id,
                )
                if entitlement:
                    status = _REVOCATIONS[event_type]
                    self.store.revoke_entitlement(
                        entitlement,
                        status=status,
                        source=f"stripe:{event_type}",
                    )
                    result.update(
                        {
                            "handled": True,
                            "user_id": entitlement.get("user_id"),
                            "status": status,
                        }
                    )
                else:
                    result["error"] = "no matching entitlement"

        if event_id:
            self.store.record_billing_event(event_id, event_type, event)
        return result

    # --- entitlement ------------------------------------------------------
    def entitlement(self, email: str | None = None, *, user_id: str | None = None) -> dict:
        ent = (
            self.store.get_entitlement_by_user_id(user_id)
            if user_id
            else self.store.get_entitlement(email or "")
        )
        if not ent or ent.get("status") != "active":
            return {
                "user_id": user_id,
                "email": (email or "").strip().lower() or None,
                "active": False,
                "plan": None,
            }
        return {
            "user_id": ent.get("user_id"),
            "email": ent["email"],
            "active": True,
            "plan": ent["plan"],
            "status": ent["status"],
        }
