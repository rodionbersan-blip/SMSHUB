from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Dict, List, Optional
from uuid import uuid4

from cachebot.models.deal import Deal, DealStatus
from cachebot.services.rate_provider import RateProvider
from cachebot.storage import StateRepository


class DealService:
    def __init__(
        self,
        repository: StateRepository,
        rate_provider: RateProvider,
        payment_window_minutes: int,
        *,
        admin_ids: set[int] | None = None,
    ) -> None:
        self._repository = repository
        self._rate_provider = rate_provider
        self._lock = asyncio.Lock()
        snapshot = repository.snapshot()
        self._deals: Dict[str, Deal] = {deal.id: deal for deal in snapshot.deals}
        self._balances: Dict[int, Decimal] = snapshot.balances.copy()
        self._payment_window = timedelta(minutes=payment_window_minutes)
        self._admin_ids = admin_ids or set()
        self._deal_seq = snapshot.deal_sequence or len(self._deals)

    async def create_deal(self, seller_id: int, usd_amount: Decimal, comment: str | None = None) -> Deal:
        if usd_amount <= Decimal("0"):
            raise ValueError("Amount must be greater than zero")
        rate_snapshot = await self._rate_provider.snapshot()
        fee_multiplier = rate_snapshot.fee_multiplier
        base_usdt = usd_amount / rate_snapshot.usd_rate
        fee = base_usdt * fee_multiplier
        total_usdt = base_usdt + fee
        async with self._lock:
            now = datetime.now(timezone.utc)
            expires_at = now + self._payment_window
            deal = Deal(
                id=str(uuid4()),
                seller_id=seller_id,
                usd_amount=usd_amount,
                rate=rate_snapshot.usd_rate,
                fee_percent=rate_snapshot.fee_percent,
                fee_amount=fee,
                usdt_amount=total_usdt,
                created_at=now,
                expires_at=expires_at,
                comment=comment,
                public_id=self._next_public_id_locked(),
            )
            self._deals[deal.id] = deal
            await self._persist()
        return deal

    async def list_open_deals(self) -> List[Deal]:
        async with self._lock:
            return sorted(
                (deal for deal in self._deals.values() if deal.status == DealStatus.OPEN),
                key=lambda deal: deal.created_at,
            )

    async def list_user_deals(self, user_id: int) -> List[Deal]:
        async with self._lock:
            return sorted(
                (
                    deal
                    for deal in self._deals.values()
                    if deal.seller_id == user_id or deal.buyer_id == user_id
                ),
                key=lambda deal: deal.created_at,
                reverse=True,
            )

    async def get_deal(self, deal_id: str) -> Deal | None:
        async with self._lock:
            return self._deals.get(deal_id)

    async def accept_deal(self, deal_id: str, buyer_id: int) -> Deal:
        async with self._lock:
            deal = self._deals.get(deal_id)
            if not deal:
                raise LookupError("Deal not found")
            if deal.status != DealStatus.OPEN:
                raise ValueError("Deal is not available for accepting")
            if deal.seller_id == buyer_id and not self._is_admin(buyer_id):
                raise ValueError("Seller cannot accept own deal")
            now = datetime.now(timezone.utc)
            deal.buyer_id = buyer_id
            deal.status = DealStatus.RESERVED
            deal.expires_at = now + self._payment_window
            self._deals[deal.id] = deal
            await self._persist()
            return deal

    async def release_deal(self, deal_id: str) -> Deal:
        async with self._lock:
            deal = self._ensure_deal(deal_id)
            deal.buyer_id = None
            deal.invoice_id = None
            deal.invoice_url = None
            deal.status = DealStatus.OPEN
            deal.expires_at = datetime.now(timezone.utc) + self._payment_window
            self._deals[deal.id] = deal
            await self._persist()
            return deal

    async def attach_invoice(self, deal_id: str, invoice_id: str, invoice_url: str) -> Deal:
        async with self._lock:
            deal = self._ensure_deal(deal_id)
            deal.invoice_id = invoice_id
            deal.invoice_url = invoice_url
            self._deals[deal.id] = deal
            await self._persist()
            return deal

    async def mark_invoice_paid(self, invoice_id: str) -> Deal:
        async with self._lock:
            deal = self._find_deal_by_invoice(invoice_id)
            if deal.status in {DealStatus.PAID, DealStatus.COMPLETED}:
                return deal
            deal.status = DealStatus.PAID
            self._credit_balance_locked(deal.seller_id, deal.usd_amount)
            self._deals[deal.id] = deal
            await self._persist()
            return deal

    async def mark_paid_manual(self, deal_id: str) -> Deal:
        async with self._lock:
            deal = self._ensure_deal(deal_id)
            if not deal.invoice_id:
                raise ValueError("Сделка не имеет счета Crypto Pay")
            if deal.status in {DealStatus.PAID, DealStatus.COMPLETED}:
                return deal
            deal.status = DealStatus.PAID
            self._credit_balance_locked(deal.seller_id, deal.usd_amount)
            self._deals[deal.id] = deal
            await self._persist()
            return deal

    async def complete_deal(self, deal_id: str, actor_id: int) -> Deal:
        async with self._lock:
            deal = self._ensure_deal(deal_id)
            if actor_id not in (deal.seller_id, deal.buyer_id) and not self._is_admin(actor_id):
                raise PermissionError("Not allowed to complete this deal")
            if deal.status not in {DealStatus.PAID, DealStatus.RESERVED}:
                raise ValueError("Deal is not ready for completion")
            deal.status = DealStatus.COMPLETED
            self._deals[deal.id] = deal
            await self._persist()
            return deal

    async def cancel_deal(self, deal_id: str, actor_id: int) -> Deal:
        async with self._lock:
            deal = self._ensure_deal(deal_id)
            if actor_id not in (deal.seller_id, deal.buyer_id) and not self._is_admin(actor_id):
                raise PermissionError("Not allowed to cancel")
            if deal.status in {DealStatus.CANCELED, DealStatus.COMPLETED}:
                return deal
            deal.status = DealStatus.CANCELED
            deal.buyer_id = None
            deal.invoice_id = None
            deal.invoice_url = None
            self._deals[deal.id] = deal
            await self._persist()
            return deal

    async def cleanup_expired(self) -> List[Deal]:
        now = datetime.now(timezone.utc)
        expired: List[Deal] = []
        async with self._lock:
            for deal in self._deals.values():
                if deal.status in {DealStatus.OPEN, DealStatus.RESERVED} and deal.expires_at <= now:
                    previous_status = deal.status
                    deal.status = DealStatus.EXPIRED
                    if previous_status == DealStatus.RESERVED:
                        deal.buyer_id = None
                        deal.invoice_id = None
                        deal.invoice_url = None
                    expired.append(deal)
            if expired:
                await self._persist()
        return expired

    async def reserved_deals_with_invoices(self) -> List[Deal]:
        async with self._lock:
            return [
                deal
                for deal in self._deals.values()
                if deal.status == DealStatus.RESERVED and deal.invoice_id
            ]

    async def balance_of(self, user_id: int) -> Decimal:
        async with self._lock:
            return self._balances.get(user_id, Decimal("0"))

    async def balances(self) -> Dict[int, Decimal]:
        async with self._lock:
            return self._balances.copy()

    def _credit_balance_locked(self, user_id: int, amount: Decimal) -> None:
        self._balances[user_id] = self._balances.get(user_id, Decimal("0")) + amount

    def _ensure_deal(self, deal_token: str) -> Deal:
        deal = self._deals.get(deal_token)
        if not deal:
            match_token = deal_token.upper()
            for candidate in self._deals.values():
                if candidate.public_id.upper() == match_token:
                    deal = candidate
                    break
        if not deal:
            raise LookupError("Deal not found")
        return deal

    def _find_deal_by_invoice(self, invoice_id: str) -> Deal:
        for deal in self._deals.values():
            if deal.invoice_id == invoice_id:
                return deal
        raise LookupError("Invoice is not attached to any deal")

    async def _persist(self) -> None:
        await self._repository.persist_deals_and_balances(
            list(self._deals.values()),
            self._balances,
            deal_sequence=self._deal_seq,
        )

    def _is_admin(self, actor_id: int) -> bool:
        return actor_id in self._admin_ids

    def _next_public_id_locked(self) -> str:
        self._deal_seq += 1
        return f"C{self._deal_seq:05d}"
