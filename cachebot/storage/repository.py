from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Dict, List, Optional

from cachebot.models.advert import Advert
from cachebot.models.balance_event import BalanceEvent
from cachebot.models.chat import ChatMessage
from cachebot.models.deal import Deal
from cachebot.models.dispute import Dispute
from cachebot.models.review import Review
from cachebot.models.user import MerchantApplication, UserProfile
from cachebot.models.topup import Topup


@dataclass(slots=True)
class RateSettings:
    usd_rate: Decimal
    fee_percent: Decimal
    withdraw_fee_percent: Decimal

    def to_dict(self) -> dict[str, str]:
        return {
            "usd_rate": str(self.usd_rate),
            "fee_percent": str(self.fee_percent),
            "withdraw_fee_percent": str(self.withdraw_fee_percent),
        }

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> "RateSettings":
        return cls(
            usd_rate=Decimal(data["usd_rate"]),
            fee_percent=Decimal(data["fee_percent"]),
            withdraw_fee_percent=Decimal(data.get("withdraw_fee_percent", "2.5")),
        )


@dataclass(slots=True)
class StorageState:
    deals: List[Deal]
    balances: Dict[int, Decimal]
    balance_events: List[BalanceEvent]
    settings: Optional[RateSettings]
    user_roles: Dict[int, str]
    applications: List[MerchantApplication]
    profiles: Dict[int, UserProfile]
    reviews: List[Review]
    disputes: List[Dispute]
    adverts: List[Advert]
    topups: List[Topup]
    chats: Dict[str, List[ChatMessage]]
    deal_sequence: int
    advert_sequence: int
    merchant_since: Dict[int, str]
    p2p_trading_enabled: Dict[int, bool]
    moderators: List[int]
    user_warnings: Dict[int, int]
    user_bans: List[int]
    user_deal_blocks: List[int]


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
        self,
        deals: List[Deal],
        balances: Dict[int, Decimal],
        deal_sequence: int | None = None,
        balance_events: List[BalanceEvent] | None = None,
    ) -> None:
        async with self._lock:
            sequence = self._state.deal_sequence if deal_sequence is None else deal_sequence
            self._state = StorageState(
                deals=deals,
                balances=balances,
                balance_events=balance_events or self._state.balance_events,
                settings=self._state.settings,
                user_roles=self._state.user_roles,
                applications=self._state.applications,
                profiles=self._state.profiles,
                reviews=self._state.reviews,
                disputes=self._state.disputes,
                adverts=self._state.adverts,
                topups=self._state.topups,
                chats=self._state.chats,
                deal_sequence=sequence,
                advert_sequence=self._state.advert_sequence,
                merchant_since=self._state.merchant_since,
                p2p_trading_enabled=self._state.p2p_trading_enabled,
                moderators=self._state.moderators,
                user_warnings=self._state.user_warnings,
                user_bans=self._state.user_bans,
                user_deal_blocks=self._state.user_deal_blocks,
            )
            self._write_locked()

    async def persist_settings(self, settings: RateSettings) -> None:
        async with self._lock:
            self._state = StorageState(
                deals=self._state.deals,
                balances=self._state.balances,
                balance_events=self._state.balance_events,
                settings=settings,
                user_roles=self._state.user_roles,
                applications=self._state.applications,
                profiles=self._state.profiles,
                reviews=self._state.reviews,
                disputes=self._state.disputes,
                adverts=self._state.adverts,
                topups=self._state.topups,
                chats=self._state.chats,
                deal_sequence=self._state.deal_sequence,
                advert_sequence=self._state.advert_sequence,
                merchant_since=self._state.merchant_since,
                p2p_trading_enabled=self._state.p2p_trading_enabled,
                moderators=self._state.moderators,
                user_warnings=self._state.user_warnings,
                user_bans=self._state.user_bans,
                user_deal_blocks=self._state.user_deal_blocks,
            )
            self._write_locked()

    async def persist_user_data(
        self,
        roles: Dict[int, str],
        applications: List[MerchantApplication],
        profiles: Dict[int, UserProfile],
        merchant_since: Dict[int, str],
        moderators: List[int],
        user_warnings: Dict[int, int],
        user_bans: List[int],
        user_deal_blocks: List[int],
    ) -> None:
        async with self._lock:
            self._state = StorageState(
                deals=self._state.deals,
                balances=self._state.balances,
                balance_events=self._state.balance_events,
                settings=self._state.settings,
                user_roles=roles,
                applications=applications,
                profiles=profiles,
                reviews=self._state.reviews,
                disputes=self._state.disputes,
                adverts=self._state.adverts,
                topups=self._state.topups,
                chats=self._state.chats,
                deal_sequence=self._state.deal_sequence,
                advert_sequence=self._state.advert_sequence,
                merchant_since=merchant_since,
                p2p_trading_enabled=self._state.p2p_trading_enabled,
                moderators=moderators,
                user_warnings=user_warnings,
                user_bans=user_bans,
                user_deal_blocks=user_deal_blocks,
            )
            self._write_locked()

    async def persist_reviews(self, reviews: List[Review]) -> None:
        async with self._lock:
            self._state = StorageState(
                deals=self._state.deals,
                balances=self._state.balances,
                balance_events=self._state.balance_events,
                settings=self._state.settings,
                user_roles=self._state.user_roles,
                applications=self._state.applications,
                profiles=self._state.profiles,
                reviews=reviews,
                disputes=self._state.disputes,
                adverts=self._state.adverts,
                topups=self._state.topups,
                chats=self._state.chats,
                deal_sequence=self._state.deal_sequence,
                advert_sequence=self._state.advert_sequence,
                merchant_since=self._state.merchant_since,
                p2p_trading_enabled=self._state.p2p_trading_enabled,
                moderators=self._state.moderators,
                user_warnings=self._state.user_warnings,
                user_bans=self._state.user_bans,
                user_deal_blocks=self._state.user_deal_blocks,
            )
            self._write_locked()

    async def persist_disputes(self, disputes: List[Dispute]) -> None:
        async with self._lock:
            self._state = StorageState(
                deals=self._state.deals,
                balances=self._state.balances,
                balance_events=self._state.balance_events,
                settings=self._state.settings,
                user_roles=self._state.user_roles,
                applications=self._state.applications,
                profiles=self._state.profiles,
                reviews=self._state.reviews,
                disputes=disputes,
                adverts=self._state.adverts,
                topups=self._state.topups,
                chats=self._state.chats,
                deal_sequence=self._state.deal_sequence,
                advert_sequence=self._state.advert_sequence,
                merchant_since=self._state.merchant_since,
                p2p_trading_enabled=self._state.p2p_trading_enabled,
                moderators=self._state.moderators,
                user_warnings=self._state.user_warnings,
                user_bans=self._state.user_bans,
                user_deal_blocks=self._state.user_deal_blocks,
            )
            self._write_locked()

    async def persist_adverts(
        self,
        adverts: List[Advert],
        advert_sequence: int,
        p2p_trading_enabled: Dict[int, bool],
    ) -> None:
        async with self._lock:
            self._state = StorageState(
                deals=self._state.deals,
                balances=self._state.balances,
                balance_events=self._state.balance_events,
                settings=self._state.settings,
                user_roles=self._state.user_roles,
                applications=self._state.applications,
                profiles=self._state.profiles,
                reviews=self._state.reviews,
                disputes=self._state.disputes,
                adverts=adverts,
                topups=self._state.topups,
                chats=self._state.chats,
                deal_sequence=self._state.deal_sequence,
                advert_sequence=advert_sequence,
                merchant_since=self._state.merchant_since,
                p2p_trading_enabled=p2p_trading_enabled,
                moderators=self._state.moderators,
                user_warnings=self._state.user_warnings,
                user_bans=self._state.user_bans,
                user_deal_blocks=self._state.user_deal_blocks,
            )
            self._write_locked()

    async def persist_topups(self, topups: List[Topup]) -> None:
        async with self._lock:
            self._state = StorageState(
                deals=self._state.deals,
                balances=self._state.balances,
                balance_events=self._state.balance_events,
                settings=self._state.settings,
                user_roles=self._state.user_roles,
                applications=self._state.applications,
                profiles=self._state.profiles,
                reviews=self._state.reviews,
                disputes=self._state.disputes,
                adverts=self._state.adverts,
                topups=topups,
                chats=self._state.chats,
                deal_sequence=self._state.deal_sequence,
                advert_sequence=self._state.advert_sequence,
                merchant_since=self._state.merchant_since,
                p2p_trading_enabled=self._state.p2p_trading_enabled,
                moderators=self._state.moderators,
                user_warnings=self._state.user_warnings,
                user_bans=self._state.user_bans,
                user_deal_blocks=self._state.user_deal_blocks,
            )
            self._write_locked()

    async def persist_chats(self, chats: Dict[str, List[ChatMessage]]) -> None:
        async with self._lock:
            self._state = StorageState(
                deals=self._state.deals,
                balances=self._state.balances,
                balance_events=self._state.balance_events,
                settings=self._state.settings,
                user_roles=self._state.user_roles,
                applications=self._state.applications,
                profiles=self._state.profiles,
                reviews=self._state.reviews,
                disputes=self._state.disputes,
                adverts=self._state.adverts,
                topups=self._state.topups,
                chats=chats,
                deal_sequence=self._state.deal_sequence,
                advert_sequence=self._state.advert_sequence,
                merchant_since=self._state.merchant_since,
                p2p_trading_enabled=self._state.p2p_trading_enabled,
                moderators=self._state.moderators,
                user_warnings=self._state.user_warnings,
                user_bans=self._state.user_bans,
                user_deal_blocks=self._state.user_deal_blocks,
            )
            self._write_locked()

    def _write_locked(self) -> None:
        payload = {
            "deals": [deal.to_dict() for deal in self._state.deals],
            "balances": {str(uid): str(amount) for uid, amount in self._state.balances.items()},
            "balance_events": [event.to_dict() for event in self._state.balance_events],
            "settings": self._state.settings.to_dict() if self._state.settings else None,
            "user_roles": {str(uid): role for uid, role in self._state.user_roles.items()},
            "applications": [app.to_dict() for app in self._state.applications],
            "profiles": {
                str(uid): profile.to_dict() for uid, profile in self._state.profiles.items()
            },
            "reviews": [review.to_dict() for review in self._state.reviews],
            "disputes": [dispute.to_dict() for dispute in self._state.disputes],
            "adverts": [advert.to_dict() for advert in self._state.adverts],
            "topups": [topup.to_dict() for topup in self._state.topups],
            "chats": {
                deal_id: [msg.to_dict() for msg in messages]
                for deal_id, messages in self._state.chats.items()
            },
            "deal_sequence": self._state.deal_sequence,
            "advert_sequence": self._state.advert_sequence,
            "merchant_since": self._state.merchant_since,
            "p2p_trading_enabled": {
                str(uid): enabled for uid, enabled in self._state.p2p_trading_enabled.items()
            },
            "moderators": list(self._state.moderators),
            "user_warnings": {str(uid): count for uid, count in self._state.user_warnings.items()},
            "user_bans": list(self._state.user_bans),
            "user_deal_blocks": list(self._state.user_deal_blocks),
        }
        tmp = self._path.with_suffix(".tmp")
        tmp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        tmp.replace(self._path)

    def _load(self) -> StorageState:
        if not self._path.exists():
            return StorageState(
                deals=[],
                balances={},
                balance_events=[],
                settings=None,
                user_roles={},
                applications=[],
                profiles={},
                reviews=[],
                disputes=[],
                adverts=[],
                topups=[],
                chats={},
                deal_sequence=0,
                advert_sequence=0,
                merchant_since={},
                p2p_trading_enabled={},
                moderators=[],
                user_warnings={},
                user_bans=[],
                user_deal_blocks=[],
            )
        raw = json.loads(self._path.read_text(encoding="utf-8"))
        deals = [Deal.from_dict(item) for item in raw.get("deals", [])]
        balances = {
            int(uid): Decimal(amount) for uid, amount in (raw.get("balances") or {}).items()
        }
        balance_events = [
            BalanceEvent.from_dict(item) for item in (raw.get("balance_events") or [])
        ]
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
        reviews = [Review.from_dict(item) for item in raw.get("reviews", [])]
        disputes = [Dispute.from_dict(item) for item in raw.get("disputes", [])]
        adverts = [Advert.from_dict(item) for item in raw.get("adverts", [])]
        topups = [Topup.from_dict(item) for item in raw.get("topups", [])]
        chats_raw = raw.get("chats") or {}
        chats = {
            str(deal_id): [ChatMessage.from_dict(item) for item in messages]
            for deal_id, messages in chats_raw.items()
        }
        merchant_since = {
            int(uid): value for uid, value in (raw.get("merchant_since") or {}).items()
        }
        p2p_trading_enabled = {
            int(uid): bool(value) for uid, value in (raw.get("p2p_trading_enabled") or {}).items()
        }
        moderators = [int(uid) for uid in (raw.get("moderators") or [])]
        user_warnings = {
            int(uid): int(count) for uid, count in (raw.get("user_warnings") or {}).items()
        }
        user_bans = [int(uid) for uid in (raw.get("user_bans") or [])]
        user_deal_blocks = [int(uid) for uid in (raw.get("user_deal_blocks") or [])]
        return StorageState(
            deals=deals,
            balances=balances,
            balance_events=balance_events,
            settings=settings,
            user_roles=roles,
            applications=applications,
            profiles=profiles,
            reviews=reviews,
            disputes=disputes,
            adverts=adverts,
            topups=topups,
            chats=chats,
            deal_sequence=int(raw.get("deal_sequence") or 0),
            advert_sequence=int(raw.get("advert_sequence") or 0),
            merchant_since=merchant_since,
            p2p_trading_enabled=p2p_trading_enabled,
            moderators=moderators,
            user_warnings=user_warnings,
            user_bans=user_bans,
            user_deal_blocks=user_deal_blocks,
        )
