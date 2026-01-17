from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Dict, List, Optional
from uuid import uuid4

from cachebot.models.deal import Deal, DealStatus, QrStage
from cachebot.services.rate_provider import RateProvider
from cachebot.storage import StateRepository


class DealService:
    def __init__(
        self,
        repository: StateRepository,
        rate_provider: RateProvider,
        payment_window_minutes: int,
        offer_window_minutes: int | None = None,
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
        self._offer_window = timedelta(
            minutes=offer_window_minutes if offer_window_minutes is not None else payment_window_minutes
        )
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
            expires_at = now
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
            deal.dispute_available_at = None
            deal.dispute_notified = False
            self._deals[deal.id] = deal
            self._reset_qr_locked(deal)
            await self._persist()
        return deal

    async def create_p2p_deal(
        self,
        *,
        seller_id: int,
        buyer_id: int,
        usd_amount: Decimal,
        rate: Decimal,
        advert_id: str | None = None,
        comment: str | None = None,
    ) -> Deal:
        if usd_amount <= Decimal("0"):
            raise ValueError("Amount must be greater than zero")
        if rate <= Decimal("0"):
            raise ValueError("Rate must be greater than zero")
        rate_snapshot = await self._rate_provider.snapshot()
        fee_multiplier = rate_snapshot.fee_multiplier
        base_usdt = usd_amount / rate
        fee = base_usdt * fee_multiplier
        total_usdt = base_usdt + fee
        async with self._lock:
            current = self._balances.get(seller_id, Decimal("0"))
            if current < base_usdt:
                raise ValueError("Недостаточно баланса")
            self._balances[seller_id] = current - base_usdt
            now = datetime.now(timezone.utc)
            deal = Deal(
                id=str(uuid4()),
                seller_id=seller_id,
                usd_amount=usd_amount,
                rate=rate,
                fee_percent=rate_snapshot.fee_percent,
                fee_amount=fee,
                usdt_amount=total_usdt,
                created_at=now,
                expires_at=now,
                status=DealStatus.RESERVED,
                buyer_id=buyer_id,
                comment=comment,
                public_id=self._next_public_id_locked(),
                is_p2p=True,
                advert_id=advert_id,
            )
            deal.dispute_available_at = None
            deal.dispute_notified = False
            self._deals[deal.id] = deal
            self._reset_qr_locked(deal)
            await self._persist()
        return deal

    async def create_p2p_offer(
        self,
        *,
        seller_id: int,
        buyer_id: int,
        initiator_id: int,
        usd_amount: Decimal,
        rate: Decimal,
        advert_id: str | None = None,
        comment: str | None = None,
    ) -> Deal:
        if usd_amount <= Decimal("0"):
            raise ValueError("Amount must be greater than zero")
        if rate <= Decimal("0"):
            raise ValueError("Rate must be greater than zero")
        rate_snapshot = await self._rate_provider.snapshot()
        fee_multiplier = rate_snapshot.fee_multiplier
        base_usdt = usd_amount / rate
        fee = base_usdt * fee_multiplier
        total_usdt = base_usdt + fee
        async with self._lock:
            current = self._balances.get(seller_id, Decimal("0"))
            if current < base_usdt:
                raise ValueError("Недостаточно баланса")
            self._balances[seller_id] = current - base_usdt
            now = datetime.now(timezone.utc)
            expires_at = now + self._offer_window
            deal = Deal(
                id=str(uuid4()),
                seller_id=seller_id,
                usd_amount=usd_amount,
                rate=rate,
                fee_percent=rate_snapshot.fee_percent,
                fee_amount=fee,
                usdt_amount=total_usdt,
                created_at=now,
                expires_at=expires_at,
                status=DealStatus.PENDING,
                buyer_id=buyer_id,
                offer_initiator_id=initiator_id,
                offer_expires_at=expires_at,
                comment=comment,
                public_id=self._next_public_id_locked(),
                is_p2p=True,
                advert_id=advert_id,
            )
            deal.dispute_available_at = None
            deal.dispute_notified = False
            self._deals[deal.id] = deal
            self._reset_qr_locked(deal)
            await self._persist()
        return deal

    async def accept_p2p_offer(self, deal_id: str, actor_id: int) -> Deal:
        async with self._lock:
            deal = self._ensure_deal(deal_id)
            if deal.status != DealStatus.PENDING:
                raise ValueError("Предложение уже обработано")
            if deal.offer_initiator_id == actor_id:
                raise PermissionError("Нельзя принять собственное предложение")
            if actor_id not in {deal.seller_id, deal.buyer_id} and not self._is_admin(actor_id):
                raise PermissionError("Нет доступа")
            now = datetime.now(timezone.utc)
            if deal.offer_expires_at and deal.offer_expires_at <= now:
                raise ValueError("Предложение истекло")
            deal.status = DealStatus.PAID
            deal.offer_expires_at = None
            deal.expires_at = now
            deal.invoice_id = None
            deal.invoice_url = None
            deal.dispute_available_at = now + self._payment_window
            deal.dispute_notified = False
            self._reset_qr_locked(deal)
            self._deals[deal.id] = deal
            await self._persist()
            return deal

    async def decline_p2p_offer(
        self,
        deal_id: str,
        actor_id: int,
        *,
        expired: bool = False,
    ) -> tuple[Deal, Decimal]:
        async with self._lock:
            deal = self._ensure_deal(deal_id)
            if deal.status != DealStatus.PENDING:
                raise ValueError("Предложение уже обработано")
            if actor_id not in {deal.seller_id, deal.buyer_id} and not self._is_admin(actor_id):
                raise PermissionError("Нет доступа")
            base_usdt = deal.usd_amount / deal.rate
            if base_usdt > 0:
                self._credit_balance_locked(deal.seller_id, base_usdt)
            deal.status = DealStatus.EXPIRED if expired else DealStatus.CANCELED
            deal.offer_expires_at = None
            deal.invoice_id = None
            deal.invoice_url = None
            self._reset_qr_locked(deal)
            self._deals[deal.id] = deal
            await self._persist()
            return deal, base_usdt

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

    async def get_deal_by_token(self, token: str) -> Deal | None:
        async with self._lock:
            try:
                return self._ensure_deal(token)
            except LookupError:
                return None

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
            deal.expires_at = now
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
            self._reset_qr_locked(deal)
            deal.expires_at = datetime.now(timezone.utc)
            deal.dispute_available_at = None
            deal.dispute_notified = False
            deal.dispute_opened_by = None
            deal.dispute_opened_at = None
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
            deal.invoice_url = None
            deal.dispute_available_at = datetime.now(timezone.utc) + self._payment_window
            deal.dispute_notified = False
            self._reset_qr_locked(deal)
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
            deal.invoice_url = None
            deal.dispute_available_at = datetime.now(timezone.utc) + self._payment_window
            deal.dispute_notified = False
            self._reset_qr_locked(deal)
            self._deals[deal.id] = deal
            await self._persist()
            return deal

    async def complete_deal(self, deal_id: str, actor_id: int) -> tuple[Deal, bool]:
        async with self._lock:
            deal = self._ensure_deal(deal_id)
            if actor_id not in (deal.seller_id, deal.buyer_id) and not self._is_admin(actor_id):
                raise PermissionError("Not allowed to complete this deal")
            if deal.status not in {DealStatus.PAID, DealStatus.RESERVED}:
                raise ValueError("Deal is not ready for completion")
            deal.buyer_cash_confirmed = True
            deal.seller_cash_confirmed = True
            payout = self._finalize_cash_locked(deal)
            self._deals[deal.id] = deal
            await self._persist()
            return deal, payout

    async def cancel_deal(self, deal_id: str, actor_id: int) -> tuple[Deal, Decimal | None]:
        async with self._lock:
            deal = self._ensure_deal(deal_id)
            if deal.status == DealStatus.PENDING:
                if actor_id not in {deal.seller_id, deal.buyer_id} and not self._is_admin(actor_id):
                    raise PermissionError("Not allowed to cancel")
                base_usdt = deal.usd_amount / deal.rate
                if base_usdt > 0:
                    self._credit_balance_locked(deal.seller_id, base_usdt)
                deal.status = DealStatus.CANCELED
                deal.offer_expires_at = None
                deal.invoice_id = None
                deal.invoice_url = None
                self._reset_qr_locked(deal)
                self._deals[deal.id] = deal
                await self._persist()
                return deal, base_usdt
            if not self._can_cancel(deal, actor_id):
                raise PermissionError("Not allowed to cancel")
            if deal.status in {DealStatus.CANCELED, DealStatus.COMPLETED, DealStatus.DISPUTE}:
                return deal, None
            was_paid = deal.status == DealStatus.PAID
            refund_amount: Decimal | None = None
            is_seller = actor_id == deal.seller_id
            if is_seller and was_paid:
                refund_amount = max(Decimal("0"), deal.usdt_amount - deal.fee_amount)
                self._credit_balance_locked(actor_id, refund_amount)
            if deal.is_p2p and not was_paid:
                base_usdt = deal.usd_amount / deal.rate
                if base_usdt > 0:
                    self._credit_balance_locked(deal.seller_id, base_usdt)
            deal.status = DealStatus.CANCELED
            if not was_paid:
                deal.buyer_id = None
            deal.invoice_id = None
            deal.invoice_url = None
            self._reset_qr_locked(deal)
            self._deals[deal.id] = deal
            await self._persist()
            return deal, refund_amount

    async def cleanup_expired(self) -> List[Deal]:
        now = datetime.now(timezone.utc)
        expired: List[Deal] = []
        async with self._lock:
            for deal in list(self._deals.values()):
                if deal.status != DealStatus.PENDING:
                    continue
                expires_at = deal.offer_expires_at or deal.expires_at
                if not expires_at or expires_at > now:
                    continue
                base_usdt = deal.usd_amount / deal.rate
                if base_usdt > 0:
                    self._credit_balance_locked(deal.seller_id, base_usdt)
                deal.status = DealStatus.EXPIRED
                deal.offer_expires_at = None
                deal.invoice_id = None
                deal.invoice_url = None
                self._reset_qr_locked(deal)
                self._deals[deal.id] = deal
                expired.append(deal)
            if expired:
                await self._persist()
        return expired

    async def list_dispute_ready(self) -> List[Deal]:
        now = datetime.now(timezone.utc)
        async with self._lock:
            return [
                deal
                for deal in self._deals.values()
                if deal.status == DealStatus.PAID
                and deal.dispute_available_at
                and deal.dispute_available_at <= now
                and not deal.dispute_notified
            ]

    async def mark_dispute_notified(self, deal_id: str) -> None:
        async with self._lock:
            deal = self._ensure_deal(deal_id)
            deal.dispute_notified = True
            self._deals[deal.id] = deal
            await self._persist()

    async def open_dispute(self, deal_id: str, opener_id: int) -> Deal:
        async with self._lock:
            deal = self._ensure_deal(deal_id)
            if deal.status != DealStatus.PAID:
                raise ValueError("Спор можно открыть только после оплаты")
            deal.status = DealStatus.DISPUTE
            deal.dispute_opened_by = opener_id
            deal.dispute_opened_at = datetime.now(timezone.utc)
            self._deals[deal.id] = deal
            await self._persist()
            return deal

    async def resolve_dispute(
        self,
        deal_id: str,
        *,
        seller_amount: Decimal,
        buyer_amount: Decimal,
    ) -> Deal:
        async with self._lock:
            deal = self._ensure_deal(deal_id)
            if deal.status != DealStatus.DISPUTE:
                if deal.dispute_opened_by is None:
                    raise ValueError("Спор не открыт")
                if deal.payout_completed:
                    raise ValueError("Сделка уже завершена")
                deal.status = DealStatus.DISPUTE
            total = seller_amount + buyer_amount
            if seller_amount < 0 or buyer_amount < 0:
                raise ValueError("Сумма не может быть отрицательной")
            if total > deal.usdt_amount:
                raise ValueError("Сумма превышает объем сделки")
            if seller_amount > 0:
                self._credit_balance_locked(deal.seller_id, seller_amount)
            if deal.buyer_id and buyer_amount > 0:
                self._credit_balance_locked(deal.buyer_id, buyer_amount)
            deal.status = DealStatus.COMPLETED
            deal.buyer_cash_confirmed = True
            deal.seller_cash_confirmed = True
            deal.payout_completed = True
            self._deals[deal.id] = deal
            await self._persist()
            return deal

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

    async def reserved_of(self, user_id: int) -> Decimal:
        async with self._lock:
            reserved = Decimal("0")
            for deal in self._deals.values():
                if deal.seller_id != user_id or not deal.is_p2p:
                    continue
                if deal.status in {
                    DealStatus.PENDING,
                    DealStatus.RESERVED,
                    DealStatus.PAID,
                    DealStatus.DISPUTE,
                }:
                    reserved += deal.usd_amount / deal.rate
            return reserved

    def _credit_balance_locked(self, user_id: int, amount: Decimal) -> None:
        self._balances[user_id] = self._balances.get(user_id, Decimal("0")) + amount

    def _finalize_cash_locked(self, deal: Deal) -> bool:
        if (
            deal.status in {DealStatus.PAID, DealStatus.RESERVED}
            and deal.seller_cash_confirmed
            and not deal.payout_completed
        ):
            deal.status = DealStatus.COMPLETED
            if deal.buyer_id:
                self._credit_balance_locked(deal.buyer_id, deal.usdt_amount)
            deal.payout_completed = True
            return True
        return False

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

    def _can_cancel(self, deal: Deal, actor_id: int) -> bool:
        if actor_id == deal.buyer_id:
            return True
        if actor_id == deal.seller_id and deal.status in {
            DealStatus.OPEN,
            DealStatus.RESERVED,
            DealStatus.PAID,
        }:
            return True
        return self._is_admin(actor_id)

    def _find_deal_by_invoice(self, invoice_id: str) -> Deal:
        for deal in self._deals.values():
            if deal.invoice_id == invoice_id:
                return deal
        raise LookupError("Invoice is not attached to any deal")

    async def start_qr_request(self, deal_id: str, buyer_id: int, banks: list[str]) -> Deal:
        async with self._lock:
            deal = self._ensure_deal(deal_id)
            if deal.buyer_id != buyer_id:
                raise PermissionError("Нет доступа к сделке")
            if deal.status != DealStatus.PAID:
                raise ValueError("QR можно запросить только после оплаты")
            if deal.qr_stage not in {QrStage.IDLE, QrStage.READY}:
                raise ValueError("Запрос уже в работе")
            if not banks:
                raise ValueError("Нужно выбрать хотя бы один банк")
            deal.qr_bank_options = list(banks)
            deal.atm_bank = None
            deal.qr_stage = QrStage.AWAITING_SELLER_BANK
            deal.qr_photo_id = None
            self._deals[deal.id] = deal
            await self._persist()
            return deal

    async def seller_choose_qr_bank(self, deal_id: str, seller_id: int, bank: str) -> Deal:
        async with self._lock:
            deal = self._ensure_deal(deal_id)
            if deal.seller_id != seller_id:
                raise PermissionError("Нет доступа к сделке")
            if deal.qr_stage != QrStage.AWAITING_SELLER_BANK:
                raise ValueError("Сейчас не требуется выбор банкомата")
            if bank not in deal.qr_bank_options:
                raise ValueError("Такой банк не запрашивали")
            deal.atm_bank = bank
            deal.qr_stage = QrStage.AWAITING_SELLER_ATTACH
            self._deals[deal.id] = deal
            await self._persist()
            return deal

    async def seller_request_qr(self, deal_id: str, seller_id: int) -> Deal:
        async with self._lock:
            deal = self._ensure_deal(deal_id)
            if deal.seller_id != seller_id:
                raise PermissionError("Нет доступа к сделке")
            if deal.qr_stage not in {QrStage.AWAITING_SELLER_ATTACH, QrStage.AWAITING_BUYER_READY}:
                raise ValueError("Сейчас нельзя отправить QR")
            deal.qr_stage = QrStage.AWAITING_BUYER_READY
            self._deals[deal.id] = deal
            await self._persist()
            return deal

    async def buyer_ready_for_qr(self, deal_id: str, buyer_id: int) -> Deal:
        async with self._lock:
            deal = self._ensure_deal(deal_id)
            if deal.buyer_id != buyer_id:
                raise PermissionError("Нет доступа к сделке")
            if deal.qr_stage != QrStage.AWAITING_BUYER_READY:
                raise ValueError("Пока не требуется подтверждение")
            deal.qr_stage = QrStage.AWAITING_SELLER_PHOTO
            self._deals[deal.id] = deal
            await self._persist()
            return deal

    async def attach_qr_photo(self, deal_id: str, seller_id: int, file_id: str) -> Deal:
        async with self._lock:
            deal = self._ensure_deal(deal_id)
            if deal.seller_id != seller_id:
                raise PermissionError("Нет доступа к сделке")
            if deal.qr_stage not in {QrStage.AWAITING_SELLER_PHOTO, QrStage.READY}:
                raise ValueError("Сейчас не требуется отправлять QR")
            deal.qr_photo_id = file_id
            deal.qr_stage = QrStage.READY
            self._deals[deal.id] = deal
            await self._persist()
            return deal

    async def confirm_buyer_cash(self, deal_id: str, buyer_id: int) -> tuple[Deal, bool]:
        async with self._lock:
            deal = self._ensure_deal(deal_id)
            if deal.buyer_id != buyer_id:
                raise PermissionError("Нет доступа к сделке")
            if deal.status not in {DealStatus.PAID, DealStatus.COMPLETED}:
                raise ValueError("Сделка еще не оплачена")
            if deal.status == DealStatus.DISPUTE:
                raise ValueError("По сделке открыт спор")
            deal.buyer_cash_confirmed = True
            payout = self._finalize_cash_locked(deal)
            self._deals[deal.id] = deal
            await self._persist()
            return deal, payout

    async def confirm_seller_cash(self, deal_id: str, seller_id: int) -> tuple[Deal, bool]:
        async with self._lock:
            deal = self._ensure_deal(deal_id)
            if deal.seller_id != seller_id:
                raise PermissionError("Нет доступа к сделке")
            if deal.status not in {DealStatus.PAID, DealStatus.COMPLETED}:
                raise ValueError("Сделка еще не оплачена")
            if deal.status == DealStatus.DISPUTE:
                raise ValueError("По сделке открыт спор")
            deal.seller_cash_confirmed = True
            payout = self._finalize_cash_locked(deal)
            self._deals[deal.id] = deal
            await self._persist()
            return deal, payout

    async def withdraw_balance(self, user_id: int, amount: Decimal) -> Decimal:
        if amount <= 0:
            raise ValueError("Сумма должна быть больше нуля")
        async with self._lock:
            current = self._balances.get(user_id, Decimal("0"))
            if current < amount:
                raise ValueError("Недостаточно средств")
            self._balances[user_id] = current - amount
            await self._persist()
            return self._balances[user_id]

    async def deposit_balance(self, user_id: int, amount: Decimal) -> Decimal:
        if amount <= 0:
            raise ValueError("Сумма должна быть больше нуля")
        async with self._lock:
            self._credit_balance_locked(user_id, amount)
            await self._persist()
            return self._balances[user_id]

    def _reset_qr_locked(self, deal: Deal) -> None:
        deal.qr_stage = QrStage.IDLE
        deal.qr_bank_options = []
        deal.atm_bank = None
        deal.qr_photo_id = None
        deal.buyer_cash_confirmed = False
        deal.seller_cash_confirmed = False
        if deal.status != DealStatus.COMPLETED:
            deal.payout_completed = False

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
