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
import logging
from dataclasses import dataclass

from .config import Settings
from .storage import LocalStore

logger = logging.getLogger("pricinglibrary_rag.billing")

# Stripe events we act on.
_COMPLETED = "checkout.session.completed"
_SUB_DELETED = "customer.subscription.deleted"
_PLANS = ("starter", "student", "pro")


class BillingError(RuntimeError):
    """Raised for invalid plans, missing config, or webhook verification errors."""


@dataclass(frozen=True)
class CheckoutSession:
    id: str
    url: str
    plan: str
    mode: str  # 'live' (real Stripe) | 'mock' (offline, no charge)


def _redact(secret: str | None) -> str:
    if not secret:
        return "absent"
    return f"{secret[:4]}...{secret[-2:]} (len {len(secret)})"


class BillingService:
    def __init__(self, settings: Settings, store: LocalStore) -> None:
        self.settings = settings
        self.store = store
        self._stripe = None
        if settings.billing_configured:
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
        success_url: str | None = None,
        cancel_url: str | None = None,
    ) -> CheckoutSession:
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
            "metadata": {"plan": plan},
            "allow_promotion_codes": True,
        }
        if email:
            params["customer_email"] = email
        session = self._stripe.checkout.Session.create(**params)
        logger.info("[billing] live checkout created id=%s plan=%s", session.id, plan)
        return CheckoutSession(id=session.id, url=session.url, plan=plan, mode="live")

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
            email = (
                obj.get("customer_email")
                or (obj.get("customer_details") or {}).get("email")
                or (obj.get("metadata") or {}).get("email")
            )
            plan = (obj.get("metadata") or {}).get("plan") or "starter"
            if not email:
                logger.warning("[billing] %s without email; cannot grant entitlement", _COMPLETED)
                result["error"] = "no email on session"
            else:
                self.store.upsert_entitlement(
                    email,
                    plan,
                    status="active",
                    stripe_customer_id=obj.get("customer"),
                    stripe_subscription_id=obj.get("subscription"),
                    source="stripe:checkout.completed",
                )
                logger.info("[billing] entitlement granted email=%s plan=%s", email, plan)
                result.update({"handled": True, "email": email, "plan": plan, "status": "active"})

        elif event_type == _SUB_DELETED:
            email = (obj.get("metadata") or {}).get("email")
            if email:
                ent = self.store.get_entitlement(email)
                self.store.upsert_entitlement(
                    email, (ent or {}).get("plan", "starter"), status="canceled",
                    source="stripe:subscription.deleted",
                )
                result.update({"handled": True, "email": email, "status": "canceled"})

        if event_id:
            self.store.record_billing_event(event_id, event_type, event)
        return result

    # --- entitlement ------------------------------------------------------
    def entitlement(self, email: str) -> dict:
        ent = self.store.get_entitlement(email)
        if not ent or ent.get("status") != "active":
            return {"email": email.strip().lower(), "active": False, "plan": None}
        return {
            "email": ent["email"],
            "active": True,
            "plan": ent["plan"],
            "status": ent["status"],
        }
