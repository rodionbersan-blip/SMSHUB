from __future__ import annotations

import asyncio
from dataclasses import replace
from datetime import datetime, timezone
from decimal import Decimal
from typing import Dict, List
from uuid import uuid4

from cachebot.models.advert import Advert, AdvertSide
from cachebot.storage import StateRepository


class AdvertService:
    def __init__(self, repository: StateRepository) -> None:
        self._repository = repository
        self._lock = asyncio.Lock()
        snapshot = repository.snapshot()
        self._adverts: Dict[str, Advert] = {item.id: item for item in snapshot.adverts}
        self._advert_seq = snapshot.advert_sequence or len(self._adverts)
        self._trading_enabled: Dict[int, bool] = snapshot.p2p_trading_enabled.copy()

    async def list_user_ads(self, user_id: int) -> List[Advert]:
        async with self._lock:
            return sorted(
                (ad for ad in self._adverts.values() if ad.owner_id == user_id),
                key=lambda ad: ad.created_at,
                reverse=True,
            )

    async def list_public_ads(self, side: AdvertSide, *, exclude_user_id: int | None = None) -> List[Advert]:
        async with self._lock:
            result = []
            for ad in self._adverts.values():
                if ad.side != side or not ad.active:
                    continue
                if ad.remaining_usdt <= Decimal("0"):
                    continue
                if not self._trading_enabled.get(ad.owner_id, True):
                    continue
                if exclude_user_id is not None and ad.owner_id == exclude_user_id:
                    continue
                result.append(ad)
            return sorted(result, key=lambda ad: ad.created_at, reverse=True)

    async def get_ad(self, advert_id: str) -> Advert | None:
        async with self._lock:
            return self._adverts.get(advert_id)

    async def create_ad(
        self,
        owner_id: int,
        side: AdvertSide,
        total_usdt: Decimal,
        price_rub: Decimal,
        min_rub: Decimal,
        max_rub: Decimal,
        banks: List[str],
        terms: str | None,
    ) -> Advert:
        if total_usdt <= Decimal("0"):
            raise ValueError("Объём должен быть больше нуля")
        if price_rub <= Decimal("0"):
            raise ValueError("Цена должна быть больше нуля")
        if min_rub <= Decimal("0") or max_rub <= Decimal("0") or min_rub > max_rub:
            raise ValueError("Некорректные лимиты")
        async with self._lock:
            ad = Advert(
                id=str(uuid4()),
                owner_id=owner_id,
                side=side,
                price_rub=price_rub,
                total_usdt=total_usdt,
                remaining_usdt=total_usdt,
                min_rub=min_rub,
                max_rub=max_rub,
                banks=list(banks),
                terms=terms,
                active=False,
                created_at=datetime.now(timezone.utc),
                public_id=self._next_public_id_locked(),
            )
            self._adverts[ad.id] = ad
            await self._persist_locked()
            return ad

    async def update_ad(self, advert_id: str, **changes) -> Advert:
        async with self._lock:
            ad = self._adverts.get(advert_id)
            if not ad:
                raise LookupError("Объявление не найдено")
            updated = replace(ad, **changes)
            self._adverts[ad.id] = updated
            await self._persist_locked()
            return updated

    async def toggle_active(self, advert_id: str, active: bool) -> Advert:
        return await self.update_ad(advert_id, active=active)

    async def set_trading(self, user_id: int, enabled: bool) -> None:
        async with self._lock:
            self._trading_enabled[user_id] = enabled
            await self._persist_locked()

    async def trading_enabled(self, user_id: int) -> bool:
        async with self._lock:
            return self._trading_enabled.get(user_id, True)

    async def reduce_volume(self, advert_id: str, usdt_amount: Decimal) -> Advert:
        if usdt_amount <= Decimal("0"):
            raise ValueError("Некорректный объём")
        async with self._lock:
            ad = self._adverts.get(advert_id)
            if not ad:
                raise LookupError("Объявление не найдено")
            if ad.remaining_usdt < usdt_amount:
                raise ValueError("Недостаточно объёма в объявлении")
            updated = replace(ad, remaining_usdt=ad.remaining_usdt - usdt_amount)
            self._adverts[ad.id] = updated
            await self._persist_locked()
            return updated

    async def restore_volume(self, advert_id: str, usdt_amount: Decimal) -> Advert:
        if usdt_amount <= Decimal("0"):
            raise ValueError("Некорректный объём")
        async with self._lock:
            ad = self._adverts.get(advert_id)
            if not ad:
                raise LookupError("Объявление не найдено")
            updated = replace(ad, remaining_usdt=ad.remaining_usdt + usdt_amount)
            self._adverts[ad.id] = updated
            await self._persist_locked()
            return updated

    async def delete_ad(self, advert_id: str) -> None:
        async with self._lock:
            self._adverts.pop(advert_id, None)
            await self._persist_locked()

    async def counts_for_user(self, user_id: int) -> tuple[int, int]:
        async with self._lock:
            ads = [ad for ad in self._adverts.values() if ad.owner_id == user_id]
            active = sum(1 for ad in ads if ad.active)
            return active, len(ads)

    async def disable_user_ads(self, user_id: int) -> int:
        async with self._lock:
            updated = 0
            for ad in list(self._adverts.values()):
                if ad.owner_id != user_id or not ad.active:
                    continue
                self._adverts[ad.id] = replace(ad, active=False)
                updated += 1
            if updated:
                await self._persist_locked()
            return updated

    async def _persist_locked(self) -> None:
        await self._repository.persist_adverts(
            list(self._adverts.values()),
            advert_sequence=self._advert_seq,
            p2p_trading_enabled=self._trading_enabled,
        )

    def _next_public_id_locked(self) -> str:
        self._advert_seq += 1
        return f"O{self._advert_seq:07d}"
