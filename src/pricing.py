import os


def public_pricing() -> dict:
    pro_url = os.getenv("STRIPE_PRO_URL", "").strip()
    creator_url = os.getenv("STRIPE_CREATOR_URL", "").strip()
    return {
        "plans": [
            {
                "id": "free",
                "name": "Free",
                "price": 0,
                "description": "Try the research workflow before connecting paid services.",
                "checkout_enabled": True,
                "checkout_url": "#research",
            },
            {
                "id": "pro",
                "name": "Pro",
                "price": 15,
                "description": "Watchlists, saved research, and live-provider workflows.",
                "checkout_enabled": bool(pro_url),
                "checkout_url": pro_url or None,
            },
            {
                "id": "creator",
                "name": "Creator / Research",
                "price": 39,
                "description": "Higher-volume research workflows for creators and small teams.",
                "checkout_enabled": bool(creator_url),
                "checkout_url": creator_url or None,
            },
        ]
    }
