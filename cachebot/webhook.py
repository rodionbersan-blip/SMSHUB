from __future__ import annotations

import hashlib
import hmac
import json
import logging
from typing import Any

from aiohttp import web

from cachebot.deps import AppDeps
from cachebot.services.scheduler import handle_paid_invoice

logger = logging.getLogger(__name__)


def create_app(bot, deps: AppDeps) -> web.Application:
    app = web.Application()
    app["bot"] = bot
    app["deps"] = deps
    app.router.add_post(deps.config.webhook_path, _crypto_pay_handler)
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
