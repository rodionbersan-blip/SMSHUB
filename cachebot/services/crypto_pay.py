from __future__ import annotations

import asyncio
from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable, List, Optional
from uuid import uuid4

import httpx


@dataclass(slots=True)
class CryptoInvoice:
    invoice_id: str
    status: str
    amount: Decimal
    currency: str
    pay_url: str


class CryptoPayClient:
    API_BASE = "https://pay.crypt.bot/api/"

    def __init__(self, token: str | None) -> None:
        self._token = token
        self._client: Optional[httpx.AsyncClient] = None
        self._dry_run = token is None
        self._lock = asyncio.Lock()

    async def _client_instance(self) -> httpx.AsyncClient:
        async with self._lock:
            if not self._client:
                headers = {"Content-Type": "application/json"}
                if self._token:
                    headers["Crypto-Pay-API-Token"] = self._token
                self._client = httpx.AsyncClient(base_url=self.API_BASE, headers=headers, timeout=20.0)
            return self._client

    async def close(self) -> None:
        async with self._lock:
            if self._client:
                await self._client.aclose()
                self._client = None

    async def create_invoice(
        self,
        *,
        amount: Decimal,
        currency: str,
        description: str,
        payload: str,
    ) -> CryptoInvoice:
        if self._dry_run:
            return CryptoInvoice(
                invoice_id=f"dry-{uuid4().hex}",
                status="active",
                amount=amount,
                currency=currency,
                pay_url="https://t.me/CryptoBot?start=dry",
            )
        client = await self._client_instance()
        response = await client.post(
            "createInvoice",
            json={
                "amount": str(amount),
                "currency_type": "crypto",
                "asset": currency,
                "description": description,
                "payload": payload,
            },
        )
        data = response.json()
        if not data.get("ok"):
            raise RuntimeError(f"Crypto Pay error: {data}")
        result = data["result"]
        return CryptoInvoice(
            invoice_id=str(result["invoice_id"]),
            status=result["status"],
            amount=Decimal(result["amount"]),
            currency=result["asset"] if result.get("asset") else result.get("currency"),
            pay_url=result["pay_url"],
        )

    async def fetch_invoices(self, invoice_ids: Iterable[str]) -> List[CryptoInvoice]:
        ids = [invoice_id for invoice_id in invoice_ids if invoice_id]
        if not ids:
            return []
        if self._dry_run:
            return []
        client = await self._client_instance()
        response = await client.post(
            "getInvoices",
            json={"invoice_ids": ",".join(ids)},
        )
        data = response.json()
        if not data.get("ok"):
            raise RuntimeError(f"Crypto Pay error: {data}")
        result = data.get("result") or []
        if isinstance(result, dict):
            items = result.get("items", [])
        else:
            items = result
        invoices: List[CryptoInvoice] = []
        for item in items:
            invoices.append(
                CryptoInvoice(
                    invoice_id=str(item["invoice_id"]),
                    status=item["status"],
                    amount=Decimal(item["amount"]),
                    currency=item.get("asset") or item.get("currency", "USDT"),
                    pay_url=item["pay_url"],
                )
            )
        return invoices
