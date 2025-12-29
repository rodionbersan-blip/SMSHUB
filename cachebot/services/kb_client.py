from __future__ import annotations

import logging
from decimal import Decimal
from typing import Optional

import httpx


logger = logging.getLogger(__name__)


class KBClient:
    def __init__(self, base_url: str | None, token: str | None) -> None:
        self._base_url = base_url.rstrip("/") if base_url else None
        self._token = token

    async def credit_balance(self, user_id: int, amount: Decimal) -> bool:
        if not self._base_url or not self._token:
            logger.info("KB client is not configured; skipping credit for user %s", user_id)
            return False
        async with httpx.AsyncClient(base_url=self._base_url, headers={"Authorization": f"Bearer {self._token}"}, timeout=15.0) as client:
            response = await client.post(
                "/balances/credit",
                json={"user_id": user_id, "amount": str(amount)},
            )
            if response.status_code >= 400:
                logger.error("KB credit failed (%s): %s", response.status_code, response.text)
                return False
        return True
