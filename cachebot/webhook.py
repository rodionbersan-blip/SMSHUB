from __future__ import annotations

import hashlib
import hmac
import json
import logging
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl

from aiohttp import web

from cachebot.deps import AppDeps
from cachebot.services.scheduler import handle_paid_invoice

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
    deps: AppDeps = request.app["deps"]
    init_data = request.headers.get("X-Telegram-Init-Data") or request.query.get("initData")
    if not init_data:
        raise web.HTTPUnauthorized(text="Missing initData")
    user = _validate_init_data(init_data, deps.config.telegram_bot_token)
    if not user:
        raise web.HTTPUnauthorized(text="Invalid initData")
    return web.json_response({"ok": True, "user": user})


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
