from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import List, Optional

from cachebot.models.review import Review
from cachebot.storage import StateRepository


class ReviewService:
    def __init__(self, repository: StateRepository) -> None:
        self._repository = repository
        snapshot = repository.snapshot()
        self._reviews: List[Review] = list(getattr(snapshot, "reviews", []))
        self._lock = asyncio.Lock()

    async def add_review(
        self,
        *,
        deal_id: str,
        from_user_id: int,
        to_user_id: int,
        rating: int,
        comment: str | None,
    ) -> Review:
        if rating not in (1, -1):
            raise ValueError("Некорректная оценка")
        async with self._lock:
            for review in self._reviews:
                if review.deal_id == deal_id and review.from_user_id == from_user_id:
                    raise ValueError("Отзыв уже оставлен")
            new_review = Review(
                deal_id=deal_id,
                from_user_id=from_user_id,
                to_user_id=to_user_id,
                rating=rating,
                comment=comment,
                created_at=datetime.now(timezone.utc),
            )
            self._reviews.append(new_review)
            await self._repository.persist_reviews(list(self._reviews))
            return new_review

    async def list_for_user(self, user_id: int) -> List[Review]:
        async with self._lock:
            return [review for review in self._reviews if review.to_user_id == user_id]

    async def review_for_deal(
        self, deal_id: str, *, prefer_from: int | None = None
    ) -> Optional[Review]:
        async with self._lock:
            if prefer_from is not None:
                for review in self._reviews:
                    if review.deal_id == deal_id and review.from_user_id == prefer_from:
                        return review
            for review in self._reviews:
                if review.deal_id == deal_id:
                    return review
        return None

    async def review_between(self, from_user_id: int, to_user_id: int) -> Optional[Review]:
        async with self._lock:
            for review in self._reviews:
                if review.from_user_id == from_user_id and review.to_user_id == to_user_id:
                    return review
        return None
