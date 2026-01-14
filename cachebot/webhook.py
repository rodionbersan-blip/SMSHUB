from __future__ import annotations

import hashlib
import hmac
import json
import logging
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl
from decimal import Decimal, InvalidOperation, ROUND_UP

from aiohttp import web

from cachebot.deps import AppDeps
from cachebot.services.scheduler import handle_paid_invoice
from cachebot.models.advert import AdvertSide
from cachebot.constants import BANK_OPTIONS

logger = logging.getLogger(__name__)


def create_app(bot, deps: AppDeps) -> web.Application:
    app = web.Application()
    app["bot"] = bot
    app["deps"] = deps
    app.router.add_post(deps.config.webhook_path, _crypto_pay_handler)
    app.router.add_get("/app", _webapp_index)
    app.router.add_get("/app/", _webapp_index)
    app.router.add_get("/app/{path:.*}", _webapp_static)
    app.router.add_get("/api/me", _api_me)
    app.router.add_get("/api/profile", _api_profile)
    app.router.add_get("/api/balance", _api_balance)
    app.router.add_get("/api/my-deals", _api_my_deals)
    app.router.add_get("/api/deals/{deal_id}", _api_deal_detail)
    app.router.add_post("/api/deals/{deal_id}/cancel", _api_deal_cancel)
    app.router.add_post("/api/deals/{deal_id}/buyer-ready", _api_deal_buyer_ready)
    app.router.add_post("/api/deals/{deal_id}/seller-ready", _api_deal_seller_ready)
    app.router.add_post("/api/deals/{deal_id}/confirm-buyer", _api_deal_confirm_buyer)
    app.router.add_post("/api/deals/{deal_id}/confirm-seller", _api_deal_confirm_seller)
    app.router.add_post("/api/deals/{deal_id}/open-dispute", _api_deal_open_dispute)
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
    app.router.add_get("/api/admin/summary", _api_admin_summary)
    app.router.add_get("/api/admin/settings", _api_admin_settings)
    app.router.add_post("/api/admin/settings", _api_admin_settings_update)
    app.router.add_get("/api/admin/moderators", _api_admin_moderators)
    app.router.add_post("/api/admin/moderators", _api_admin_add_moderator)
    app.router.add_delete("/api/admin/moderators/{user_id}", _api_admin_remove_moderator)
    app.router.add_get("/api/admin/merchants", _api_admin_merchants)
    app.router.add_post("/api/admin/merchants/{user_id}/revoke", _api_admin_merchant_revoke)
    app.router.add_get("/api/reviews", _api_reviews_list)
    app.router.add_get("/api/summary", _api_summary)
    app.router.add_get("/api/ping", _api_ping)
    return app


async def _crypto_pay_handler(request: web.Request) -> web.Response:
    deps: AppDeps = request.app["deps"]
    bot = request.app["bot"]
    secret = deps.config.crypto_pay_webhook_secret or deps.config.crypto_pay_token
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
        try:
            deal = await deps.deal_service.mark_invoice_paid(str(invoice_id))
            await handle_paid_invoice(deal, deps.kb_client, bot)
        except Exception as exc:  # pragma: no cover
            logger.exception("Failed to handle paid invoice %s: %s", invoice_id, exc)
            raise web.HTTPInternalServerError()

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
    return web.FileResponse(index_path)


async def _webapp_static(request: web.Request) -> web.Response:
    root = _webapp_root()
    rel_path = request.match_info.get("path") or ""
    safe_path = (root / rel_path).resolve()
    if not safe_path.exists() or root not in safe_path.parents:
        raise web.HTTPNotFound()
    return web.FileResponse(safe_path)


async def _api_ping(_: web.Request) -> web.Response:
    return web.json_response({"ok": True})


async def _api_me(request: web.Request) -> web.Response:
    user, _ = await _require_user(request)
    return web.json_response({"ok": True, "user": user})


async def _api_profile(request: web.Request) -> web.Response:
    deps: AppDeps = request.app["deps"]
    user, user_id = await _require_user(request)
    profile = await deps.user_service.profile_of(user_id)
    role = await deps.user_service.role_of(user_id)
    merchant_since = await deps.user_service.merchant_since_of(user_id)
    payload = {
        "user": user,
        "profile": _profile_payload(profile),
        "role": role.value if role else None,
        "merchant_since": merchant_since.isoformat() if merchant_since else None,
    }
    return web.json_response({"ok": True, "data": payload})


async def _api_balance(request: web.Request) -> web.Response:
    deps: AppDeps = request.app["deps"]
    _, user_id = await _require_user(request)
    balance = await deps.deal_service.balance_of(user_id)
    return web.json_response({"ok": True, "balance": str(balance)})


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
        payload.append(await _deal_payload(deps, deal, user_id))
    return web.json_response({"ok": True, "deals": payload})


async def _api_deal_detail(request: web.Request) -> web.Response:
    deps: AppDeps = request.app["deps"]
    _, user_id = await _require_user(request)
    deal_id = request.match_info["deal_id"]
    deal = await deps.deal_service.get_deal(deal_id)
    if not deal:
        raise web.HTTPNotFound(text="Deal not found")
    if user_id not in {deal.seller_id, deal.buyer_id}:
        raise web.HTTPForbidden(text="Нет доступа к сделке")
    payload = await _deal_payload(deps, deal, user_id, with_actions=True)
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
    payload = await _deal_payload(deps, deal, user_id, with_actions=True)
    return web.json_response({"ok": True, "deal": payload})


async def _api_deal_buyer_ready(request: web.Request) -> web.Response:
    deps: AppDeps = request.app["deps"]
    _, user_id = await _require_user(request)
    deal_id = request.match_info["deal_id"]
    try:
        deal = await deps.deal_service.buyer_ready_for_qr(deal_id, user_id)
    except (PermissionError, ValueError) as exc:
        raise web.HTTPBadRequest(text=str(exc))
    payload = await _deal_payload(deps, deal, user_id, with_actions=True)
    return web.json_response({"ok": True, "deal": payload})


async def _api_deal_seller_ready(request: web.Request) -> web.Response:
    deps: AppDeps = request.app["deps"]
    _, user_id = await _require_user(request)
    deal_id = request.match_info["deal_id"]
    try:
        deal = await deps.deal_service.seller_request_qr(deal_id, user_id)
    except (PermissionError, ValueError) as exc:
        raise web.HTTPBadRequest(text=str(exc))
    payload = await _deal_payload(deps, deal, user_id, with_actions=True)
    return web.json_response({"ok": True, "deal": payload})


async def _api_deal_confirm_buyer(request: web.Request) -> web.Response:
    deps: AppDeps = request.app["deps"]
    _, user_id = await _require_user(request)
    deal_id = request.match_info["deal_id"]
    try:
        deal, _ = await deps.deal_service.confirm_buyer_cash(deal_id, user_id)
    except (PermissionError, ValueError) as exc:
        raise web.HTTPBadRequest(text=str(exc))
    payload = await _deal_payload(deps, deal, user_id, with_actions=True)
    return web.json_response({"ok": True, "deal": payload})


async def _api_deal_confirm_seller(request: web.Request) -> web.Response:
    deps: AppDeps = request.app["deps"]
    _, user_id = await _require_user(request)
    deal_id = request.match_info["deal_id"]
    try:
        deal, _ = await deps.deal_service.confirm_seller_cash(deal_id, user_id)
    except (PermissionError, ValueError) as exc:
        raise web.HTTPBadRequest(text=str(exc))
    payload = await _deal_payload(deps, deal, user_id, with_actions=True)
    return web.json_response({"ok": True, "deal": payload})


async def _api_deal_open_dispute(request: web.Request) -> web.Response:
    deps: AppDeps = request.app["deps"]
    _, user_id = await _require_user(request)
    deal_id = request.match_info["deal_id"]
    try:
        deal = await deps.deal_service.open_dispute(deal_id, user_id)
    except (PermissionError, ValueError) as exc:
        raise web.HTTPBadRequest(text=str(exc))
    payload = await _deal_payload(deps, deal, user_id, with_actions=True)
    return web.json_response({"ok": True, "deal": payload})


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
    payload = [await _ad_payload(deps, ad) for ad in ads]
    return web.json_response({"ok": True, "ads": payload})


async def _api_p2p_my_ads(request: web.Request) -> web.Response:
    deps: AppDeps = request.app["deps"]
    _, user_id = await _require_user(request)
    ads = await deps.advert_service.list_user_ads(user_id)
    payload = [await _ad_payload(deps, ad, include_owner=False) for ad in ads]
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
    payload = await _ad_payload(deps, ad, include_owner=False)
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
    payload = await _ad_payload(deps, updated, include_owner=False)
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
    updated = await deps.advert_service.toggle_active(ad_id, bool(desired))
    payload = await _ad_payload(deps, updated, include_owner=False)
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
    if rub_amount < ad.min_rub or rub_amount > ad.max_rub:
        raise web.HTTPBadRequest(text="Сумма должна быть в пределах лимитов объявления")
    base_usdt = rub_amount / ad.price_rub
    if base_usdt > ad.remaining_usdt:
        raise web.HTTPBadRequest(text="В объявлении недостаточно объёма")
    if ad.side == AdvertSide.SELL:
        seller_id = ad.owner_id
        buyer_id = user_id
    else:
        seller_id = user_id
        buyer_id = ad.owner_id
    try:
        deal = await deps.deal_service.create_p2p_deal(
            seller_id=seller_id,
            buyer_id=buyer_id,
            usd_amount=rub_amount,
            rate=ad.price_rub,
            advert_id=ad.id,
            comment=ad.terms,
        )
        await deps.advert_service.reduce_volume(ad.id, base_usdt)
        invoice = await deps.crypto_pay.create_invoice(
            amount=deal.usdt_amount,
            currency="USDT",
            description=f"Сделка {deal.hashtag} на {deal.usd_amount} RUB",
            payload=deal.id,
        )
        await deps.deal_service.attach_invoice(deal.id, invoice.invoice_id, invoice.pay_url)
    except Exception as exc:
        raise web.HTTPBadRequest(text=f"Не удалось создать сделку: {exc}")
    if buyer_id != user_id:
        await bot.send_message(
            buyer_id,
            f"✅ Сделка {deal.hashtag} создана.\nОжидаем оплату продавца.",
        )
    await bot.send_message(
        seller_id,
        f"✅ Сделка {deal.hashtag} закреплена за тобой.\n"
        f"Оплати {deal.usdt_amount.quantize(Decimal('0.01'), rounding=ROUND_UP)} USDT\n"
        "После оплаты начнется отсчет времени для открытия спора.",
    )
    payload = await _deal_payload(deps, deal, user_id, with_actions=True)
    return web.json_response(
        {
            "ok": True,
            "deal": payload,
            "pay_url": invoice.pay_url if user_id == seller_id else None,
        }
    )


async def _api_disputes_summary(request: web.Request) -> web.Response:
    deps: AppDeps = request.app["deps"]
    _, user_id = await _require_user(request)
    can_access = await _has_dispute_access(user_id, deps)
    if not can_access:
        return web.json_response({"ok": True, "can_access": False, "count": 0})
    disputes = await deps.dispute_service.list_open_disputes_for(user_id)
    return web.json_response({"ok": True, "can_access": True, "count": len(disputes)})


async def _api_disputes_list(request: web.Request) -> web.Response:
    deps: AppDeps = request.app["deps"]
    _, user_id = await _require_user(request)
    if not await _has_dispute_access(user_id, deps):
        raise web.HTTPForbidden(text="Нет доступа")
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
    evidence = []
    for item in dispute.evidence:
        file_url = await _file_url(request, item.file_id)
        evidence.append(
            {
                "kind": item.kind,
                "file_id": item.file_id,
                "author_id": item.author_id,
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
        "assigned_to": dispute.assigned_to,
        "messages": [
            {
                "author_id": msg.author_id,
                "text": msg.text,
                "created_at": msg.created_at.isoformat(),
            }
            for msg in dispute.messages
        ],
        "evidence": evidence,
        "deal": await _deal_payload(deps, deal, user_id, with_actions=False),
        "seller": _profile_payload(seller),
        "buyer": _profile_payload(buyer),
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
    return web.json_response({"ok": True})


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
                "profile": _profile_payload(profile),
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
                "profile": _profile_payload(rec.profile),
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
    reviews = await deps.review_service.list_for_user(user_id)
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
                "author": _profile_payload(author),
            }
        )
    positive = sum(1 for item in reviews if item.rating > 0)
    negative = sum(1 for item in reviews if item.rating < 0)
    return web.json_response(
        {"ok": True, "reviews": payload, "positive": positive, "negative": negative}
    )


def _validate_init_data(init_data: str, bot_token: str) -> dict[str, Any] | None:
    try:
        pairs = parse_qsl(init_data, keep_blank_values=True)
    except Exception:
        return None
    data = dict(pairs)
    received_hash = data.pop("hash", "")
    if not received_hash:
        return None
    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(data.items()))
    secret_key = hashlib.sha256(bot_token.encode()).digest()
    expected_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(received_hash, expected_hash):
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


def _profile_payload(profile) -> dict[str, Any] | None:
    if not profile:
        return None
    return {
        "user_id": profile.user_id,
        "full_name": profile.full_name,
        "username": profile.username,
        "registered_at": profile.registered_at.isoformat(),
        "last_seen_at": profile.last_seen_at.isoformat() if profile.last_seen_at else None,
    }


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


async def _ad_payload(deps: AppDeps, ad, *, include_owner: bool = True) -> dict[str, Any]:
    owner = await deps.user_service.profile_of(ad.owner_id) if include_owner else None
    return {
        "id": ad.id,
        "public_id": ad.public_id,
        "side": ad.side.value,
        "price_rub": str(ad.price_rub),
        "total_usdt": str(ad.total_usdt),
        "remaining_usdt": str(ad.remaining_usdt),
        "min_rub": str(ad.min_rub),
        "max_rub": str(ad.max_rub),
        "banks": list(ad.banks),
        "terms": ad.terms,
        "active": ad.active,
        "created_at": ad.created_at.isoformat(),
        "owner": _profile_payload(owner) if include_owner else None,
    }


async def _file_url(request: web.Request, file_id: str) -> str | None:
    if not file_id:
        return None
    bot = request.app["bot"]
    deps: AppDeps = request.app["deps"]
    try:
        file = await bot.get_file(file_id)
    except Exception:
        return None
    return f"https://api.telegram.org/file/bot{deps.config.telegram_bot_token}/{file.file_path}"


async def _deal_payload(
    deps: AppDeps, deal, user_id: int, *, with_actions: bool = False
) -> dict[str, Any]:
    role = "seller" if deal.seller_id == user_id else "buyer"
    counterparty_id = deal.buyer_id if role == "seller" else deal.seller_id
    counterparty = await deps.user_service.profile_of(counterparty_id) if counterparty_id else None
    payload = {
        "id": deal.id,
        "public_id": deal.public_id,
        "status": deal.status.value,
        "qr_stage": deal.qr_stage.value,
        "role": role,
        "cash_rub": str(deal.usd_amount),
        "usdt_amount": str(deal.usdt_amount),
        "rate": str(deal.rate),
        "created_at": deal.created_at.isoformat(),
        "atm_bank": deal.atm_bank,
        "counterparty": _profile_payload(counterparty),
        "is_p2p": deal.is_p2p,
        "buyer_cash_confirmed": deal.buyer_cash_confirmed,
        "seller_cash_confirmed": deal.seller_cash_confirmed,
        "dispute_available_at": deal.dispute_available_at.isoformat()
        if deal.dispute_available_at
        else None,
    }
    if with_actions:
        payload["actions"] = _deal_actions(deal, user_id)
    return payload


def _deal_actions(deal, user_id: int) -> dict[str, bool]:
    is_seller = user_id == deal.seller_id
    is_buyer = user_id == deal.buyer_id
    can_cancel = bool(
        (is_buyer)
        or (is_seller and deal.status.value in {"open", "reserved", "paid"})
    )
    can_buyer_ready = bool(is_buyer and deal.qr_stage.value == "awaiting_buyer_ready")
    can_seller_ready = bool(
        is_seller and deal.qr_stage.value in {"awaiting_seller_attach", "awaiting_buyer_ready"}
    )
    can_confirm_buyer = bool(
        is_buyer and deal.status.value in {"paid", "completed"} and deal.status.value != "dispute"
    )
    can_confirm_seller = bool(
        is_seller and deal.status.value in {"paid", "completed"} and deal.status.value != "dispute"
    )
    can_open_dispute = bool(
        deal.status.value == "paid"
        and deal.dispute_available_at
        and deal.dispute_available_at <= datetime.now(timezone.utc)
    )
    return {
        "cancel": can_cancel,
        "buyer_ready": can_buyer_ready,
        "seller_ready": can_seller_ready,
        "confirm_buyer": can_confirm_buyer,
        "confirm_seller": can_confirm_seller,
        "open_dispute": can_open_dispute,
    }
