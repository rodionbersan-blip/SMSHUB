from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from cachebot.config import Config
from cachebot.services.crypto_pay import CryptoPayClient
from cachebot.services.deals import DealService
from cachebot.services.kb_client import KBClient
from cachebot.services.rate_provider import RateProvider
from cachebot.services.users import UserService


@dataclass(slots=True)
class AppDeps:
    config: Config
    deal_service: DealService
    rate_provider: RateProvider
    crypto_pay: CryptoPayClient
    kb_client: KBClient
    user_service: UserService


_current: Optional[AppDeps] = None


def wire(deps: AppDeps) -> None:
    global _current
    _current = deps


def get_deps() -> AppDeps:
    if not _current:
        raise RuntimeError("Dependencies are not initialized")
    return _current
