from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, List


class UserRole(str, Enum):
    BUYER = "buyer"
    SELLER = "seller"


class ApplicationStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


@dataclass(slots=True)
class MerchantApplication:
    id: str
    user_id: int
    username: str | None
    banks: List[str]
    uses_personal_bank: bool
    accepts_risk: bool
    photo_file_ids: List[str]
    created_at: datetime
    status: ApplicationStatus = ApplicationStatus.PENDING

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "username": self.username,
            "banks": self.banks,
            "uses_personal_bank": self.uses_personal_bank,
            "accepts_risk": self.accepts_risk,
            "photo_file_ids": self.photo_file_ids,
            "created_at": self.created_at.isoformat(),
            "status": self.status.value,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MerchantApplication":
        return cls(
            id=data["id"],
            user_id=int(data["user_id"]),
            username=data.get("username"),
            banks=list(data.get("banks") or []),
            uses_personal_bank=bool(data.get("uses_personal_bank")),
            accepts_risk=bool(data.get("accepts_risk")),
            photo_file_ids=list(data.get("photo_file_ids") or []),
            created_at=datetime.fromisoformat(data["created_at"]),
            status=ApplicationStatus(data.get("status", ApplicationStatus.PENDING)),
        )


@dataclass(slots=True)
class UserProfile:
    user_id: int
    full_name: str | None
    username: str | None
    registered_at: datetime
    last_seen_at: datetime

    def to_dict(self) -> dict[str, Any]:
        return {
            "user_id": self.user_id,
            "full_name": self.full_name,
            "username": self.username,
            "registered_at": self.registered_at.isoformat(),
            "last_seen_at": self.last_seen_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "UserProfile":
        registered = datetime.fromisoformat(data["registered_at"])
        return cls(
            user_id=int(data["user_id"]),
            full_name=data.get("full_name"),
            username=data.get("username"),
            registered_at=registered,
            last_seen_at=datetime.fromisoformat(data.get("last_seen_at", data["registered_at"])),
        )
