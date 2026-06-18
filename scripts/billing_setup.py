"""Create the Stripe TEST products + recurring prices for the 3 plans, and write
their price ids into .env. Idempotent and test-mode-only by default.

- Refuses a live key (sk_live_) unless --allow-live is passed.
- Reuses an existing product (matched by metadata tpl_plan) instead of creating
  duplicates; reuses an existing valid price id already in .env.
- Writes STRIPE_PRICE_STARTER/STUDENT/PRO + TPL_BILLING_CHECKOUT_MODE=subscription
  into .env without clobbering other keys.

Usage:
    STRIPE_SECRET_KEY=sk_test_... python scripts/billing_setup.py
    python scripts/billing_setup.py            # reads key from .env
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from pricinglibrary_rag.config import _load_env_file  # noqa: E402

# plan key, display name, monthly amount in cents (EUR)
PLANS = [
    ("starter", "Starter", 900),
    ("student", "Student", 1900),
    ("pro", "Professional", 4900),
]
ENV_PATH = BACKEND_ROOT / ".env"


def _redact(secret: str) -> str:
    return f"{secret[:7]}...{secret[-2:]} (len {len(secret)})" if secret else "absent"


def _upsert_env(path: Path, updates: dict[str, str]) -> None:
    lines = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
    keys = set(updates)
    out: list[str] = []
    seen: set[str] = set()
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and "=" in stripped:
            k = stripped.split("=", 1)[0].strip()
            if k in keys:
                out.append(f"{k}={updates[k]}")
                seen.add(k)
                continue
        out.append(line)
    for k, v in updates.items():
        if k not in seen:
            out.append(f"{k}={v}")
    path.write_text("\n".join(out) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Set up Stripe test products/prices.")
    parser.add_argument("--allow-live", action="store_true", help="Permit a sk_live_ key (dangerous).")
    args = parser.parse_args()

    _load_env_file()
    key = os.environ.get("STRIPE_SECRET_KEY") or os.environ.get("TPL_STRIPE_SECRET_KEY")
    print("=" * 60)
    print("  Stripe billing setup")
    print("=" * 60)
    print(f"[STEP 1] secret key  [STATUS] {'ok' if key else 'fail'}  [OUTPUT] {_redact(key or '')}")
    if not key:
        print("  [NEXT] Set STRIPE_SECRET_KEY (sk_test_...) in env or .env and re-run.")
        return 1
    if key.startswith("sk_live_") and not args.allow_live:
        print("  [STATUS] fail  [ERROR] refusing a LIVE key. Use a sk_test_ key (or --allow-live).")
        return 1

    import stripe

    stripe.api_key = key

    updates: dict[str, str] = {"TPL_BILLING_CHECKOUT_MODE": "subscription"}
    for plan, name, amount in PLANS:
        env_name = f"STRIPE_PRICE_{plan.upper()}"
        existing = os.environ.get(env_name)
        if existing:
            try:
                price = stripe.Price.retrieve(existing)
                if price and price.get("active"):
                    print(f"[plan {plan}] reuse existing price {existing} [STATUS] ok")
                    updates[env_name] = existing
                    continue
            except Exception:
                pass  # stale id -> recreate

        # find or create the product (idempotent by metadata)
        product = None
        try:
            found = stripe.Product.search(query=f"metadata['tpl_plan']:'{plan}'")
            product = found.data[0] if getattr(found, "data", None) else None
        except Exception:
            for p in stripe.Product.list(limit=100).auto_paging_iter():
                if (p.get("metadata") or {}).get("tpl_plan") == plan:
                    product = p
                    break
        if product is None:
            product = stripe.Product.create(
                name=f"ThePricingLibrary {name}",
                metadata={"tpl_plan": plan},
            )
            print(f"[plan {plan}] created product {product.id} [STATUS] ok")
        else:
            print(f"[plan {plan}] reuse product {product.id} [STATUS] ok")

        price = stripe.Price.create(
            product=product.id,
            unit_amount=amount,
            currency="eur",
            recurring={"interval": "month"},
            metadata={"tpl_plan": plan},
        )
        print(f"[plan {plan}] created price {price.id} ({amount/100:.0f}EUR/mo) [STATUS] ok")
        updates[env_name] = price.id

    _upsert_env(ENV_PATH, updates)
    print("-" * 60)
    print(f"[done] wrote {len(updates)} keys to {ENV_PATH}")
    for k, v in updates.items():
        print(f"  {k}={v}")
    print("Restart the backend to pick up the new prices.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
