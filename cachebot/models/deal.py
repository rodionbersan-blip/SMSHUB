from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any


class DealStatus(str, Enum):
    OPEN = "open"
    RESERVED = "reserved"
    PAID = "paid"
    COMPLETED = "completed"
    CANCELED = "canceled"
    EXPIRED = "expired"


@dataclass(slots=True)
class Deal:
    id: str
    seller_id: int
    usd_amount: Decimal
    rate: Decimal
    fee_percent: Decimal
    fee_amount: Decimal
    usdt_amount: Decimal
    created_at: datetime
    expires_at: datetime
    status: DealStatus = DealStatus.OPEN
    buyer_id: int | None = None
    invoice_id: str | None = None
    invoice_url: str | None = None
    comment: str | None = None
    public_id: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "seller_id": self.seller_id,
            "usd_amount": str(self.usd_amount),
            "rate": str(self.rate),
            "fee_percent": str(self.fee_percent),
            "fee_amount": str(self.fee_amount),
            "usdt_amount": str(self.usdt_amount),
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "status": self.status.value,
            "buyer_id": self.buyer_id,
            "invoice_id": self.invoice_id,
            "invoice_url": self.invoice_url,
            "comment": self.comment,
            "public_id": self.public_id,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Deal":
        return cls(
            id=data["id"],
            seller_id=int(data["seller_id"]),
            usd_amount=Decimal(data["usd_amount"]),
            rate=Decimal(data["rate"]),
            fee_percent=Decimal(data["fee_percent"]),
            fee_amount=Decimal(data["fee_amount"]),
            usdt_amount=Decimal(data["usdt_amount"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            expires_at=datetime.fromisoformat(data["expires_at"]),
            status=DealStatus(data["status"]),
            buyer_id=data.get("buyer_id"),
            invoice_id=data.get("invoice_id"),
            invoice_url=data.get("invoice_url"),
            comment=data.get("comment"),
            public_id=data.get("public_id") or _fallback_public_id(data["id"]),
        )


def _fallback_public_id(source_id: str) -> str:
    trimmed = source_id.replace("-", "")[:8]
    return f"D{trimmed.upper()}"
