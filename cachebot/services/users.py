from __future__ import annotations

import asyncio
import random
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Optional

from cachebot.models.user import ApplicationStatus, MerchantApplication, UserProfile, UserRole
from cachebot.storage import StateRepository


@dataclass(slots=True)
class MerchantRecord:
    user_id: int
    profile: UserProfile | None
    merchant_since: datetime | None


class UserService:
    def __init__(self, repository: StateRepository) -> None:
        self._repository = repository
        snapshot = repository.snapshot()
        self._roles: Dict[int, str] = snapshot.user_roles.copy()
        self._applications: List[MerchantApplication] = list(snapshot.applications)
        self._profiles: Dict[int, UserProfile] = snapshot.profiles.copy()
        self._merchant_since: Dict[int, datetime] = {
            uid: datetime.fromisoformat(value) for uid, value in snapshot.merchant_since.items()
        }
        self._moderators = set(snapshot.moderators)
        self._lock = asyncio.Lock()
        now = datetime.now(timezone.utc)
        for uid, role in self._roles.items():
            if role == UserRole.BUYER.value and uid not in self._merchant_since:
                self._merchant_since[uid] = now

    async def set_role(self, user_id: int, role: UserRole, *, revoke_merchant: bool = False) -> None:
        async with self._lock:
            previous = self._roles.get(user_id)
            self._roles[user_id] = role.value
            if role == UserRole.BUYER:
                if previous != UserRole.BUYER.value or user_id not in self._merchant_since:
                    self._merchant_since[user_id] = datetime.now(timezone.utc)
            else:
                if revoke_merchant:
                    self._merchant_since.pop(user_id, None)
            await self._persist()

    async def role_of(self, user_id: int) -> UserRole | None:
        async with self._lock:
            value = self._roles.get(user_id)
        return UserRole(value) if value else None

    async def add_application(self, application: MerchantApplication) -> MerchantApplication:
        async with self._lock:
            self._applications.append(application)
            await self._persist()
            return application

    async def list_applications(self) -> List[MerchantApplication]:
        async with self._lock:
            return list(self._applications)

    async def get_application(self, app_id: str) -> Optional[MerchantApplication]:
        async with self._lock:
            for app in self._applications:
                if app.id == app_id:
                    return app
        return None

    async def update_application_status(
        self, app_id: str, status: ApplicationStatus
    ) -> Optional[MerchantApplication]:
        async with self._lock:
            for index, app in enumerate(self._applications):
                if app.id == app_id:
                    updated = MerchantApplication(
                        id=app.id,
                        user_id=app.user_id,
                        username=app.username,
                        banks=app.banks,
                        uses_personal_bank=app.uses_personal_bank,
                        accepts_risk=app.accepts_risk,
                        photo_file_ids=app.photo_file_ids,
                        created_at=app.created_at,
                        status=status,
                    )
                    self._applications.pop(index)
                    await self._persist()
                    return updated
        return None

    async def ensure_profile(
        self, user_id: int, *, full_name: str | None, username: str | None
    ) -> UserProfile:
        now = datetime.now(timezone.utc)
        async with self._lock:
            profile = self._profiles.get(user_id)
            display_name = profile.display_name if profile else None
            if not display_name:
                display_name = _random_display_name()
            if not profile:
                profile = UserProfile(
                    user_id=user_id,
                    full_name=full_name,
                    username=username,
                    display_name=display_name,
                    avatar_path=None,
                    registered_at=now,
                    last_seen_at=now,
                )
            else:
                profile = UserProfile(
                    user_id=user_id,
                    full_name=full_name if full_name is not None else profile.full_name,
                    username=username if username is not None else profile.username,
                    display_name=display_name,
                    avatar_path=profile.avatar_path,
                    registered_at=profile.registered_at,
                    last_seen_at=now,
                )
            self._profiles[user_id] = profile
            await self._persist()
            return profile

    async def update_profile(
        self,
        user_id: int,
        *,
        display_name: str | None = None,
        avatar_path: str | None = None,
    ) -> UserProfile:
        async with self._lock:
            profile = self._profiles.get(user_id)
            if not profile:
                profile = UserProfile(
                    user_id=user_id,
                    full_name=None,
                    username=None,
                    display_name=_random_display_name(),
                    avatar_path=None,
                    registered_at=datetime.now(timezone.utc),
                    last_seen_at=datetime.now(timezone.utc),
                )
            profile = UserProfile(
                user_id=profile.user_id,
                full_name=profile.full_name,
                username=profile.username,
                display_name=display_name or profile.display_name,
                avatar_path=avatar_path if avatar_path is not None else profile.avatar_path,
                registered_at=profile.registered_at,
                last_seen_at=profile.last_seen_at,
            )
            self._profiles[user_id] = profile
            await self._persist()
            return profile

    async def profile_of(self, user_id: int) -> UserProfile | None:
        async with self._lock:
            return self._profiles.get(user_id)

    async def profile_by_username(self, username: str) -> UserProfile | None:
        needle = username.lstrip("@").lower()
        async with self._lock:
            for profile in self._profiles.values():
                if profile.username and profile.username.lower() == needle:
                    return profile
        return None

    async def is_moderator(self, user_id: int) -> bool:
        async with self._lock:
            return user_id in self._moderators

    async def add_moderator(self, user_id: int) -> None:
        async with self._lock:
            self._moderators.add(user_id)
            await self._persist()

    async def remove_moderator(self, user_id: int) -> None:
        async with self._lock:
            self._moderators.discard(user_id)
            await self._persist()

    async def list_moderators(self) -> List[int]:
        async with self._lock:
            return sorted(self._moderators)

    async def list_merchants(self) -> List[MerchantRecord]:
        async with self._lock:
            records = [
                MerchantRecord(
                    user_id=uid,
                    profile=self._profiles.get(uid),
                    merchant_since=self._merchant_since.get(uid),
                )
                for uid, role in self._roles.items()
                if role == UserRole.BUYER.value
            ]
        records.sort(key=lambda rec: rec.merchant_since or datetime.min.replace(tzinfo=timezone.utc))
        return records

    async def has_merchant_access(self, user_id: int) -> bool:
        async with self._lock:
            if self._roles.get(user_id) == UserRole.BUYER.value:
                return True
            return user_id in self._merchant_since

    async def merchant_since_of(self, user_id: int) -> datetime | None:
        async with self._lock:
            return self._merchant_since.get(user_id)

    async def _persist(self) -> None:
        await self._repository.persist_user_data(
            roles=self._roles.copy(),
            applications=list(self._applications),
            profiles=self._profiles.copy(),
            merchant_since={uid: value.isoformat() for uid, value in self._merchant_since.items()},
            moderators=sorted(self._moderators),
        )


def _random_display_name() -> str:
    adjectives = [
        "Swift",
        "Calm",
        "Bright",
        "Bold",
        "Quick",
        "Silent",
        "Nova",
        "Sunny",
        "Lucky",
        "Cool",
    ]
    nouns = [
        "Fox",
        "Wolf",
        "Eagle",
        "Lynx",
        "Hawk",
        "Bear",
        "Otter",
        "Kite",
        "Raven",
        "Star",
    ]
    return f"{random.choice(adjectives)} {random.choice(nouns)}"
