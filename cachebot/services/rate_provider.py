from __future__ import annotations

import asyncio
from decimal import Decimal

from cachebot.models.rate import RateSnapshot
from cachebot.storage import RateSettings, StateRepository


class RateProvider:
    def __init__(
        self,
        repository: StateRepository,
        *,
        default_rate: Decimal,
        default_fee_percent: Decimal,
    ) -> None:
        self._repository = repository
        state = repository.snapshot()
        settings = state.settings or RateSettings(default_rate, default_fee_percent)
        self._snapshot = RateSnapshot(settings.usd_rate, settings.fee_percent)
        self._lock = asyncio.Lock()

    async def set_rate(self, usd_rate: Decimal | None = None, fee_percent: Decimal | None = None) -> RateSnapshot:
        async with self._lock:
            rate = usd_rate if usd_rate is not None else self._snapshot.usd_rate
            fee = fee_percent if fee_percent is not None else self._snapshot.fee_percent
            self._snapshot = RateSnapshot(rate, fee)
            await self._repository.persist_settings(RateSettings(rate, fee))
            return self._snapshot

    async def snapshot(self) -> RateSnapshot:
        async with self._lock:
            return RateSnapshot(self._snapshot.usd_rate, self._snapshot.fee_percent)
