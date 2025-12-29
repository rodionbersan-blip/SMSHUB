from __future__ import annotations

import asyncio
import logging
from typing import Optional

from aiogram import Bot

from cachebot.models.deal import Deal, DealStatus
from cachebot.services.crypto_pay import CryptoPayClient
from cachebot.services.deals import DealService
from cachebot.services.kb_client import KBClient

logger = logging.getLogger(__name__)


async def expiry_watcher(deal_service: DealService, bot: Bot, interval: int = 30) -> None:
    while True:
        try:
            expired = await deal_service.cleanup_expired()
            for deal in expired:
                text = f"❗️ Сделка {deal.public_id} истекла"
                await bot.send_message(deal.seller_id, text)
                if deal.buyer_id:
                    await bot.send_message(deal.buyer_id, text)
        except Exception as exc:  # pragma: no cover - protection loop
            logger.exception("Expiry watcher error: %s", exc)
        await asyncio.sleep(interval)


async def invoice_watcher(
    deal_service: DealService,
    crypto_client: CryptoPayClient,
    kb_client: KBClient,
    bot: Bot,
    interval: int,
) -> None:
    while True:
        try:
            deals = await deal_service.reserved_deals_with_invoices()
            invoices = await crypto_client.fetch_invoices([deal.invoice_id for deal in deals])
            paid_ids = {invoice.invoice_id for invoice in invoices if invoice.status == "paid"}
            for invoice_id in paid_ids:
                deal = await deal_service.mark_invoice_paid(invoice_id)
                await handle_paid_invoice(deal, kb_client, bot)
        except Exception as exc:  # pragma: no cover
            logger.exception("Invoice watcher error: %s", exc)
        await asyncio.sleep(interval)


async def handle_paid_invoice(deal: Deal, kb_client: KBClient, bot: Bot) -> None:
    await kb_client.credit_balance(deal.seller_id, deal.usd_amount)
    await bot.send_message(
        deal.seller_id,
        f"✅ Получен платеж по сделке {deal.public_id}. Рубли зачислены на баланс.",
    )
    if deal.buyer_id:
        await bot.send_message(
            deal.buyer_id,
            f"Спасибо! Платеж по сделке {deal.public_id} подтвержден. Ожидайте передачу наличных.",
        )
