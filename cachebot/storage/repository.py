from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Dict, List, Optional

from cachebot.models.deal import Deal
from cachebot.models.user import MerchantApplication, UserProfile


@dataclass(slots=True)
class RateSettings:
    usd_rate: Decimal
    fee_percent: Decimal

    def to_dict(self) -> dict[str, str]:
        return {
            "usd_rate": str(self.usd_rate),
            "fee_percent": str(self.fee_percent),
        }

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> "RateSettings":
        return cls(
            usd_rate=Decimal(data["usd_rate"]),
            fee_percent=Decimal(data["fee_percent"]),
        )


@dataclass(slots=True)
class StorageState:
    deals: List[Deal]
    balances: Dict[int, Decimal]
    settings: Optional[RateSettings]
    user_roles: Dict[int, str]
    applications: List[MerchantApplication]
    profiles: Dict[int, UserProfile]
    deal_sequence: int
    merchant_since: Dict[int, str]


class StateRepository:
    def __init__(self, path: Path) -> None:
        self._path = path
        self._lock = asyncio.Lock()
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._state = self._load()

    def snapshot(self) -> StorageState:
        return self._state

    async def replace_state(self, state: StorageState) -> None:
        async with self._lock:
            self._state = state
            self._write_locked()

    async def persist_deals_and_balances(
        self, deals: List[Deal], balances: Dict[int, Decimal], deal_sequence: int | None = None
    ) -> None:
        async with self._lock:
            sequence = self._state.deal_sequence if deal_sequence is None else deal_sequence
            self._state = StorageState(
                deals=deals,
                balances=balances,
                settings=self._state.settings,
                user_roles=self._state.user_roles,
                applications=self._state.applications,
                profiles=self._state.profiles,
                deal_sequence=sequence,
                merchant_since=self._state.merchant_since,
            )
            self._write_locked()

    async def persist_settings(self, settings: RateSettings) -> None:
        async with self._lock:
            self._state = StorageState(
                deals=self._state.deals,
                balances=self._state.balances,
                settings=settings,
                user_roles=self._state.user_roles,
                applications=self._state.applications,
                profiles=self._state.profiles,
                deal_sequence=self._state.deal_sequence,
                merchant_since=self._state.merchant_since,
            )
            self._write_locked()

    async def persist_user_data(
        self,
        roles: Dict[int, str],
        applications: List[MerchantApplication],
        profiles: Dict[int, UserProfile],
        merchant_since: Dict[int, str],
    ) -> None:
        async with self._lock:
            self._state = StorageState(
                deals=self._state.deals,
                balances=self._state.balances,
                settings=self._state.settings,
                user_roles=roles,
                applications=applications,
                profiles=profiles,
                deal_sequence=self._state.deal_sequence,
                merchant_since=merchant_since,
            )
            self._write_locked()

    def _write_locked(self) -> None:
        payload = {
            "deals": [deal.to_dict() for deal in self._state.deals],
            "balances": {str(uid): str(amount) for uid, amount in self._state.balances.items()},
            "settings": self._state.settings.to_dict() if self._state.settings else None,
            "user_roles": {str(uid): role for uid, role in self._state.user_roles.items()},
            "applications": [app.to_dict() for app in self._state.applications],
            "profiles": {
                str(uid): profile.to_dict() for uid, profile in self._state.profiles.items()
            },
            "deal_sequence": self._state.deal_sequence,
            "merchant_since": self._state.merchant_since,
        }
        tmp = self._path.with_suffix(".tmp")
        tmp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        tmp.replace(self._path)

    def _load(self) -> StorageState:
        if not self._path.exists():
            return StorageState(
                deals=[],
                balances={},
                settings=None,
                user_roles={},
                applications=[],
                profiles={},
                deal_sequence=0,
                merchant_since={},
            )
        raw = json.loads(self._path.read_text(encoding="utf-8"))
        deals = [Deal.from_dict(item) for item in raw.get("deals", [])]
        balances = {
            int(uid): Decimal(amount) for uid, amount in (raw.get("balances") or {}).items()
        }
        settings = None
        if raw.get("settings"):
            settings = RateSettings.from_dict(raw["settings"])
        roles = {int(uid): role for uid, role in (raw.get("user_roles") or {}).items()}
        applications = [
            MerchantApplication.from_dict(item) for item in raw.get("applications", [])
        ]
        profiles = {
            int(uid): UserProfile.from_dict(data)
            for uid, data in (raw.get("profiles") or {}).items()
        }
        merchant_since = {
            int(uid): value for uid, value in (raw.get("merchant_since") or {}).items()
        }
        return StorageState(
            deals=deals,
            balances=balances,
            settings=settings,
            user_roles=roles,
            applications=applications,
            profiles=profiles,
            deal_sequence=int(raw.get("deal_sequence") or 0),
            merchant_since=merchant_since,
        )
