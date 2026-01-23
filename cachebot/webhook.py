from __future__ import annotations

import hashlib
import hmac
import json
import logging
import shutil
import time
from datetime import datetime, timezone
from contextlib import suppress
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl
from decimal import Decimal, InvalidOperation, ROUND_UP

from aiohttp import web

from cachebot.deps import AppDeps
from cachebot.services.scheduler import handle_paid_invoice
from cachebot.models.advert import AdvertSide
from cachebot.models.deal import DealStatus
from cachebot.models.dispute import EvidenceItem
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, FSInputFile
from PIL import Image, ImageChops, ImageDraw
from cachebot.constants import BANK_OPTIONS
from cachebot.models.user import UserRole

logger = logging.getLogger(__name__)


def create_app(bot, deps: AppDeps) -> web.Application:
    app = web.Application(client_max_size=50 * 1024 * 1024)
    app["bot"] = bot
    app["deps"] = deps
    app.router.add_post(deps.config.webhook_path, _crypto_pay_handler)
    app.router.add_get("/app", _webapp_index)
    app.router.add_get("/app/", _webapp_index)
    app.router.add_get("/app/{path:.*}", _webapp_static)
    app.router.add_get("/api/me", _api_me)
    app.router.add_get("/api/profile", _api_profile)
    app.router.add_post("/api/profile", _api_profile_update)
    app.router.add_post("/api/profile/avatar", _api_profile_avatar)
    app.router.add_get("/api/users/{user_id}", _api_public_profile)
    app.router.add_get("/api/avatar/{user_id}", _api_avatar)
    app.router.add_get("/api/balance", _api_balance)
    app.router.add_get("/api/balance/history", _api_balance_history)
    app.router.add_post("/api/balance/topup", _api_balance_topup)
    app.router.add_post("/api/balance/withdraw", _api_balance_withdraw)
    app.router.add_get("/api/my-deals", _api_my_deals)
    app.router.add_post("/api/deals", _api_create_deal)
    app.router.add_get("/api/deals/{deal_id}", _api_deal_detail)
    app.router.add_post("/api/deals/{deal_id}/cancel", _api_deal_cancel)
    app.router.add_post("/api/deals/{deal_id}/accept", _api_deal_accept)
    app.router.add_post("/api/deals/{deal_id}/decline", _api_deal_decline)
    app.router.add_post("/api/deals/{deal_id}/buyer-ready", _api_deal_buyer_ready)
    app.router.add_post("/api/deals/{deal_id}/seller-ready", _api_deal_seller_ready)
    app.router.add_post("/api/deals/{deal_id}/confirm-buyer", _api_deal_confirm_buyer)
    app.router.add_post("/api/deals/{deal_id}/confirm-seller", _api_deal_confirm_seller)
    app.router.add_post("/api/deals/{deal_id}/buyer-proof", _api_deal_buyer_proof)
    app.router.add_post("/api/deals/{deal_id}/open-dispute", _api_deal_open_dispute)
    app.router.add_post("/api/deals/{deal_id}/qr", _api_deal_upload_qr)
    app.router.add_post("/api/deals/{deal_id}/qr-text", _api_deal_upload_qr_text)
    app.router.add_get("/api/deals/{deal_id}/chat", _api_deal_chat_list)
    app.router.add_post("/api/deals/{deal_id}/chat", _api_deal_chat_send)
    app.router.add_post("/api/deals/{deal_id}/chat/file", _api_deal_chat_send_file)
    app.router.add_get("/api/chat-files/{deal_id}/{filename}", _api_chat_file)
    app.router.add_get("/api/p2p/summary", _api_p2p_summary)
    app.router.add_get("/api/p2p/banks", _api_p2p_banks)
    app.router.add_get("/api/p2p/ads", _api_p2p_public_ads)
    app.router.add_get("/api/p2p/my-ads", _api_p2p_my_ads)
    app.router.add_post("/api/p2p/ads", _api_p2p_create_ad)
    app.router.add_post("/api/p2p/ads/{ad_id}", _api_p2p_update_ad)
    app.router.add_post("/api/p2p/ads/{ad_id}/toggle", _api_p2p_toggle_ad)
    app.router.add_post("/api/p2p/ads/{ad_id}/delete", _api_p2p_delete_ad)
    app.router.add_post("/api/p2p/ads/{ad_id}/offer", _api_p2p_offer_ad)
    app.router.add_post("/api/p2p/trading", _api_p2p_trading)
    app.router.add_get("/api/disputes", _api_disputes_list)
    app.router.add_get("/api/disputes/summary", _api_disputes_summary)
    app.router.add_get("/api/disputes/{dispute_id}", _api_dispute_detail)
    app.router.add_post("/api/disputes/{dispute_id}/assign", _api_dispute_assign)
    app.router.add_post("/api/disputes/{dispute_id}/resolve", _api_dispute_resolve)
    app.router.add_post("/api/disputes/{dispute_id}/evidence", _api_dispute_evidence_upload)
    app.router.add_post("/api/disputes/{dispute_id}/message", _api_dispute_message)
    app.router.add_get("/api/dispute-files/{dispute_id}/{filename}", _api_dispute_file)
    app.router.add_get("/api/admin/summary", _api_admin_summary)
    app.router.add_get("/api/admin/settings", _api_admin_settings)
    app.router.add_post("/api/admin/settings", _api_admin_settings_update)
    app.router.add_get("/api/admin/moderators", _api_admin_moderators)
    app.router.add_post("/api/admin/moderators", _api_admin_add_moderator)
    app.router.add_delete("/api/admin/moderators/{user_id}", _api_admin_remove_moderator)
    app.router.add_get("/api/admin/merchants", _api_admin_merchants)
    app.router.add_post("/api/admin/merchants/{user_id}/revoke", _api_admin_merchant_revoke)
    app.router.add_get("/api/reviews", _api_reviews_list)
    app.router.add_post("/api/reviews", _api_reviews_add)
    app.router.add_get("/api/summary", _api_summary)
    app.router.add_get("/api/ping", _api_ping)
    app.router.add_post("/api/debug/initdata", _api_debug_initdata)
    return app


async def _crypto_pay_handler(request: web.Request) -> web.Response:
    deps: AppDeps = request.app["deps"]
    bot = request.app["bot"]
    secret = deps.config.crypto_pay_webhook_secret
    raw_body = await request.read()
    if secret:
        signature = request.headers.get("X-Crypto-Pay-Signature", "")
        expected = hmac.new(secret.encode(), raw_body, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature.lower(), expected.lower()):
            logger.warning("Crypto Pay webhook signature mismatch")
            raise web.HTTPUnauthorized()
    try:
        payload = json.loads(raw_body.decode("utf-8"))
    except json.JSONDecodeError:
        raise web.HTTPBadRequest(text="Invalid JSON")

    invoice = _extract_invoice(payload)
    if not invoice:
        logger.info("Webhook without invoice: %s", payload)
        return web.json_response({"ok": True})

    invoice_id = invoice.get("invoice_id")
    status = (invoice.get("status") or "").lower()
    if invoice_id and status.startswith("paid"):
        handled = False
        try:
            deal = await deps.deal_service.mark_invoice_paid(str(invoice_id))
            await handle_paid_invoice(deal, deps.kb_client, bot)
            handled = True
        except LookupError:
            handled = False
        except Exception as exc:  # pragma: no cover
            logger.exception("Failed to handle paid invoice %s: %s", invoice_id, exc)
            raise web.HTTPInternalServerError()
        if not handled:
            topup = await deps.topup_service.pop_paid(str(invoice_id))
            if topup:
                await deps.deal_service.deposit_balance(topup.user_id, topup.amount, kind="topup")
                amount_str = f"{topup.amount.quantize(Decimal('0.01')):f}"
                await bot.send_message(
                    topup.user_id,
                    "✅ Пополнение успешно.\n"
                    f"Сумма: {amount_str} USDT\n"
                    "Хороших сделок!",
                )

    return web.json_response({"ok": True})


def _extract_invoice(payload: dict[str, Any]) -> dict[str, Any] | None:
    if "payload" in payload and isinstance(payload["payload"], dict):
        return payload["payload"]
    if "invoice" in payload and isinstance(payload["invoice"], dict):
        return payload["invoice"]
    if payload.get("invoice_id"):
        return payload
    return None


def _webapp_root() -> Path:
    return Path(__file__).resolve().parent / "webapp"


async def _webapp_index(_: web.Request) -> web.Response:
    root = _webapp_root()
    index_path = root / "index.html"
    response = web.FileResponse(index_path)
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


async def _webapp_static(request: web.Request) -> web.Response:
    root = _webapp_root()
    rel_path = request.match_info.get("path") or ""
    safe_path = (root / rel_path).resolve()
    if not safe_path.exists() or root not in safe_path.parents:
        raise web.HTTPNotFound()
    response = web.FileResponse(safe_path)
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


async def _api_ping(_: web.Request) -> web.Response:
    return web.json_response({"ok": True})


async def _api_debug_initdata(request: web.Request) -> web.Response:
    try:
        payload = await request.json()
    except Exception:
        payload = {}
    init_data = (payload.get("init_data") or "").strip()
    unsafe = payload.get("unsafe") or {}
    tag = payload.get("tag") or "-"
    message = payload.get("message")
    source = payload.get("source")
    line = payload.get("line")
    col = payload.get("col")
    stack = payload.get("stack")
    logger.warning(
        "WebApp init debug: tag=%s has_init=%s len=%s has_unsafe=%s user=%s ua=%s msg=%s src=%s line=%s col=%s",
        tag,
        bool(init_data),
        len(init_data),
        bool(unsafe),
        (unsafe or {}).get("user"),
        request.headers.get("User-Agent"),
        message,
        source,
        line,
        col,
    )
    if stack:
        logger.warning("WebApp init debug: stack=%s", stack)
    return web.json_response({"ok": True})


async def _api_me(request: web.Request) -> web.Response:
    deps: AppDeps = request.app["deps"]
    user, user_id = await _require_user(request)
    profile = await deps.user_service.profile_of(user_id)
    payload = {
        "id": user_id,
        "display_name": profile.display_name if profile else None,
        "username": getattr(user, "username", None),
        "first_name": getattr(user, "first_name", None),
        "last_name": getattr(user, "last_name", None),
        "full_name": f"{getattr(user, 'first_name', '')} {getattr(user, 'last_name', '')}".strip()
        or None,
        "avatar_url": _avatar_url(request, profile),
    }
    return web.json_response({"ok": True, "user": payload})


async def _api_profile(request: web.Request) -> web.Response:
    deps: AppDeps = request.app["deps"]
    user, user_id = await _require_user(request)
    profile = await deps.user_service.profile_of(user_id)
    role = await deps.user_service.role_of(user_id)
    merchant_since = await deps.user_service.merchant_since_of(user_id)
    deals = await deps.deal_service.list_user_deals(user_id)
    total_deals = len(deals)
    success_deals = sum(1 for deal in deals if deal.status == DealStatus.COMPLETED)
    failed_deals = sum(1 for deal in deals if deal.status in {DealStatus.CANCELED, DealStatus.EXPIRED})
    success_percent = round((success_deals / total_deals) * 100) if total_deals else 0
    fail_percent = round((failed_deals / total_deals) * 100) if total_deals else 0
    reviews = await deps.review_service.list_for_user(user_id)
    include_private = _is_admin(user_id, deps)
    payload = {
        "user": user,
        "profile": _profile_payload(profile, request=request, include_private=include_private),
        "role": role.value if role else None,
        "merchant_since": merchant_since.isoformat() if merchant_since else None,
        "stats": {
            "total_deals": total_deals,
            "success_percent": success_percent,
            "fail_percent": fail_percent,
            "reviews_count": len(reviews),
        },
    }
    return web.json_response({"ok": True, "data": payload})


async def _api_public_profile(request: web.Request) -> web.Response:
    deps: AppDeps = request.app["deps"]
    await _require_user(request)
    try:
        target_id = int(request.match_info.get("user_id", "0"))
    except ValueError:
        raise web.HTTPBadRequest(text="Некорректный пользователь")
    profile = await deps.user_service.profile_of(target_id)
    if not profile:
        raise web.HTTPNotFound(text="Пользователь не найден")
    role = await deps.user_service.role_of(target_id)
    merchant_since = await deps.user_service.merchant_since_of(target_id)
    deals = await deps.deal_service.list_user_deals(target_id)
    total_deals = len(deals)
    success_deals = sum(1 for deal in deals if deal.status == DealStatus.COMPLETED)
    failed_deals = sum(1 for deal in deals if deal.status in {DealStatus.CANCELED, DealStatus.EXPIRED})
    success_percent = round((success_deals / total_deals) * 100) if total_deals else 0
    fail_percent = round((failed_deals / total_deals) * 100) if total_deals else 0
    reviews = await deps.review_service.list_for_user(target_id)
    payload = {
        "profile": _profile_payload(profile, request=request, include_private=False),
        "role": role.value if role else None,
        "merchant_since": merchant_since.isoformat() if merchant_since else None,
        "stats": {
            "total_deals": total_deals,
            "success_percent": success_percent,
            "fail_percent": fail_percent,
            "reviews_count": len(reviews),
        },
    }
    return web.json_response({"ok": True, "data": payload})


async def _api_profile_update(request: web.Request) -> web.Response:
    deps: AppDeps = request.app["deps"]
    _, user_id = await _require_user(request)
    try:
        body = await request.json()
    except Exception:
        raise web.HTTPBadRequest(text="Invalid JSON")
    display_name = str(body.get("display_name") or "").strip()
    if len(display_name) < 2 or len(display_name) > 32:
        raise web.HTTPBadRequest(text="Некорректное имя")
    profile = await deps.user_service.update_profile(user_id, display_name=display_name)
    payload = _profile_payload(profile, request=request, include_private=_is_admin(user_id, deps))
    return web.json_response({"ok": True, "profile": payload})


async def _api_profile_avatar(request: web.Request) -> web.Response:
    deps: AppDeps = request.app["deps"]
    _, user_id = await _require_user(request)
    reader = await request.multipart()
    field = await reader.next()
    if not field or field.name != "avatar":
        raise web.HTTPBadRequest(text="Нет файла")
    filename = field.filename or "avatar.jpg"
    ext = Path(filename).suffix.lower()
    if ext not in {".jpg", ".jpeg", ".png", ".webp"}:
        ext = ".jpg"
    avatar_dir = _avatar_dir(deps)
    avatar_dir.mkdir(parents=True, exist_ok=True)
    avatar_path = avatar_dir / f"{user_id}{ext}"
    with avatar_path.open("wb") as handle:
        while True:
            chunk = await field.read_chunk()
            if not chunk:
                break
            handle.write(chunk)
    profile = await deps.user_service.update_profile(user_id, avatar_path=str(avatar_path))
    payload = _profile_payload(profile, request=request, include_private=_is_admin(user_id, deps))
    return web.json_response({"ok": True, "profile": payload})


async def _api_avatar(request: web.Request) -> web.Response:
    deps: AppDeps = request.app["deps"]
    user_id = request.match_info.get("user_id", "")
    try:
        uid = int(user_id)
    except ValueError:
        raise web.HTTPNotFound()
    profile = await deps.user_service.profile_of(uid)
    if not profile or not profile.avatar_path:
        raise web.HTTPNotFound()
    avatar_dir = _avatar_dir(deps).resolve()
    path = Path(profile.avatar_path).resolve()
    if avatar_dir not in path.parents or not path.exists():
        raise web.HTTPNotFound()
    return web.FileResponse(path)


async def _api_balance(request: web.Request) -> web.Response:
    deps: AppDeps = request.app["deps"]
    _, user_id = await _require_user(request)
    balance = await deps.deal_service.balance_of(user_id)
    reserved = await deps.deal_service.reserved_of(user_id)
    total = balance + reserved
    return web.json_response(
        {"ok": True, "balance": str(balance), "reserved": str(reserved), "total": str(total)}
    )


async def _api_balance_history(request: web.Request) -> web.Response:
    deps: AppDeps = request.app["deps"]
    _, user_id = await _require_user(request)
    items = await deps.deal_service.balance_history(user_id)
    payload = [
        {
            "id": item.id,
            "amount": str(item.amount),
            "kind": item.kind,
            "created_at": item.created_at.isoformat(),
            "meta": item.meta or {},
        }
        for item in items
    ]
    return web.json_response({"ok": True, "items": payload})


async def _api_balance_topup(request: web.Request) -> web.Response:
    deps: AppDeps = request.app["deps"]
    _, user_id = await _require_user(request)
    try:
        body = await request.json()
    except Exception:
        raise web.HTTPBadRequest(text="Invalid JSON")
    try:
        amount = Decimal(str(body.get("amount")))
    except (InvalidOperation, TypeError):
        raise web.HTTPBadRequest(text="Некорректная сумма")
    if amount <= 0:
        raise web.HTTPBadRequest(text="Сумма должна быть больше нуля")
    invoice = await deps.crypto_pay.create_invoice(
        amount=amount,
        currency="USDT",
        description="Пополнение баланса",
        payload=f"topup:{user_id}",
    )
    await deps.topup_service.create(user_id=user_id, amount=amount, invoice_id=invoice.invoice_id)
    amount_str = f"{amount.quantize(Decimal('0.01')):f}"
    bot = request.app.get("bot")
    if bot:
        markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="💳 Оплатить", url=invoice.pay_url)]
            ]
        )
        await bot.send_message(
            user_id,
            f"Новое пополнение на {amount_str} USDT.\n"
            "Нажмите на кнопку ниже для оплаты счета.",
            reply_markup=markup,
        )
    return web.json_response({"ok": True, "invoice_id": invoice.invoice_id, "pay_url": invoice.pay_url})


async def _api_balance_withdraw(request: web.Request) -> web.Response:
    deps: AppDeps = request.app["deps"]
    user, user_id = await _require_user(request)
    try:
        body = await request.json()
    except Exception:
        raise web.HTTPBadRequest(text="Invalid JSON")
    try:
        amount = Decimal(str(body.get("amount")))
    except (InvalidOperation, TypeError):
        raise web.HTTPBadRequest(text="Некорректная сумма")
    if amount <= 0:
        raise web.HTTPBadRequest(text="Сумма должна быть больше нуля")
    fee_percent = deps.config.withdraw_fee_percent
    fee = (amount * fee_percent / Decimal("100")).quantize(Decimal("0.00000001"))
    total = (amount + fee).quantize(Decimal("0.00000001"))
    balance = await deps.deal_service.balance_of(user_id)
    if balance < total:
        raise web.HTTPBadRequest(text="Недостаточно средств")
    try:
        await deps.deal_service.withdraw_balance(user_id, total)
    except Exception as exc:
        raise web.HTTPBadRequest(text=f"Не удалось списать средства: {exc}")
    try:
        await deps.crypto_pay.transfer(user_id=user_id, amount=amount, currency="USDT")
    except Exception as exc:
        await deps.deal_service.deposit_balance(user_id, total, kind="refund", record_event=False)
        raise web.HTTPBadRequest(text=f"Перевод не выполнен: {exc}")
    return web.json_response(
        {
            "ok": True,
            "amount": str(amount),
            "fee": str(fee),
            "total": str(total),
            "username": user.get("username") or "",
        }
    )


async def _api_summary(request: web.Request) -> web.Response:
    deps: AppDeps = request.app["deps"]
    _, user_id = await _require_user(request)
    deals = await deps.deal_service.list_user_deals(user_id)
    balance = await deps.deal_service.balance_of(user_id)
    return web.json_response(
        {
            "ok": True,
            "deals_total": len(deals),
            "deals_active": sum(1 for deal in deals if deal.status.value in {"open", "reserved", "paid", "dispute"}),
            "balance": str(balance),
        }
    )


async def _api_my_deals(request: web.Request) -> web.Response:
    deps: AppDeps = request.app["deps"]
    _, user_id = await _require_user(request)
    deals = await deps.deal_service.list_user_deals(user_id)
    deals.sort(key=lambda deal: deal.created_at, reverse=True)
    payload = []
    for deal in deals:
        payload.append(await _deal_payload(deps, deal, user_id, request=request))
    return web.json_response({"ok": True, "deals": payload})


async def _api_create_deal(request: web.Request) -> web.Response:
    deps: AppDeps = request.app["deps"]
    _, user_id = await _require_user(request)
    role = await deps.user_service.role_of(user_id)
    if role != UserRole.SELLER:
        raise web.HTTPForbidden(text="Доступно только продавцу")
    try:
        body = await request.json()
    except Exception:
        raise web.HTTPBadRequest(text="Invalid JSON")
    try:
        rub_amount = Decimal(str(body.get("rub_amount")))
    except InvalidOperation:
        raise web.HTTPBadRequest(text="Некорректная сумма")
    if rub_amount <= 0:
        raise web.HTTPBadRequest(text="Сумма должна быть больше нуля")
    deal = await deps.deal_service.create_deal(user_id, rub_amount)
    payload = await _deal_payload(deps, deal, user_id, with_actions=True, request=request)
    return web.json_response({"ok": True, "deal": payload})


async def _api_deal_detail(request: web.Request) -> web.Response:
    deps: AppDeps = request.app["deps"]
    _, user_id = await _require_user(request)
    deal_id = request.match_info["deal_id"]
    deal = await deps.deal_service.get_deal(deal_id)
    if not deal:
        raise web.HTTPNotFound(text="Deal not found")
    if user_id not in {deal.seller_id, deal.buyer_id}:
        raise web.HTTPForbidden(text="Нет доступа к сделке")
    payload = await _deal_payload(deps, deal, user_id, with_actions=True, request=request)
    return web.json_response({"ok": True, "deal": payload})


async def _api_deal_cancel(request: web.Request) -> web.Response:
    deps: AppDeps = request.app["deps"]
    _, user_id = await _require_user(request)
    deal_id = request.match_info["deal_id"]
    try:
        deal, _ = await deps.deal_service.cancel_deal(deal_id, user_id)
    except PermissionError:
        raise web.HTTPForbidden(text="Отмена недоступна")
    except LookupError:
        raise web.HTTPNotFound(text="Deal not found")
    if deal.is_p2p and deal.advert_id:
        try:
            base_usdt = deal.usd_amount / deal.rate
            await deps.advert_service.restore_volume(deal.advert_id, base_usdt)
        except Exception:
            pass
    payload = await _deal_payload(deps, deal, user_id, with_actions=True, request=request)
    return web.json_response({"ok": True, "deal": payload})


async def _api_deal_accept(request: web.Request) -> web.Response:
    deps: AppDeps = request.app["deps"]
    bot = request.app["bot"]
    _, user_id = await _require_user(request)
    deal_id = request.match_info["deal_id"]
    try:
        deal = await deps.deal_service.accept_p2p_offer(deal_id, user_id)
    except (PermissionError, ValueError) as exc:
        raise web.HTTPBadRequest(text=str(exc))
    await bot.send_message(
        deal.seller_id,
        f"✅ Сделка {deal.hashtag} закреплена за тобой.\n"
        "Оплата подтверждена, можно продолжать сделку.",
    )
    if deal.buyer_id:
        await bot.send_message(
            deal.buyer_id,
            f"✅ Сделка {deal.hashtag} создана.\nОплата подтверждена, можно продолжать сделку.",
        )
    payload = await _deal_payload(deps, deal, user_id, with_actions=True, request=request)
    return web.json_response({"ok": True, "deal": payload})


async def _api_deal_decline(request: web.Request) -> web.Response:
    deps: AppDeps = request.app["deps"]
    bot = request.app["bot"]
    _, user_id = await _require_user(request)
    deal_id = request.match_info["deal_id"]
    try:
        deal, base_usdt = await deps.deal_service.decline_p2p_offer(deal_id, user_id)
    except (PermissionError, ValueError) as exc:
        raise web.HTTPBadRequest(text=str(exc))
    if deal.is_p2p and deal.advert_id and base_usdt:
        with suppress(Exception):
            await deps.advert_service.restore_volume(deal.advert_id, base_usdt)
    initiator_id = deal.offer_initiator_id
    if initiator_id and initiator_id != user_id:
        await bot.send_message(
            initiator_id,
            f"❌ Предложение по сделке {deal.hashtag} отклонено.",
        )
    payload = await _deal_payload(deps, deal, user_id, with_actions=True, request=request)
    return web.json_response({"ok": True, "deal": payload})


async def _api_deal_buyer_ready(request: web.Request) -> web.Response:
    deps: AppDeps = request.app["deps"]
    bot = request.app["bot"]
    _, user_id = await _require_user(request)
    deal_id = request.match_info["deal_id"]
    try:
        deal = await deps.deal_service.buyer_ready_for_qr(deal_id, user_id)
    except (PermissionError, ValueError) as exc:
        raise web.HTTPBadRequest(text=str(exc))
    await deps.chat_service.add_message(
        deal_id=deal_id,
        sender_id=0,
        text="Покупатель готов сканировать QR.",
        file_path=None,
        file_name=None,
        system=True,
        recipient_id=deal.seller_id,
    )
    await deps.chat_service.add_message(
        deal_id=deal_id,
        sender_id=0,
        text="Нужно отправить QR в приложении.",
        file_path=None,
        file_name=None,
        system=True,
        recipient_id=deal.seller_id,
    )
    with suppress(Exception):
        await bot.send_message(
            deal.seller_id,
            "🔔 Новое уведомление по сделке\n"
            "Отправьте QR в течение 5 минут.",
        )
    payload = await _deal_payload(deps, deal, user_id, with_actions=True, request=request)
    return web.json_response({"ok": True, "deal": payload})


async def _api_deal_seller_ready(request: web.Request) -> web.Response:
    deps: AppDeps = request.app["deps"]
    _, user_id = await _require_user(request)
    deal_id = request.match_info["deal_id"]
    try:
        deal = await deps.deal_service.seller_request_qr(deal_id, user_id)
    except (PermissionError, ValueError) as exc:
        raise web.HTTPBadRequest(text=str(exc))
    await deps.chat_service.add_message(
        deal_id=deal_id,
        sender_id=0,
        text="Продавец запросил готовность покупателя.",
        file_path=None,
        file_name=None,
        system=True,
        recipient_id=deal.buyer_id,
    )
    if deal.buyer_id:
        with suppress(Exception):
            await request.app["bot"].send_message(
                deal.buyer_id,
                "Продавец готов отправить QR.\nНажмите «Готов сканировать».",
            )
    payload = await _deal_payload(deps, deal, user_id, with_actions=True, request=request)
    return web.json_response({"ok": True, "deal": payload})


async def _api_deal_confirm_buyer(request: web.Request) -> web.Response:
    deps: AppDeps = request.app["deps"]
    _, user_id = await _require_user(request)
    deal_id = request.match_info["deal_id"]
    try:
        deal, _ = await deps.deal_service.confirm_buyer_cash(deal_id, user_id)
    except (PermissionError, ValueError) as exc:
        raise web.HTTPBadRequest(text=str(exc))
    payload = await _deal_payload(deps, deal, user_id, with_actions=True, request=request)
    return web.json_response({"ok": True, "deal": payload})


async def _api_deal_buyer_proof(request: web.Request) -> web.Response:
    deps: AppDeps = request.app["deps"]
    _, user_id = await _require_user(request)
    deal_id = request.match_info["deal_id"]
    deal = await deps.deal_service.get_deal(deal_id)
    if not deal:
        raise web.HTTPNotFound(text="Сделка не найдена")
    if user_id != deal.buyer_id and user_id not in deps.config.admin_ids:
        raise web.HTTPForbidden(text="Нет доступа")
    reader = await request.multipart()
    field = await reader.next()
    if not field or field.name != "file":
        raise web.HTTPBadRequest(text="Файл не найден")
    try:
        deal, _ = await deps.deal_service.confirm_buyer_cash(deal_id, deal.buyer_id or user_id)
    except (PermissionError, ValueError):
        deal = await deps.deal_service.get_deal(deal_id)
    filename = Path(field.filename or "proof.png").name
    chat_dir = _chat_dir(deps) / deal_id
    chat_dir.mkdir(parents=True, exist_ok=True)
    file_path = chat_dir / filename
    with file_path.open("wb") as handle:
        while True:
            chunk = await field.read_chunk()
            if not chunk:
                break
            handle.write(chunk)
    msg = await deps.chat_service.add_message(
        deal_id=deal_id,
        sender_id=0,
        text="Фото операции от покупателя.",
        file_path=str(file_path),
        file_name=filename,
        system=True,
        recipient_id=deal.seller_id,
    )
    payload = {
        **msg.to_dict(),
        "file_url": _chat_file_url(request, msg),
    }
    return web.json_response({"ok": True, "message": payload})


async def _api_deal_confirm_seller(request: web.Request) -> web.Response:
    deps: AppDeps = request.app["deps"]
    _, user_id = await _require_user(request)
    deal_id = request.match_info["deal_id"]
    try:
        deal, _ = await deps.deal_service.confirm_seller_cash(deal_id, user_id)
    except (PermissionError, ValueError) as exc:
        raise web.HTTPBadRequest(text=str(exc))
    payload = await _deal_payload(deps, deal, user_id, with_actions=True, request=request)
    return web.json_response({"ok": True, "deal": payload})


async def _api_deal_open_dispute(request: web.Request) -> web.Response:
    deps: AppDeps = request.app["deps"]
    _, user_id = await _require_user(request)
    deal_id = request.match_info["deal_id"]
    comment = None
    reason = "Открыт через WebApp"
    with suppress(Exception):
        payload = await request.json()
        if isinstance(payload, dict):
            raw_comment = payload.get("comment")
            if isinstance(raw_comment, str):
                comment = raw_comment.strip() or None
            reason_key = payload.get("reason")
            reason_text = payload.get("reason_text")
            if isinstance(reason_key, str):
                reason_key = reason_key.strip()
                if reason_key == "no_cash":
                    reason = "Не получил деньги"
                elif reason_key == "partial":
                    reason = "Получил, но не все"
                elif reason_key == "other":
                    reason = "Другая причина"
                    if isinstance(reason_text, str):
                        extra = reason_text.strip()
                        if extra:
                            reason = f"Другая причина: {extra}"
    deal = await deps.deal_service.get_deal(deal_id)
    if not deal:
        raise web.HTTPNotFound(text="Сделка не найдена")
    now = datetime.now(timezone.utc)
    if deal.dispute_available_at and deal.dispute_available_at > now:
        remaining = deal.dispute_available_at - now
        minutes = max(1, int(remaining.total_seconds() // 60))
        raise web.HTTPBadRequest(text=f"Спор доступен через {minutes} мин")
    try:
        deal = await deps.deal_service.open_dispute(deal_id, user_id)
    except (PermissionError, ValueError) as exc:
        raise web.HTTPBadRequest(text=str(exc))
    if not await deps.dispute_service.dispute_for_deal(deal_id):
        await deps.dispute_service.open_dispute(
            deal_id=deal_id,
            opened_by=user_id,
            reason=reason,
            comment=comment,
            evidence=[],
        )
    await deps.chat_service.add_message(
        deal_id=deal_id,
        sender_id=0,
        text="Открыт спор.",
        file_path=None,
        file_name=None,
        system=True,
    )
    other_id = None
    if deal.seller_id and deal.buyer_id:
        other_id = deal.buyer_id if user_id == deal.seller_id else deal.seller_id
    with suppress(Exception):
        if other_id:
            await request.app["bot"].send_message(
                other_id,
                f"Спор по сделке #{deal.public_id} открыт.\n"
                "Если хотите внести уточнение, перейдите к сделке.",
            )
    payload = await _deal_payload(deps, deal, user_id, with_actions=True, request=request)
    return web.json_response({"ok": True, "deal": payload})


async def _api_deal_upload_qr(request: web.Request) -> web.Response:
    deps: AppDeps = request.app["deps"]
    _, user_id = await _require_user(request)
    deal_id = request.match_info["deal_id"]
    deal = await deps.deal_service.get_deal(deal_id)
    if not deal:
        raise web.HTTPNotFound(text="Сделка не найдена")
    if user_id != deal.seller_id and user_id not in deps.config.admin_ids:
        raise web.HTTPForbidden(text="Нет доступа")
    reader = await request.multipart()
    field = await reader.next()
    if not field or field.name != "file":
        raise web.HTTPBadRequest(text="Файл не найден")
    filename = Path(field.filename or "qr.png").name
    chat_dir = _chat_dir(deps) / deal_id
    chat_dir.mkdir(parents=True, exist_ok=True)
    file_path = chat_dir / filename
    with file_path.open("wb") as handle:
        while True:
            chunk = await field.read_chunk()
            if not chunk:
                break
            handle.write(chunk)
    await deps.deal_service.attach_qr_web(deal_id, deal.seller_id, filename)
    msg = await deps.chat_service.add_message(
        deal_id=deal_id,
        sender_id=user_id,
        text="QR код",
        file_path=str(file_path),
        file_name=filename,
        system=False,
    )
    if deal.buyer_id:
        deal_label = f"#{deal.public_id}" if getattr(deal, "public_id", None) else deal_id
        with suppress(Exception):
            await request.app["bot"].send_photo(
                deal.buyer_id,
                FSInputFile(str(file_path)),
                caption=f"QR по сделке {deal_label}.",
            )
    payload = {
        **msg.to_dict(),
        "file_url": _chat_file_url(request, msg),
    }
    return web.json_response({"ok": True, "message": payload})


async def _api_deal_upload_qr_text(request: web.Request) -> web.Response:
    deps: AppDeps = request.app["deps"]
    _, user_id = await _require_user(request)
    deal_id = request.match_info["deal_id"]
    deal = await deps.deal_service.get_deal(deal_id)
    if not deal:
        raise web.HTTPNotFound(text="Сделка не найдена")
    if user_id != deal.seller_id and user_id not in deps.config.admin_ids:
        raise web.HTTPForbidden(text="Нет доступа")
    try:
        body = await request.json()
    except Exception:
        raise web.HTTPBadRequest(text="Invalid JSON")
    text = (body.get("text") or "").strip()
    if not text:
        raise web.HTTPBadRequest(text="Пустой QR")
    try:
        import qrcode
        from qrcode.image.styledpil import StyledPilImage
        from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
        from qrcode.image.styles.colormasks import SolidFillColorMask
        try:
            from qrcode.image.styles.eyedrawers import RoundedEyeDrawer
        except Exception:
            RoundedEyeDrawer = None
    except Exception:
        raise web.HTTPInternalServerError(text="QR генератор недоступен")
    chat_dir = _chat_dir(deps) / deal_id
    chat_dir.mkdir(parents=True, exist_ok=True)
    filename = f"qr-{int(time.time())}.png"
    file_path = chat_dir / filename
    qr = qrcode.QRCode(
        box_size=12,
        border=2,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
    )
    qr.add_data(text)
    qr.make(fit=True)
    image_kwargs = dict(
        image_factory=StyledPilImage,
        module_drawer=RoundedModuleDrawer(),
        color_mask=SolidFillColorMask(back_color=(255, 255, 255), front_color=(0, 0, 0)),
    )
    if RoundedEyeDrawer:
        image_kwargs["eye_drawer"] = RoundedEyeDrawer()
    img = qr.make_image(**image_kwargs).convert("RGBA")
    img = _apply_rounded_eyes(img, qr)
    img = _apply_qr_logo(img)
    img.save(file_path)
    await deps.deal_service.attach_qr_web(deal_id, deal.seller_id, filename)
    msg = await deps.chat_service.add_message(
        deal_id=deal_id,
        sender_id=user_id,
        text="QR код",
        file_path=str(file_path),
        file_name=filename,
        system=False,
    )
    if deal.buyer_id:
        deal_label = f"#{deal.public_id}" if getattr(deal, "public_id", None) else deal_id
        with suppress(Exception):
            await request.app["bot"].send_photo(
                deal.buyer_id,
                FSInputFile(str(file_path)),
                caption=f"QR по сделке {deal_label}.",
            )
    payload = {
        **msg.to_dict(),
        "file_url": _chat_file_url(request, msg),
    }
    return web.json_response({"ok": True, "message": payload})


async def _api_deal_chat_list(request: web.Request) -> web.Response:
    deps: AppDeps = request.app["deps"]
    _, user_id = await _require_user(request)
    deal_id = request.match_info["deal_id"]
    deal = await deps.deal_service.get_deal(deal_id)
    if not deal:
        raise web.HTTPNotFound(text="Сделка не найдена")
    if user_id not in {deal.seller_id, deal.buyer_id} and user_id not in deps.config.admin_ids:
        dispute = await deps.dispute_service.dispute_for_deal(deal_id)
        if not dispute or not await _has_dispute_access(user_id, deps):
            raise web.HTTPForbidden(text="Нет доступа")
    include_all = user_id in deps.config.admin_ids
    messages = await deps.chat_service.list_messages_for_user(
        deal_id, user_id, include_all=include_all
    )
    admin_ids = set(deps.config.admin_ids or [])
    admin_profiles: dict[int, dict[str, Any] | None] = {}
    for msg in messages:
        if msg.sender_id in admin_ids and msg.sender_id not in admin_profiles:
            profile = await deps.user_service.profile_of(msg.sender_id)
            admin_profiles[msg.sender_id] = _profile_payload(
                profile, request=request, include_private=True
            )
    payload = []
    for msg in messages:
        label = None
        if msg.sender_id in admin_ids and not msg.system:
            dispute_any = await deps.dispute_service.dispute_any_for_deal(deal_id)
            profile = admin_profiles.get(msg.sender_id) or {}
            name = (
                profile.get("display_name")
                or profile.get("full_name")
                or profile.get("username")
                or msg.sender_id
            )
            if dispute_any and dispute_any.assigned_to == msg.sender_id:
                label = f"Модератор {name}"
        payload.append(
            {
                **msg.to_dict(),
                "sender_label": label,
                "file_url": _chat_file_url(request, msg) if msg.file_path else None,
            }
        )
    return web.json_response({"ok": True, "messages": payload})


async def _api_deal_chat_send(request: web.Request) -> web.Response:
    deps: AppDeps = request.app["deps"]
    _, user_id = await _require_user(request)
    deal_id = request.match_info["deal_id"]
    deal = await deps.deal_service.get_deal(deal_id)
    if not deal:
        raise web.HTTPNotFound(text="Сделка не найдена")
    if user_id not in {deal.seller_id, deal.buyer_id} and user_id not in deps.config.admin_ids:
        raise web.HTTPForbidden(text="Нет доступа")
    try:
        body = await request.json()
    except Exception:
        raise web.HTTPBadRequest(text="Invalid JSON")
    text = (body.get("text") or "").strip()
    if not text:
        raise web.HTTPBadRequest(text="Пустое сообщение")
    msg = await deps.chat_service.add_message(
        deal_id=deal_id,
        sender_id=user_id,
        text=text,
        file_path=None,
        file_name=None,
    )
    is_moderator = user_id in set(deps.config.admin_ids or []) or await deps.user_service.is_moderator(user_id)
    if is_moderator:
        with suppress(Exception):
            notice = f"⚠️ Модератор написал в чате сделки #{deal.public_id}.\nОткройте приложение."
            if deal.seller_id and deal.seller_id != user_id:
                await request.app["bot"].send_message(deal.seller_id, notice)
            if deal.buyer_id and deal.buyer_id != user_id:
                await request.app["bot"].send_message(deal.buyer_id, notice)
    sender_label = None
    if user_id in set(deps.config.admin_ids or []):
        dispute_any = await deps.dispute_service.dispute_any_for_deal(deal_id)
        profile = await deps.user_service.profile_of(user_id)
        data = _profile_payload(profile, request=request, include_private=True) or {}
        name = data.get("display_name") or data.get("full_name") or data.get("username") or user_id
        if dispute_any and dispute_any.assigned_to == user_id:
            sender_label = f"Модератор {name}"
    payload = {**msg.to_dict(), "file_url": None, "sender_label": sender_label}
    return web.json_response({"ok": True, "message": payload})


async def _api_deal_chat_send_file(request: web.Request) -> web.Response:
    deps: AppDeps = request.app["deps"]
    _, user_id = await _require_user(request)
    deal_id = request.match_info["deal_id"]
    deal = await deps.deal_service.get_deal(deal_id)
    if not deal:
        raise web.HTTPNotFound(text="Сделка не найдена")
    if user_id not in {deal.seller_id, deal.buyer_id} and user_id not in deps.config.admin_ids:
        raise web.HTTPForbidden(text="Нет доступа")
    reader = await request.multipart()
    field = await reader.next()
    if not field or field.name != "file":
        raise web.HTTPBadRequest(text="Файл не найден")
    filename = Path(field.filename or "file").name
    chat_dir = _chat_dir(deps) / deal_id
    chat_dir.mkdir(parents=True, exist_ok=True)
    file_path = chat_dir / filename
    with file_path.open("wb") as handle:
        while True:
            chunk = await field.read_chunk()
            if not chunk:
                break
            handle.write(chunk)
    text_field = await reader.next()
    text = None
    if text_field and text_field.name == "text":
        raw = await text_field.text()
        text = raw.strip() if raw else None
    msg = await deps.chat_service.add_message(
        deal_id=deal_id,
        sender_id=user_id,
        text=text,
        file_path=str(file_path),
        file_name=filename,
    )
    is_moderator = user_id in set(deps.config.admin_ids or []) or await deps.user_service.is_moderator(user_id)
    if is_moderator:
        with suppress(Exception):
            notice = f"⚠️ Модератор отправил файл в чате сделки #{deal.public_id}.\nОткройте приложение."
            if deal.seller_id and deal.seller_id != user_id:
                await request.app["bot"].send_message(deal.seller_id, notice)
            if deal.buyer_id and deal.buyer_id != user_id:
                await request.app["bot"].send_message(deal.buyer_id, notice)
    sender_label = None
    if user_id in set(deps.config.admin_ids or []):
        dispute_any = await deps.dispute_service.dispute_any_for_deal(deal_id)
        profile = await deps.user_service.profile_of(user_id)
        data = _profile_payload(profile, request=request, include_private=True) or {}
        name = data.get("display_name") or data.get("full_name") or data.get("username") or user_id
        if dispute_any and dispute_any.assigned_to == user_id:
            sender_label = f"Модератор {name}"
    payload = {
        **msg.to_dict(),
        "file_url": _chat_file_url(request, msg),
        "sender_label": sender_label,
    }
    return web.json_response({"ok": True, "message": payload})


async def _api_chat_file(request: web.Request) -> web.Response:
    deps: AppDeps = request.app["deps"]
    _, user_id = await _require_user(request)
    deal_id = request.match_info["deal_id"]
    filename = request.match_info["filename"]
    deal = await deps.deal_service.get_deal(deal_id)
    if not deal:
        raise web.HTTPNotFound(text="Сделка не найдена")
    if user_id not in {deal.seller_id, deal.buyer_id} and user_id not in deps.config.admin_ids:
        raise web.HTTPForbidden(text="Нет доступа")
    chat_dir = _chat_dir(deps).resolve()
    path = (chat_dir / deal_id / filename).resolve()
    if chat_dir not in path.parents or not path.exists():
        raise web.HTTPNotFound()
    return web.FileResponse(path)


async def _api_p2p_summary(request: web.Request) -> web.Response:
    deps: AppDeps = request.app["deps"]
    _, user_id = await _require_user(request)
    active, total = await deps.advert_service.counts_for_user(user_id)
    trading = await deps.advert_service.trading_enabled(user_id)
    return web.json_response({"ok": True, "active": active, "total": total, "trading": trading})


async def _api_p2p_banks(_: web.Request) -> web.Response:
    banks = [{"key": key, "label": label} for key, label in BANK_OPTIONS.items()]
    return web.json_response({"ok": True, "banks": banks})


async def _api_p2p_public_ads(request: web.Request) -> web.Response:
    deps: AppDeps = request.app["deps"]
    _, user_id = await _require_user(request)
    side = request.query.get("side", "sell").lower()
    if side not in {"sell", "buy"}:
        raise web.HTTPBadRequest(text="Invalid side")
    ads = await deps.advert_service.list_public_ads(
        AdvertSide(side),
        exclude_user_id=user_id,
    )
    payload = []
    for ad in ads:
        ad, available = await _ensure_ad_availability(deps, ad)
        if not ad.active or available <= 0:
            continue
        payload.append(await _ad_payload(deps, ad, available_usdt=available, request=request))
    return web.json_response({"ok": True, "ads": payload})


async def _api_p2p_my_ads(request: web.Request) -> web.Response:
    deps: AppDeps = request.app["deps"]
    _, user_id = await _require_user(request)
    ads = await deps.advert_service.list_user_ads(user_id)
    payload = []
    for ad in ads:
        ad, available = await _ensure_ad_availability(deps, ad)
        payload.append(
            await _ad_payload(
                deps, ad, include_owner=False, available_usdt=available, request=request
            )
        )
    return web.json_response({"ok": True, "ads": payload})


async def _api_p2p_create_ad(request: web.Request) -> web.Response:
    deps: AppDeps = request.app["deps"]
    _, user_id = await _require_user(request)
    try:
        body = await request.json()
    except Exception:
        raise web.HTTPBadRequest(text="Invalid JSON")
    values = _parse_ad_values(body)
    if not values:
        raise web.HTTPBadRequest(text="Некорректные значения")
    side, total_usdt, price_rub, min_rub, max_rub, banks, terms = values
    balance = await deps.deal_service.balance_of(user_id)
    if total_usdt > balance:
        raise web.HTTPBadRequest(text="Недостаточно баланса для объёма объявления")
    _validate_ad_limits(total_usdt, price_rub, min_rub, max_rub)
    ad = await deps.advert_service.create_ad(
        user_id,
        side=side,
        total_usdt=total_usdt,
        price_rub=price_rub,
        min_rub=min_rub,
        max_rub=max_rub,
        banks=banks,
        terms=terms,
    )
    payload = await _ad_payload(deps, ad, include_owner=False, request=request)
    return web.json_response({"ok": True, "ad": payload})


async def _api_p2p_update_ad(request: web.Request) -> web.Response:
    deps: AppDeps = request.app["deps"]
    _, user_id = await _require_user(request)
    ad_id = request.match_info["ad_id"]
    ad = await deps.advert_service.get_ad(ad_id)
    if not ad:
        raise web.HTTPNotFound(text="Объявление не найдено")
    if ad.owner_id != user_id:
        raise web.HTTPForbidden(text="Нет доступа")
    try:
        body = await request.json()
    except Exception:
        raise web.HTTPBadRequest(text="Invalid JSON")
    price_rub = _parse_decimal(body.get("price_rub"), fallback=ad.price_rub)
    total_usdt = _parse_decimal(body.get("total_usdt"), fallback=ad.total_usdt)
    min_rub = _parse_decimal(body.get("min_rub"), fallback=ad.min_rub)
    max_rub = _parse_decimal(body.get("max_rub"), fallback=ad.max_rub)
    banks = list(body.get("banks")) if body.get("banks") is not None else ad.banks
    terms_raw = body.get("terms") if "terms" in body else ad.terms
    terms = (terms_raw or None) if str(terms_raw or "").strip() else None
    if price_rub <= 0 or total_usdt <= 0:
        raise web.HTTPBadRequest(text="Значение должно быть больше нуля")
    if min_rub <= 0 or max_rub <= 0 or min_rub > max_rub:
        raise web.HTTPBadRequest(text="Некорректные лимиты")
    if not banks:
        raise web.HTTPBadRequest(text="Нужно выбрать банки")
    balance = await deps.deal_service.balance_of(user_id)
    if total_usdt > balance:
        raise web.HTTPBadRequest(text="Недостаточно баланса для объёма объявления")
    _validate_ad_limits(total_usdt, price_rub, min_rub, max_rub)
    updated = await deps.advert_service.update_ad(
        ad_id,
        price_rub=price_rub,
        total_usdt=total_usdt,
        remaining_usdt=total_usdt,
        min_rub=min_rub,
        max_rub=max_rub,
        banks=banks,
        terms=terms,
    )
    payload = await _ad_payload(deps, updated, include_owner=False, request=request)
    return web.json_response({"ok": True, "ad": payload})


async def _api_p2p_toggle_ad(request: web.Request) -> web.Response:
    deps: AppDeps = request.app["deps"]
    _, user_id = await _require_user(request)
    ad_id = request.match_info["ad_id"]
    ad = await deps.advert_service.get_ad(ad_id)
    if not ad:
        raise web.HTTPNotFound(text="Объявление не найдено")
    if ad.owner_id != user_id:
        raise web.HTTPForbidden(text="Нет доступа")
    try:
        body = await request.json()
        desired = body.get("active")
    except Exception:
        desired = None
    if desired is None:
        desired = not ad.active
    if bool(desired):
        _, available = await _ensure_ad_availability(deps, ad)
        if available <= 0:
            raise web.HTTPBadRequest(text="Недостаточно баланса для публикации")
        if ad.min_rub > available * ad.price_rub:
            raise web.HTTPBadRequest(text="Лимиты превышают доступный объём")
    updated = await deps.advert_service.toggle_active(ad_id, bool(desired))
    payload = await _ad_payload(deps, updated, include_owner=False, request=request)
    return web.json_response({"ok": True, "ad": payload})


async def _api_p2p_delete_ad(request: web.Request) -> web.Response:
    deps: AppDeps = request.app["deps"]
    _, user_id = await _require_user(request)
    ad_id = request.match_info["ad_id"]
    ad = await deps.advert_service.get_ad(ad_id)
    if not ad:
        raise web.HTTPNotFound(text="Объявление не найдено")
    if ad.owner_id != user_id:
        raise web.HTTPForbidden(text="Нет доступа")
    await deps.advert_service.delete_ad(ad_id)
    return web.json_response({"ok": True})


async def _api_p2p_trading(request: web.Request) -> web.Response:
    deps: AppDeps = request.app["deps"]
    _, user_id = await _require_user(request)
    try:
        body = await request.json()
    except Exception:
        raise web.HTTPBadRequest(text="Invalid JSON")
    enabled = bool(body.get("enabled"))
    await deps.advert_service.set_trading(user_id, enabled)
    return web.json_response({"ok": True, "enabled": enabled})


async def _api_p2p_offer_ad(request: web.Request) -> web.Response:
    deps: AppDeps = request.app["deps"]
    bot = request.app["bot"]
    user, user_id = await _require_user(request)
    ad_id = request.match_info["ad_id"]
    ad = await deps.advert_service.get_ad(ad_id)
    if not ad or not ad.active:
        raise web.HTTPNotFound(text="Объявление недоступно")
    if ad.owner_id == user_id:
        raise web.HTTPBadRequest(text="Нельзя создать сделку по своему объявлению")
    if not await deps.advert_service.trading_enabled(ad.owner_id):
        raise web.HTTPBadRequest(text="Объявление недоступно")
    try:
        body = await request.json()
    except Exception:
        raise web.HTTPBadRequest(text="Invalid JSON")
    try:
        rub_amount = Decimal(str(body.get("rub_amount")))
    except (InvalidOperation, TypeError):
        raise web.HTTPBadRequest(text="Некорректная сумма")
    bank = (body.get("bank") or "").strip()
    if rub_amount < ad.min_rub or rub_amount > ad.max_rub:
        raise web.HTTPBadRequest(text="Сумма должна быть в пределах лимитов объявления")
    if ad.banks:
        if not bank:
            raise web.HTTPBadRequest(text="Выберите банкомат")
        if bank not in ad.banks:
            raise web.HTTPBadRequest(text="Некорректный банкомат")
    base_usdt = rub_amount / ad.price_rub
    if ad.side == AdvertSide.SELL:
        seller_id = ad.owner_id
        buyer_id = user_id
    else:
        seller_id = user_id
        buyer_id = ad.owner_id
    seller_balance = await deps.deal_service.balance_of(seller_id)
    available = min(ad.remaining_usdt, seller_balance)
    if base_usdt > available:
        raise web.HTTPBadRequest(text="В объявлении недостаточно объёма")
    try:
        deal = await deps.deal_service.create_p2p_offer(
            seller_id=seller_id,
            buyer_id=buyer_id,
            initiator_id=user_id,
            usd_amount=rub_amount,
            rate=ad.price_rub,
            atm_bank=bank if ad.banks else None,
            advert_id=ad.id,
            comment=ad.terms,
        )
        await deps.advert_service.reduce_volume(ad.id, base_usdt)
    except Exception as exc:
        raise web.HTTPBadRequest(text=f"Не удалось создать предложение: {exc}")
    offer_text = (
        f"🆕 Новая сделка\n"
        f"Объявление: {ad.public_id}\n"
        f"Сумма: ₽{rub_amount}\n"
        f"USDT: {deal.usdt_amount.quantize(Decimal('0.001'))}\n"
        f"Сделка: {deal.hashtag}\n\n"
        "Перейдите в приложение для обработки сделки."
    )
    if buyer_id != user_id:
        markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="✅ Принять", callback_data=f"p2p:offer:accept:{deal.id}"),
                    InlineKeyboardButton(text="❌ Отклонить", callback_data=f"p2p:offer:decline:{deal.id}"),
                ],
                [InlineKeyboardButton(text="К сделке", callback_data=f"deal_info:{deal.id}")],
            ]
        )
        await bot.send_message(buyer_id, offer_text, reply_markup=markup)
    await bot.send_message(
        user_id,
        f"✅ Предложение отправлено.\nОжидаем принятия по сделке {deal.hashtag}.",
    )
    payload = await _deal_payload(deps, deal, user_id, with_actions=True, request=request)
    return web.json_response({"ok": True, "deal": payload})


async def _api_disputes_summary(request: web.Request) -> web.Response:
    deps: AppDeps = request.app["deps"]
    _, user_id = await _require_user(request)
    can_access = await _has_dispute_access(user_id, deps)
    if not can_access:
        return web.json_response({"ok": True, "can_access": False, "count": 0})
    await _ensure_disputes_for_opened(deps)
    disputes = await deps.dispute_service.list_open_disputes_for(user_id)
    return web.json_response({"ok": True, "can_access": True, "count": len(disputes)})


async def _api_disputes_list(request: web.Request) -> web.Response:
    deps: AppDeps = request.app["deps"]
    _, user_id = await _require_user(request)
    if not await _has_dispute_access(user_id, deps):
        raise web.HTTPForbidden(text="Нет доступа")
    await _ensure_disputes_for_opened(deps)
    disputes = await deps.dispute_service.list_open_disputes_for(user_id)
    payload = []
    for item in disputes:
        deal = await deps.deal_service.get_deal(item.deal_id)
        if not deal:
            continue
        payload.append(
            {
                "id": item.id,
                "deal_id": item.deal_id,
                "public_id": deal.public_id,
                "opened_at": item.opened_at.isoformat(),
                "opened_by": item.opened_by,
                "assigned_to": item.assigned_to,
                "reason": item.reason,
                "resolved": item.resolved,
            }
        )
    return web.json_response({"ok": True, "disputes": payload})


async def _api_dispute_detail(request: web.Request) -> web.Response:
    deps: AppDeps = request.app["deps"]
    user, user_id = await _require_user(request)
    if not await _has_dispute_access(user_id, deps):
        raise web.HTTPForbidden(text="Нет доступа")
    dispute_id = request.match_info["dispute_id"]
    dispute = await deps.dispute_service.dispute_by_id(dispute_id)
    if not dispute:
        raise web.HTTPNotFound(text="Спор не найден")
    deal = await deps.deal_service.get_deal(dispute.deal_id)
    if not deal:
        raise web.HTTPNotFound(text="Сделка не найдена")
    seller = await deps.user_service.profile_of(deal.seller_id)
    buyer = await deps.user_service.profile_of(deal.buyer_id) if deal.buyer_id else None
    opener = await deps.user_service.profile_of(dispute.opened_by) if dispute.opened_by else None
    include_private = _is_admin(user_id, deps)
    can_manage = await _has_dispute_access(user_id, deps)
    def _display_name(profile, fallback: int | str | None = None) -> str:
        if not profile:
            return str(fallback or "—")
        return (
            profile.display_name
            or profile.full_name
            or profile.username
            or str(getattr(profile, "user_id", fallback or "—"))
        )
    author_ids = {item.author_id for item in dispute.evidence if item.author_id}
    author_profiles = {}
    for author_id in author_ids:
        author_profiles[author_id] = await deps.user_service.profile_of(author_id)
    evidence = []
    for item in dispute.evidence:
        file_url = await _file_url(request, item.file_id)
        evidence.append(
            {
                "kind": item.kind,
                "file_id": item.file_id,
                "author_id": item.author_id,
                "author_name": _display_name(author_profiles.get(item.author_id), item.author_id),
                "url": file_url,
            }
        )
    payload = {
        "id": dispute.id,
        "deal_id": dispute.deal_id,
        "opened_at": dispute.opened_at.isoformat(),
        "opened_by": dispute.opened_by,
        "reason": dispute.reason,
        "comment": dispute.comment,
        "opened_by_name": _display_name(opener, dispute.opened_by),
        "assigned_to": dispute.assigned_to,
        "can_manage": can_manage,
        "messages": [
            {
                "author_id": msg.author_id,
                "author_name": _display_name(
                    await deps.user_service.profile_of(msg.author_id), msg.author_id
                ),
                "text": msg.text,
                "created_at": msg.created_at.isoformat(),
            }
            for msg in dispute.messages
        ],
        "evidence": evidence,
        "deal": await _deal_payload(deps, deal, user_id, with_actions=False, request=request),
        "seller": _profile_payload(seller, request=request, include_private=include_private),
        "buyer": _profile_payload(buyer, request=request, include_private=include_private),
    }
    return web.json_response({"ok": True, "dispute": payload})


async def _api_dispute_assign(request: web.Request) -> web.Response:
    deps: AppDeps = request.app["deps"]
    _, user_id = await _require_user(request)
    if not await _has_dispute_access(user_id, deps):
        raise web.HTTPForbidden(text="Нет доступа")
    dispute_id = request.match_info["dispute_id"]
    try:
        dispute = await deps.dispute_service.assign(dispute_id, user_id)
    except ValueError as exc:
        raise web.HTTPBadRequest(text=str(exc))
    except LookupError:
        raise web.HTTPNotFound(text="Спор не найден")
    deal = await deps.deal_service.get_deal(dispute.deal_id)
    if deal:
        profile = await deps.user_service.profile_of(user_id)
        name = (
            profile.display_name
            if profile and profile.display_name
            else profile.full_name
            if profile and profile.full_name
            else profile.username
            if profile and profile.username
            else str(user_id)
        )
        await deps.chat_service.add_message(
            deal_id=deal.id,
            sender_id=0,
            text=f"Модератор {name} подключен к чату",
            file_path=None,
            file_name=None,
            system=True,
        )
    return web.json_response({"ok": True, "dispute_id": dispute.id, "assigned_to": dispute.assigned_to})


async def _api_dispute_resolve(request: web.Request) -> web.Response:
    deps: AppDeps = request.app["deps"]
    _, user_id = await _require_user(request)
    if not await _has_dispute_access(user_id, deps):
        raise web.HTTPForbidden(text="Нет доступа")
    dispute_id = request.match_info["dispute_id"]
    dispute = await deps.dispute_service.dispute_by_id(dispute_id)
    if not dispute:
        raise web.HTTPNotFound(text="Спор не найден")
    deal = await deps.deal_service.get_deal(dispute.deal_id)
    if not deal:
        raise web.HTTPNotFound(text="Сделка не найдена")
    try:
        body = await request.json()
    except Exception:
        raise web.HTTPBadRequest(text="Invalid JSON")
    try:
        seller_amount = Decimal(str(body.get("seller_amount", "0")))
        buyer_amount = Decimal(str(body.get("buyer_amount", "0")))
    except InvalidOperation:
        raise web.HTTPBadRequest(text="Некорректные суммы")
    if seller_amount < 0 or buyer_amount < 0:
        raise web.HTTPBadRequest(text="Сумма не может быть отрицательной")
    if seller_amount + buyer_amount > deal.usdt_amount:
        raise web.HTTPBadRequest(text="Сумма превышает объем сделки")
    await deps.deal_service.resolve_dispute(
        deal.id, seller_amount=seller_amount, buyer_amount=buyer_amount
    )
    await deps.dispute_service.resolve_dispute(
        dispute_id, resolved_by=user_id, seller_amount=str(seller_amount), buyer_amount=str(buyer_amount)
    )
    with suppress(Exception):
        seller_profile = await deps.user_service.profile_of(deal.seller_id)
        buyer_profile = await deps.user_service.profile_of(deal.buyer_id) if deal.buyer_id else None
        seller_name = (
            seller_profile.display_name
            if seller_profile and seller_profile.display_name
            else seller_profile.full_name
            if seller_profile and seller_profile.full_name
            else seller_profile.username
            if seller_profile and seller_profile.username
            else str(deal.seller_id)
        )
        buyer_name = (
            buyer_profile.display_name
            if buyer_profile and buyer_profile.display_name
            else buyer_profile.full_name
            if buyer_profile and buyer_profile.full_name
            else buyer_profile.username
            if buyer_profile and buyer_profile.username
            else str(deal.buyer_id or "")
        )
        seller_amount_text = f"{seller_amount.quantize(Decimal('0.001')):f}"
        buyer_amount_text = f"{buyer_amount.quantize(Decimal('0.001')):f}"
        winner_is_seller = seller_amount >= buyer_amount
        winner_name = seller_name if winner_is_seller else buyer_name
        if deal.seller_id:
            if seller_amount > 0:
                await request.app["bot"].send_message(
                    deal.seller_id,
                    f"✅ Сделка #{deal.public_id} была закрыта в вашу пользу.\n"
                    f"На баланс было зачислено {seller_amount_text} USDT.",
                )
            else:
                await request.app["bot"].send_message(
                    deal.seller_id,
                    f"Сделка #{deal.public_id} была закрыта в пользу {winner_name}.\n"
                    f"Средства отправлены {winner_name}.",
                )
        if deal.buyer_id:
            if buyer_amount > 0:
                await request.app["bot"].send_message(
                    deal.buyer_id,
                    f"✅ Сделка #{deal.public_id} была закрыта в вашу пользу.\n"
                    f"На баланс было зачислено {buyer_amount_text} USDT.",
                )
            else:
                await request.app["bot"].send_message(
                    deal.buyer_id,
                    f"Сделка #{deal.public_id} была закрыта в пользу {winner_name}.\n"
                    f"Средства отправлены {winner_name}.",
                )
    with suppress(Exception):
        await deps.chat_service.purge_chat(deal.id)
    with suppress(Exception):
        chat_dir = _chat_dir(deps) / deal.id
        shutil.rmtree(chat_dir, ignore_errors=True)
    with suppress(Exception):
        evidence_dir = _dispute_dir(deps) / dispute_id
        shutil.rmtree(evidence_dir, ignore_errors=True)
    return web.json_response({"ok": True})


async def _api_dispute_evidence_upload(request: web.Request) -> web.Response:
    deps: AppDeps = request.app["deps"]
    _, user_id = await _require_user(request)
    dispute_id = request.match_info["dispute_id"]
    dispute = await deps.dispute_service.dispute_by_id(dispute_id)
    if not dispute:
        raise web.HTTPNotFound(text="Спор не найден")
    deal = await deps.deal_service.get_deal(dispute.deal_id)
    if not deal:
        raise web.HTTPNotFound(text="Сделка не найдена")
    if user_id not in {deal.seller_id, deal.buyer_id} and not await _has_dispute_access(user_id, deps):
        raise web.HTTPForbidden(text="Нет доступа")
    reader = await request.multipart()
    field = await reader.next()
    if not field or field.name != "file":
        raise web.HTTPBadRequest(text="Файл не найден")
    filename = Path(field.filename or "evidence").name
    evidence_dir = _dispute_dir(deps) / dispute_id
    evidence_dir.mkdir(parents=True, exist_ok=True)
    file_path = evidence_dir / filename
    with file_path.open("wb") as handle:
        while True:
            chunk = await field.read_chunk()
            if not chunk:
                break
            handle.write(chunk)
    lower_name = filename.lower()
    if lower_name.endswith((".mp4", ".mov", ".m4v", ".webm", ".avi", ".mkv")):
        kind = "video"
    elif lower_name.endswith((".png", ".jpg", ".jpeg", ".webp", ".gif")):
        kind = "photo"
    else:
        kind = "document"
    await deps.dispute_service.append_evidence(
        dispute_id,
        EvidenceItem(kind=kind, file_id=f"web:{dispute_id}/{filename}", author_id=user_id),
    )
    return web.json_response({"ok": True})


async def _api_dispute_message(request: web.Request) -> web.Response:
    deps: AppDeps = request.app["deps"]
    _, user_id = await _require_user(request)
    dispute_id = request.match_info["dispute_id"]
    dispute = await deps.dispute_service.dispute_by_id(dispute_id)
    if not dispute:
        raise web.HTTPNotFound(text="Спор не найден")
    deal = await deps.deal_service.get_deal(dispute.deal_id)
    if not deal:
        raise web.HTTPNotFound(text="Сделка не найдена")
    if user_id not in {deal.seller_id, deal.buyer_id} and not await _has_dispute_access(user_id, deps):
        raise web.HTTPForbidden(text="Нет доступа")
    try:
        body = await request.json()
    except Exception:
        raise web.HTTPBadRequest(text="Invalid JSON")
    text = (body.get("text") or "").strip()
    if not text:
        raise web.HTTPBadRequest(text="Пустое сообщение")
    await deps.dispute_service.append_message(dispute_id, user_id, text)
    return web.json_response({"ok": True})


async def _api_dispute_file(request: web.Request) -> web.Response:
    deps: AppDeps = request.app["deps"]
    _, user_id = await _require_user(request)
    dispute_id = request.match_info["dispute_id"]
    filename = request.match_info["filename"]
    dispute = await deps.dispute_service.dispute_by_id(dispute_id)
    if not dispute:
        raise web.HTTPNotFound(text="Спор не найден")
    deal = await deps.deal_service.get_deal(dispute.deal_id)
    if not deal:
        raise web.HTTPNotFound(text="Сделка не найдена")
    if user_id not in {deal.seller_id, deal.buyer_id} and not await _has_dispute_access(user_id, deps):
        raise web.HTTPForbidden(text="Нет доступа")
    base_dir = _dispute_dir(deps).resolve()
    path = (base_dir / dispute_id / filename).resolve()
    if base_dir not in path.parents or not path.exists():
        raise web.HTTPNotFound()
    return web.FileResponse(path)


async def _api_admin_summary(request: web.Request) -> web.Response:
    deps: AppDeps = request.app["deps"]
    _, user_id = await _require_user(request)
    if not _is_admin(user_id, deps):
        return web.json_response({"ok": True, "can_access": False})
    return web.json_response({"ok": True, "can_access": True})


async def _api_admin_settings(request: web.Request) -> web.Response:
    deps: AppDeps = request.app["deps"]
    _, user_id = await _require_user(request)
    if not _is_admin(user_id, deps):
        raise web.HTTPForbidden(text="Нет доступа")
    rate = await deps.rate_provider.snapshot()
    withdraw_fee = await deps.rate_provider.withdraw_fee_percent()
    return web.json_response(
        {
            "ok": True,
            "usd_rate": str(rate.usd_rate),
            "fee_percent": str(rate.fee_percent),
            "withdraw_fee_percent": str(withdraw_fee),
        }
    )


async def _api_admin_settings_update(request: web.Request) -> web.Response:
    deps: AppDeps = request.app["deps"]
    _, user_id = await _require_user(request)
    if not _is_admin(user_id, deps):
        raise web.HTTPForbidden(text="Нет доступа")
    try:
        body = await request.json()
    except Exception:
        raise web.HTTPBadRequest(text="Invalid JSON")
    usd_rate = body.get("usd_rate")
    fee_percent = body.get("fee_percent")
    withdraw_fee = body.get("withdraw_fee_percent")
    rate_value = _parse_optional_decimal(usd_rate)
    fee_value = _parse_optional_decimal(fee_percent)
    withdraw_value = _parse_optional_decimal(withdraw_fee)
    if rate_value is not None or fee_value is not None:
        await deps.rate_provider.set_rate(rate_value, fee_value)
    if withdraw_value is not None:
        await deps.rate_provider.set_withdraw_fee_percent(withdraw_value)
    return await _api_admin_settings(request)


async def _api_admin_moderators(request: web.Request) -> web.Response:
    deps: AppDeps = request.app["deps"]
    _, user_id = await _require_user(request)
    if not _is_admin(user_id, deps):
        raise web.HTTPForbidden(text="Нет доступа")
    mods = await deps.user_service.list_moderators()
    payload = []
    for mod_id in mods:
        profile = await deps.user_service.profile_of(mod_id)
        resolved = await deps.dispute_service.count_resolved_by(mod_id)
        payload.append(
            {
                "user_id": mod_id,
                "profile": _profile_payload(profile, request=request, include_private=True),
                "resolved": resolved,
            }
        )
    return web.json_response({"ok": True, "moderators": payload})


async def _api_admin_add_moderator(request: web.Request) -> web.Response:
    deps: AppDeps = request.app["deps"]
    _, user_id = await _require_user(request)
    if not _is_admin(user_id, deps):
        raise web.HTTPForbidden(text="Нет доступа")
    try:
        body = await request.json()
    except Exception:
        raise web.HTTPBadRequest(text="Invalid JSON")
    username = str(body.get("username") or "").strip()
    if not username:
        raise web.HTTPBadRequest(text="Нужно указать username")
    profile = await deps.user_service.profile_by_username(username)
    if not profile:
        raise web.HTTPNotFound(text="Пользователь не найден")
    await deps.user_service.add_moderator(profile.user_id)
    return web.json_response({"ok": True, "user_id": profile.user_id})


async def _api_admin_remove_moderator(request: web.Request) -> web.Response:
    deps: AppDeps = request.app["deps"]
    _, user_id = await _require_user(request)
    if not _is_admin(user_id, deps):
        raise web.HTTPForbidden(text="Нет доступа")
    target = int(request.match_info["user_id"])
    await deps.user_service.remove_moderator(target)
    return web.json_response({"ok": True})


async def _api_admin_merchants(request: web.Request) -> web.Response:
    deps: AppDeps = request.app["deps"]
    _, user_id = await _require_user(request)
    if not _is_admin(user_id, deps):
        raise web.HTTPForbidden(text="Нет доступа")
    merchants = await deps.user_service.list_merchants()
    payload = []
    for rec in merchants:
        stats = await _merchant_stats(deps, rec.user_id)
        payload.append(
            {
                "user_id": rec.user_id,
                "profile": _profile_payload(rec.profile, request=request, include_private=True),
                "merchant_since": rec.merchant_since.isoformat() if rec.merchant_since else None,
                "stats": stats,
            }
        )
    return web.json_response({"ok": True, "merchants": payload})


async def _api_admin_merchant_revoke(request: web.Request) -> web.Response:
    deps: AppDeps = request.app["deps"]
    _, user_id = await _require_user(request)
    if not _is_admin(user_id, deps):
        raise web.HTTPForbidden(text="Нет доступа")
    target = int(request.match_info["user_id"])
    from cachebot.models.user import UserRole

    await deps.user_service.set_role(target, UserRole.SELLER, revoke_merchant=True)
    return web.json_response({"ok": True})


async def _api_reviews_list(request: web.Request) -> web.Response:
    deps: AppDeps = request.app["deps"]
    _, user_id = await _require_user(request)
    target_id = user_id
    raw_target = request.query.get("user_id")
    if raw_target:
        try:
            target_id = int(raw_target)
        except ValueError:
            raise web.HTTPBadRequest(text="Некорректный user_id")
    reviews = await deps.review_service.list_for_user(target_id)
    reviews.sort(key=lambda item: item.created_at, reverse=True)
    payload = []
    for item in reviews:
        author = await deps.user_service.profile_of(item.from_user_id)
        payload.append(
            {
                "deal_id": item.deal_id,
                "rating": item.rating,
                "comment": item.comment,
                "created_at": item.created_at.isoformat(),
                "author": _profile_payload(author, request=request, include_private=False),
            }
        )
    positive = sum(1 for item in reviews if item.rating > 0)
    negative = sum(1 for item in reviews if item.rating < 0)
    return web.json_response(
        {"ok": True, "reviews": payload, "positive": positive, "negative": negative}
    )


async def _api_reviews_add(request: web.Request) -> web.Response:
    deps: AppDeps = request.app["deps"]
    _, user_id = await _require_user(request)
    try:
        body = await request.json()
    except Exception:
        raise web.HTTPBadRequest(text="Invalid JSON")
    deal_id = str(body.get("deal_id") or "").strip()
    rating = body.get("rating")
    comment = (body.get("comment") or "").strip()
    if not deal_id:
        raise web.HTTPBadRequest(text="deal_id required")
    if rating not in (-1, 1):
        raise web.HTTPBadRequest(text="rating must be -1 or 1")
    deal = await deps.deal_service.get_deal(deal_id)
    if not deal:
        raise web.HTTPNotFound(text="Сделка не найдена")
    if deal.status != DealStatus.COMPLETED:
        raise web.HTTPBadRequest(text="Сделка не завершена")
    if user_id not in {deal.seller_id, deal.buyer_id}:
        raise web.HTTPForbidden(text="Нет доступа")
    target_id = deal.buyer_id if user_id == deal.seller_id else deal.seller_id
    if not target_id:
        raise web.HTTPBadRequest(text="Контрагент не найден")
    try:
        review = await deps.review_service.add_review(
            deal_id=deal_id,
            from_user_id=user_id,
            to_user_id=target_id,
            rating=int(rating),
            comment=comment or None,
        )
    except ValueError as exc:
        return web.json_response({"ok": False, "error": str(exc)}, status=409)
    try:
        author_profile = await deps.user_service.profile_of(user_id)
        author_name = (
            author_profile.display_name if author_profile else str(user_id)
        )
    except Exception:
        author_name = str(user_id)
    deal_label = deal.public_id or deal.id
    mark = "👍" if int(rating) > 0 else "👎"
    lines = [
        f"⭐ Новый отзыв {mark}",
        f"Сделка: #{deal_label}",
        f"От: {author_name}",
    ]
    if comment:
        lines.append(f"Комментарий: {comment}")
    text = "\n".join(lines)
    with suppress(Exception):
        await request.app["bot"].send_message(target_id, text)
    return web.json_response({"ok": True, "review": review.to_dict()})


def _validate_init_data(init_data: str, bot_token: str) -> dict[str, Any] | None:
    try:
        pairs = parse_qsl(init_data, keep_blank_values=True)
    except Exception:
        return None
    data = dict(pairs)
    received_hash = data.pop("hash", "")
    data.pop("signature", None)
    if not received_hash:
        return None
    data_check_sorted = "\n".join(f"{k}={v}" for k, v in sorted(data.items()))
    raw_pairs = [(k, v) for k, v in pairs if k not in {"hash", "signature"}]
    data_check_raw = "\n".join(f"{k}={v}" for k, v in raw_pairs)
    raw_items = []
    for chunk in init_data.split("&"):
        if not chunk:
            continue
        key, _, value = chunk.partition("=")
        if key in {"hash", "signature"}:
            continue
        raw_items.append((key, value))
    data_check_raw_unsorted = "\n".join(f"{k}={v}" for k, v in raw_items)
    data_check_raw_sorted = "\n".join(f"{k}={v}" for k, v in sorted(raw_items))
    webapp_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()

    def _hashes(data_check: str) -> tuple[str, str, str]:
        expected = hmac.new(webapp_key, data_check.encode(), hashlib.sha256).hexdigest()
        legacy = hmac.new(hashlib.sha256(bot_token.encode()).digest(), data_check.encode(), hashlib.sha256).hexdigest()
        legacy_plain = hmac.new(bot_token.encode(), data_check.encode(), hashlib.sha256).hexdigest()
        return expected, legacy, legacy_plain

    expected_hash, legacy_hash, legacy_plain = _hashes(data_check_sorted)
    if not (
        hmac.compare_digest(received_hash, expected_hash)
        or hmac.compare_digest(received_hash, legacy_hash)
        or hmac.compare_digest(received_hash, legacy_plain)
    ):
        raw_expected, raw_legacy, raw_plain = _hashes(data_check_raw)
        raw_unsorted_expected, raw_unsorted_legacy, raw_unsorted_plain = _hashes(
            data_check_raw_unsorted
        )
        raw_sorted_expected, raw_sorted_legacy, raw_sorted_plain = _hashes(data_check_raw_sorted)
        if not (
            hmac.compare_digest(received_hash, raw_expected)
            or hmac.compare_digest(received_hash, raw_legacy)
            or hmac.compare_digest(received_hash, raw_plain)
            or hmac.compare_digest(received_hash, raw_unsorted_expected)
            or hmac.compare_digest(received_hash, raw_unsorted_legacy)
            or hmac.compare_digest(received_hash, raw_unsorted_plain)
            or hmac.compare_digest(received_hash, raw_sorted_expected)
            or hmac.compare_digest(received_hash, raw_sorted_legacy)
            or hmac.compare_digest(received_hash, raw_sorted_plain)
        ):
            logger.warning(
                "Invalid initData hash: received=%s expected=%s legacy=%s keys=%s",
                received_hash[:12],
                expected_hash[:12],
                legacy_hash[:12],
                ",".join(sorted(data.keys())),
            )
            return None
    try:
        user_raw = data.get("user")
        return json.loads(user_raw) if user_raw else {}
    except Exception:
        return {}


async def _require_user(request: web.Request) -> tuple[dict[str, Any], int]:
    deps: AppDeps = request.app["deps"]
    init_data = request.headers.get("X-Telegram-Init-Data") or request.query.get("initData")
    if not init_data:
        raise web.HTTPUnauthorized(text="Missing initData")
    user = _validate_init_data(init_data, deps.config.telegram_bot_token)
    if not user and deps.config.allow_unsafe_initdata:
        try:
            pairs = parse_qsl(init_data, keep_blank_values=True)
            data = dict(pairs)
            user_raw = data.get("user")
            user = json.loads(user_raw) if user_raw else {}
            if user:
                logger.warning("Unsafe initData accepted for user_id=%s", user.get("id"))
        except Exception:
            user = None
    if not user or "id" not in user:
        raise web.HTTPUnauthorized(text="Invalid initData")
    full_name = " ".join(
        part for part in [user.get("first_name"), user.get("last_name")] if part
    ) or None
    await deps.user_service.ensure_profile(
        int(user["id"]),
        full_name=full_name,
        username=user.get("username"),
    )
    return user, int(user["id"])


async def _has_dispute_access(user_id: int, deps: AppDeps) -> bool:
    if user_id in deps.config.admin_ids:
        return True
    return await deps.user_service.is_moderator(user_id)


def _avatar_dir(deps: AppDeps) -> Path:
    return Path(deps.config.storage_path).parent / "avatars"


def _chat_dir(deps: AppDeps) -> Path:
    return Path(deps.config.storage_path).parent / "chat"


def _qr_logo_path() -> Path:
    return Path(__file__).resolve().parents[1] / "bc-logo.png"

def _trim_logo(logo: Image.Image) -> Image.Image:
    try:
        rgba = logo.convert("RGBA")
        if "A" in rgba.getbands():
            bbox = rgba.split()[-1].getbbox()
            if bbox:
                return rgba.crop(bbox)
        bg = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
        diff = ImageChops.difference(rgba, bg)
        diff = ImageChops.add(diff, diff, 2.0, -10)
        bbox = diff.getbbox()
        if bbox:
            return rgba.crop(bbox)
        return rgba
    except Exception:
        return logo

def _apply_qr_logo(image: Image.Image) -> Image.Image:
    try:
        logo_path = _qr_logo_path()
        if not logo_path.exists():
            return image
        logo = Image.open(logo_path).convert("RGBA")
        logo = _trim_logo(logo)
        qr = image.convert("RGBA")
        qr_w, qr_h = qr.size
        logo_box = int(min(qr_w, qr_h) * 0.26)
        logo.thumbnail((logo_box, logo_box), Image.Resampling.LANCZOS)
        logo_w, logo_h = logo.size

        pad = max(6, int(logo_box * 0.16))
        box_w = logo_w + pad * 2
        box_h = logo_h + pad * 2
        mask = Image.new("L", (box_w, box_h), 0)
        draw = ImageDraw.Draw(mask)
        radius = int(min(box_w, box_h) * 0.48)
        draw.rounded_rectangle((0, 0, box_w, box_h), radius=radius, fill=255)
        box = Image.new("RGBA", (box_w, box_h), (255, 255, 255, 255))
        box.putalpha(mask)
        box_pos = ((box_w - logo_w) // 2, (box_h - logo_h) // 2)
        box.alpha_composite(logo, dest=box_pos)

        pos = ((qr_w - box_w) // 2, (qr_h - box_h) // 2)
        qr.alpha_composite(box, dest=pos)
        return qr
    except Exception:
        return image


def _apply_rounded_eyes(img: Image.Image, qr) -> Image.Image:
    try:
        box = int(getattr(qr, "box_size", 12))
        border = int(getattr(qr, "border", 2))
        count = int(getattr(qr, "modules_count", 0))
        if not count:
            return img
        draw = ImageDraw.Draw(img)
        outer = 7 * box
        inner = 5 * box
        center = 3 * box
        base_radius = max(2, int(box * 1.2))

        def draw_eye(x, y):
            x0 = (border + x) * box
            y0 = (border + y) * box
            # clear to white to remove square frame
            draw.rectangle((x0, y0, x0 + outer, y0 + outer), fill=(255, 255, 255))
            # rounded outer
            draw.rounded_rectangle(
                (x0, y0, x0 + outer, y0 + outer),
                radius=min(base_radius, int(outer / 2)),
                fill=(0, 0, 0),
            )
            # rounded inner
            draw.rounded_rectangle(
                (x0 + box, y0 + box, x0 + box + inner, y0 + box + inner),
                radius=min(base_radius, int(inner / 2)),
                fill=(255, 255, 255),
            )
            # rounded center
            draw.rounded_rectangle(
                (x0 + 2 * box, y0 + 2 * box, x0 + 2 * box + center, y0 + 2 * box + center),
                radius=min(base_radius, int(center / 2)),
                fill=(0, 0, 0),
            )

        draw_eye(0, 0)
        draw_eye(count - 7, 0)
        draw_eye(0, count - 7)
        return img
    except Exception:
        return img

def _qr_dir(deps: AppDeps) -> Path:
    return Path(deps.config.storage_path).parent / "qr"


def _dispute_dir(deps: AppDeps) -> Path:
    return Path(deps.config.storage_path).parent / "disputes"


async def _ensure_disputes_for_opened(deps: AppDeps) -> None:
    deals = await deps.deal_service.list_dispute_deals()
    for deal in deals:
        existing = await deps.dispute_service.dispute_for_deal(deal.id)
        if existing:
            continue
        opener_id = deal.dispute_opened_by or deal.seller_id or deal.buyer_id or 0
        await deps.dispute_service.open_dispute(
            deal_id=deal.id,
            opened_by=opener_id,
            reason="Открыт через WebApp",
            comment=None,
            evidence=[],
        )


def _chat_file_url(request: web.Request, msg) -> str | None:
    if not msg.file_path or not msg.file_name:
        return None
    query = {}
    init_data = request.headers.get("X-Telegram-Init-Data")
    if init_data:
        query["initData"] = init_data
    return str(
        request.url.with_path(f"/api/chat-files/{msg.deal_id}/{msg.file_name}").with_query(query)
    )


def _avatar_url(request: web.Request, profile) -> str | None:
    if not profile or not getattr(profile, "avatar_path", None):
        return None
    return str(request.url.with_path(f"/api/avatar/{profile.user_id}").with_query({}))


def _profile_payload(
    profile, *, request: web.Request | None = None, include_private: bool = False
) -> dict[str, Any] | None:
    if not profile:
        return None
    payload = {
        "user_id": profile.user_id,
        "display_name": getattr(profile, "display_name", None),
        "avatar_url": _avatar_url(request, profile) if request else None,
        "registered_at": profile.registered_at.isoformat(),
        "last_seen_at": profile.last_seen_at.isoformat() if profile.last_seen_at else None,
    }
    if include_private:
        payload["full_name"] = profile.full_name
        payload["username"] = profile.username
    return payload


def _parse_decimal(value, *, fallback: Decimal | None = None) -> Decimal:
    if value is None:
        if fallback is None:
            raise InvalidOperation
        return fallback
    return Decimal(str(value))


def _parse_ad_values(payload: dict[str, Any]) -> tuple[
    AdvertSide, Decimal, Decimal, Decimal, Decimal, list[str], str | None
] | None:
    try:
        side = AdvertSide(payload.get("side", "sell"))
        total_usdt = Decimal(str(payload.get("total_usdt")))
        price_rub = Decimal(str(payload.get("price_rub")))
        min_rub = Decimal(str(payload.get("min_rub")))
        max_rub = Decimal(str(payload.get("max_rub")))
        banks = list(payload.get("banks") or [])
        terms = (payload.get("terms") or None) if str(payload.get("terms") or "").strip() else None
    except (InvalidOperation, ValueError, TypeError):
        return None
    if not banks:
        return None
    if min_rub <= 0 or max_rub <= 0 or min_rub > max_rub:
        return None
    if total_usdt <= 0 or price_rub <= 0:
        return None
    return side, total_usdt, price_rub, min_rub, max_rub, banks, terms


def _validate_ad_limits(
    total_usdt: Decimal, price_rub: Decimal, min_rub: Decimal, max_rub: Decimal
) -> None:
    max_possible = total_usdt * price_rub
    if max_possible > 0 and (max_rub > max_possible or min_rub > max_possible):
        raise web.HTTPBadRequest(
            text="Не хватает объёма для такого лимита. Введите меньшее значение."
        )


def _parse_optional_decimal(value) -> Decimal | None:
    if value is None or value == "":
        return None
    return Decimal(str(value))


def _is_admin(user_id: int, deps: AppDeps) -> bool:
    return user_id in deps.config.admin_ids


async def _merchant_stats(deps: AppDeps, user_id: int) -> dict[str, int]:
    deals = await deps.deal_service.list_user_deals(user_id)
    total = 0
    completed = 0
    canceled = 0
    for deal in deals:
        if deal.buyer_id != user_id:
            continue
        total += 1
        if deal.status.value == "completed":
            completed += 1
        if deal.status.value in {"canceled", "expired"}:
            canceled += 1
    return {"total": total, "completed": completed, "canceled": canceled}


async def _ensure_ad_availability(
    deps: AppDeps, ad
) -> tuple[Any, Decimal]:
    balance = await deps.deal_service.balance_of(ad.owner_id)
    available = min(ad.remaining_usdt, balance)
    max_possible = available * ad.price_rub
    should_deactivate = available <= 0 or ad.min_rub > max_possible
    if ad.active and should_deactivate:
        ad = await deps.advert_service.update_ad(ad.id, active=False)
    return ad, available


async def _ad_payload(
    deps: AppDeps,
    ad,
    *,
    include_owner: bool = True,
    available_usdt: Decimal | None = None,
    request: web.Request | None = None,
) -> dict[str, Any]:
    owner = await deps.user_service.profile_of(ad.owner_id) if include_owner else None
    remaining = available_usdt if available_usdt is not None else ad.remaining_usdt
    return {
        "id": ad.id,
        "public_id": ad.public_id,
        "side": ad.side.value,
        "price_rub": str(ad.price_rub),
        "total_usdt": str(ad.total_usdt),
        "remaining_usdt": str(remaining),
        "min_rub": str(ad.min_rub),
        "max_rub": str(ad.max_rub),
        "banks": list(ad.banks),
        "terms": ad.terms,
        "active": ad.active,
        "created_at": ad.created_at.isoformat(),
        "owner": _profile_payload(owner, request=request, include_private=False) if include_owner else None,
    }


async def _file_url(request: web.Request, file_id: str) -> str | None:
    if not file_id:
        return None
    if file_id.startswith("web:"):
        payload = file_id[len("web:") :]
        if "/" not in payload:
            return None
        dispute_id, filename = payload.split("/", 1)
        query = {}
        init_data = request.headers.get("X-Telegram-Init-Data")
        if init_data:
            query["initData"] = init_data
        return str(
            request.url.with_path(f"/api/dispute-files/{dispute_id}/{filename}").with_query(query)
        )
    bot = request.app["bot"]
    deps: AppDeps = request.app["deps"]
    try:
        file = await bot.get_file(file_id)
    except Exception:
        return None
    return f"https://api.telegram.org/file/bot{deps.config.telegram_bot_token}/{file.file_path}"


async def _deal_payload(
    deps: AppDeps,
    deal,
    user_id: int,
    *,
    with_actions: bool = False,
    request: web.Request | None = None,
) -> dict[str, Any]:
    role = "seller" if deal.seller_id == user_id else "buyer"
    counterparty_id = deal.buyer_id if role == "seller" else deal.seller_id
    counterparty = await deps.user_service.profile_of(counterparty_id) if counterparty_id else None
    payload = {
        "id": deal.id,
        "public_id": deal.public_id,
        "status": deal.status.value,
        "qr_stage": deal.qr_stage.value,
        "seller_id": deal.seller_id,
        "buyer_id": deal.buyer_id,
        "role": role,
        "cash_rub": str(deal.usd_amount),
        "usd_amount": str(deal.usd_amount),
        "usdt_amount": str(deal.usdt_amount),
        "rate": str(deal.rate),
        "created_at": deal.created_at.isoformat(),
        "atm_bank": deal.atm_bank,
        "counterparty": _profile_payload(counterparty, request=request, include_private=False),
        "is_p2p": deal.is_p2p,
        "buyer_cash_confirmed": deal.buyer_cash_confirmed,
        "seller_cash_confirmed": deal.seller_cash_confirmed,
        "offer_initiator_id": deal.offer_initiator_id,
        "offer_expires_at": deal.offer_expires_at.isoformat() if deal.offer_expires_at else None,
        "dispute_available_at": deal.dispute_available_at.isoformat()
        if deal.dispute_available_at
        else None,
    }
    reviewed = False
    try:
        reviewed = await deps.review_service.review_for_deal(deal.id, prefer_from=user_id) is not None
    except Exception:
        reviewed = False
    payload["reviewed"] = reviewed
    if deal.status == DealStatus.DISPUTE:
        dispute = await deps.dispute_service.dispute_for_deal(deal.id)
        payload["dispute_id"] = dispute.id if dispute else None
    dispute_any = await deps.dispute_service.dispute_any_for_deal(deal.id)
    if dispute_any and dispute_any.resolved:
        payload["dispute_resolution"] = {
            "seller_amount": dispute_any.seller_amount,
            "buyer_amount": dispute_any.buyer_amount,
            "resolved_by": dispute_any.resolved_by,
            "resolved_at": dispute_any.resolved_at.isoformat() if dispute_any.resolved_at else None,
        }
    include_all = user_id in deps.config.admin_ids
    last_chat = await deps.chat_service.latest_message_for_user(
        deal.id, user_id, include_all=include_all
    )
    payload["chat_last_at"] = last_chat.created_at.isoformat() if last_chat else None
    payload["chat_last_sender_id"] = last_chat.sender_id if last_chat else None
    if with_actions:
        payload["actions"] = _deal_actions(deal, user_id)
    return payload


def _deal_actions(deal, user_id: int) -> dict[str, bool]:
    is_seller = user_id == deal.seller_id
    is_buyer = user_id == deal.buyer_id
    is_initiator = deal.offer_initiator_id == user_id
    is_recipient = (user_id in {deal.seller_id, deal.buyer_id}) and not is_initiator
    can_cancel = bool(
        (is_buyer or is_seller)
        and deal.status.value in {"open", "reserved", "paid"}
        and deal.qr_stage.value != "ready"
    )
    can_accept_offer = bool(deal.status.value == "pending" and is_recipient)
    can_decline_offer = bool(deal.status.value == "pending" and (is_recipient or is_initiator))
    can_buyer_ready = bool(is_buyer and deal.qr_stage.value == "awaiting_buyer_ready")
    can_seller_ready = bool(
        is_seller and deal.qr_stage.value in {"awaiting_seller_attach", "awaiting_buyer_ready"}
    )
    can_confirm_buyer = bool(is_buyer and deal.status.value == "paid")
    can_confirm_seller = bool(is_seller and deal.status.value == "paid")
    can_open_dispute = bool(
        deal.status.value == "paid"
        and deal.dispute_available_at
        and deal.dispute_available_at <= datetime.now(timezone.utc)
    )
    return {
        "cancel": can_cancel,
        "accept_offer": can_accept_offer,
        "decline_offer": can_decline_offer,
        "buyer_ready": can_buyer_ready,
        "seller_ready": can_seller_ready,
        "confirm_buyer": can_confirm_buyer,
        "confirm_seller": can_confirm_seller,
        "open_dispute": can_open_dispute,
    }
