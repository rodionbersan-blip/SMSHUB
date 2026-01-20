from __future__ import annotations

import os
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Iterable, Set

from dotenv import load_dotenv


@dataclass(slots=True)
class Config:
    telegram_bot_token: str
    crypto_pay_token: str | None
    admin_ids: Set[int]
    payment_window_minutes: int = 15
    offer_window_minutes: int = 15
    invoice_poll_interval: int = 30
    storage_path: Path = Path("var/state.json")
    kb_api_url: str | None = None
    kb_api_token: str | None = None
    default_usd_rate: Decimal = Decimal("100")
    fee_percent: Decimal = Decimal("1.0")
    withdraw_fee_percent: Decimal = Decimal("2.5")
    webapp_url: str = "https://cashnowshop.ru/app/"
    webhook_host: str = "0.0.0.0"
    webhook_port: int = 8080
    webhook_path: str = "/crypto-pay/webhook"
    crypto_pay_webhook_secret: str | None = None
    allow_unsafe_initdata: bool = False

    @classmethod
    def from_env(cls) -> "Config":
        load_dotenv()
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not token:
            raise RuntimeError("TELEGRAM_BOT_TOKEN is required")
        crypto_pay_token = os.getenv("CRYPTO_PAY_TOKEN") or None
        admin_ids = _parse_admin_ids(os.getenv("ADMIN_USER_IDS"))
        storage_path = Path(os.getenv("STATE_FILE", "var/state.json")).expanduser()
        if not storage_path.is_absolute():
            project_root = Path(__file__).resolve().parent.parent
            storage_path = (project_root / storage_path).resolve()
        payment_window = int(os.getenv("DEAL_TTL_MINUTES", "15"))
        offer_window = int(os.getenv("OFFER_TTL_MINUTES", "15"))
        poll_interval = int(os.getenv("INVOICE_POLL_INTERVAL", "30"))
        kb_api_url = os.getenv("KB_API_URL") or None
        kb_api_token = os.getenv("KB_API_TOKEN") or None
        default_rate = Decimal(os.getenv("DEFAULT_USD_RATE", "100"))
        fee_percent = Decimal(os.getenv("FEE_PERCENT", "1.0"))
        withdraw_fee_percent = Decimal(os.getenv("WITHDRAW_FEE_PERCENT", "2.5"))
        webapp_url = os.getenv("WEBAPP_URL", "https://cashnowshop.ru/app/")
        webhook_host = os.getenv("CRYPTO_PAY_WEBHOOK_HOST", "0.0.0.0")
        webhook_port = int(os.getenv("CRYPTO_PAY_WEBHOOK_PORT", "8080"))
        webhook_path = os.getenv("CRYPTO_PAY_WEBHOOK_PATH", "/crypto-pay/webhook")
        webhook_secret = os.getenv("CRYPTO_PAY_WEBHOOK_SECRET") or None
        allow_unsafe = os.getenv("ALLOW_UNSAFE_INITDATA", "0").lower() in {"1", "true", "yes"}
        return cls(
            telegram_bot_token=token,
            crypto_pay_token=crypto_pay_token,
            admin_ids=admin_ids,
            payment_window_minutes=payment_window,
            offer_window_minutes=offer_window,
            invoice_poll_interval=poll_interval,
            storage_path=storage_path,
            kb_api_url=kb_api_url,
            kb_api_token=kb_api_token,
            default_usd_rate=default_rate,
            fee_percent=fee_percent,
            withdraw_fee_percent=withdraw_fee_percent,
            webapp_url=webapp_url,
            webhook_host=webhook_host,
            webhook_port=webhook_port,
            webhook_path=webhook_path,
            crypto_pay_webhook_secret=webhook_secret,
            allow_unsafe_initdata=allow_unsafe,
        )


def _parse_admin_ids(raw: str | None) -> Set[int]:
    if not raw:
        return set()
    ids: Set[int] = set()
    for chunk in raw.replace(";", ",").split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        try:
            ids.add(int(chunk))
        except ValueError:
            raise ValueError(f"Invalid admin user id: {chunk}")
    return ids
