from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import List, Optional
from uuid import uuid4

from cachebot.models.dispute import Dispute, EvidenceItem, MessageItem
from cachebot.storage import StateRepository


class DisputeService:
    def __init__(self, repository: StateRepository) -> None:
        self._repository = repository
        snapshot = repository.snapshot()
        self._disputes: List[Dispute] = list(getattr(snapshot, "disputes", []))
        self._lock = asyncio.Lock()

    async def open_dispute(
        self,
        *,
        deal_id: str,
        opened_by: int,
        reason: str,
        comment: str | None,
        evidence: List[EvidenceItem],
    ) -> Dispute:
        async with self._lock:
            for item in self._disputes:
                if item.deal_id == deal_id and not item.resolved:
                    raise ValueError("Спор уже открыт")
            dispute = Dispute(
                id=str(uuid4()),
                deal_id=deal_id,
                opened_by=opened_by,
                opened_at=datetime.now(timezone.utc),
                reason=reason,
                comment=comment,
                evidence=list(evidence),
                messages=[],
            )
            self._disputes.append(dispute)
            await self._repository.persist_disputes(list(self._disputes))
            return dispute

    async def list_open_disputes(self) -> List[Dispute]:
        async with self._lock:
            return [item for item in self._disputes if not item.resolved]

    async def list_open_disputes_for(self, user_id: int) -> List[Dispute]:
        async with self._lock:
            return [
                item
                for item in self._disputes
                if not item.resolved
                and (item.assigned_to is None or item.assigned_to == user_id)
            ]

    async def list_assigned_open(self, user_id: int) -> List[Dispute]:
        async with self._lock:
            return [
                item
                for item in self._disputes
                if not item.resolved and item.assigned_to == user_id
            ]

    async def count_resolved_by(self, user_id: int) -> int:
        async with self._lock:
            return sum(
                1
                for item in self._disputes
                if item.resolved and item.resolved_by == user_id
            )

    async def dispute_by_id(self, dispute_id: str) -> Optional[Dispute]:
        async with self._lock:
            for item in self._disputes:
                if item.id == dispute_id:
                    return item
        return None

    async def dispute_for_deal(self, deal_id: str) -> Optional[Dispute]:
        async with self._lock:
            for item in self._disputes:
                if item.deal_id == deal_id and not item.resolved:
                    return item
        return None

    async def dispute_any_for_deal(self, deal_id: str) -> Optional[Dispute]:
        async with self._lock:
            for item in self._disputes:
                if item.deal_id == deal_id:
                    return item
        return None

    async def resolve_dispute(
        self,
        dispute_id: str,
        *,
        resolved_by: int,
        seller_amount: str | None,
        buyer_amount: str | None,
    ) -> Dispute:
        async with self._lock:
            for index, item in enumerate(self._disputes):
                if item.id == dispute_id:
                    resolved = Dispute(
                        id=item.id,
                        deal_id=item.deal_id,
                        opened_by=item.opened_by,
                        opened_at=item.opened_at,
                        reason=item.reason,
                        comment=item.comment,
                        evidence=item.evidence,
                        messages=item.messages,
                        resolved=True,
                        resolved_at=datetime.now(timezone.utc),
                        resolved_by=resolved_by,
                        seller_amount=seller_amount,
                        buyer_amount=buyer_amount,
                        assigned_to=item.assigned_to,
                        assigned_at=item.assigned_at,
                    )
                    self._disputes[index] = resolved
                    await self._repository.persist_disputes(list(self._disputes))
                    return resolved
        raise LookupError("Спор не найден")

    async def resolve_for_deal(self, deal_id: str, *, resolved_by: int) -> None:
        async with self._lock:
            updated: List[Dispute] = []
            changed = False
            for item in self._disputes:
                if item.deal_id == deal_id and not item.resolved:
                    updated.append(
                        Dispute(
                            id=item.id,
                            deal_id=item.deal_id,
                            opened_by=item.opened_by,
                            opened_at=item.opened_at,
                            reason=item.reason,
                            comment=item.comment,
                            evidence=item.evidence,
                            messages=item.messages,
                            resolved=True,
                            resolved_at=datetime.now(timezone.utc),
                            resolved_by=resolved_by,
                            seller_amount=item.seller_amount,
                            buyer_amount=item.buyer_amount,
                            assigned_to=item.assigned_to,
                            assigned_at=item.assigned_at,
                        )
                    )
                    changed = True
                else:
                    updated.append(item)
            if changed:
                self._disputes = updated
                await self._repository.persist_disputes(list(self._disputes))

    async def append_message(self, dispute_id: str, author_id: int, text: str) -> MessageItem:
        async with self._lock:
            for index, item in enumerate(self._disputes):
                if item.id == dispute_id:
                    if item.resolved:
                        raise ValueError("Спор уже закрыт")
                    message = MessageItem(
                        author_id=author_id,
                        text=text,
                        created_at=datetime.now(timezone.utc),
                    )
                    updated = Dispute(
                        id=item.id,
                        deal_id=item.deal_id,
                        opened_by=item.opened_by,
                        opened_at=item.opened_at,
                        reason=item.reason,
                        comment=item.comment,
                        evidence=item.evidence,
                        messages=item.messages + [message],
                        resolved=item.resolved,
                        resolved_at=item.resolved_at,
                        resolved_by=item.resolved_by,
                        seller_amount=item.seller_amount,
                        buyer_amount=item.buyer_amount,
                        assigned_to=item.assigned_to,
                        assigned_at=item.assigned_at,
                    )
                    self._disputes[index] = updated
                    await self._repository.persist_disputes(list(self._disputes))
                    return message
        raise LookupError("Спор не найден")

    async def append_evidence(self, dispute_id: str, evidence: EvidenceItem) -> None:
        async with self._lock:
            for index, item in enumerate(self._disputes):
                if item.id == dispute_id:
                    if item.resolved:
                        raise ValueError("Спор уже закрыт")
                    updated = Dispute(
                        id=item.id,
                        deal_id=item.deal_id,
                        opened_by=item.opened_by,
                        opened_at=item.opened_at,
                        reason=item.reason,
                        comment=item.comment,
                        evidence=item.evidence + [evidence],
                        messages=item.messages,
                        resolved=item.resolved,
                        resolved_at=item.resolved_at,
                        resolved_by=item.resolved_by,
                        seller_amount=item.seller_amount,
                        buyer_amount=item.buyer_amount,
                        assigned_to=item.assigned_to,
                        assigned_at=item.assigned_at,
                    )
                    self._disputes[index] = updated
                    await self._repository.persist_disputes(list(self._disputes))
                    return
        raise LookupError("Спор не найден")

    async def append_evidence_with_reason(
        self,
        dispute_id: str,
        evidence: EvidenceItem,
        reason: str | None = None,
        comment: str | None = None,
    ) -> None:
        async with self._lock:
            for index, item in enumerate(self._disputes):
                if item.id == dispute_id:
                    if item.resolved:
                        raise ValueError("Спор уже закрыт")
                    next_reason = item.reason
                    if reason and (not item.reason or item.reason == "Открыт через WebApp"):
                        next_reason = reason
                    next_comment = item.comment
                    if comment and not item.comment:
                        next_comment = comment
                    updated = Dispute(
                        id=item.id,
                        deal_id=item.deal_id,
                        opened_by=item.opened_by,
                        opened_at=item.opened_at,
                        reason=next_reason,
                        comment=next_comment,
                        evidence=item.evidence + [evidence],
                        messages=item.messages,
                        resolved=item.resolved,
                        resolved_at=item.resolved_at,
                        resolved_by=item.resolved_by,
                        seller_amount=item.seller_amount,
                        buyer_amount=item.buyer_amount,
                        assigned_to=item.assigned_to,
                        assigned_at=item.assigned_at,
                    )
                    self._disputes[index] = updated
                    await self._repository.persist_disputes(list(self._disputes))
                    return
        raise LookupError("Спор не найден")

    async def assign(self, dispute_id: str, user_id: int) -> Dispute:
        async with self._lock:
            for index, item in enumerate(self._disputes):
                if item.id == dispute_id:
                    if item.resolved:
                        raise ValueError("Спор уже закрыт")
                    if item.assigned_to and item.assigned_to != user_id:
                        raise ValueError("Спор уже в работе")
                    updated = Dispute(
                        id=item.id,
                        deal_id=item.deal_id,
                        opened_by=item.opened_by,
                        opened_at=item.opened_at,
                        reason=item.reason,
                        comment=item.comment,
                        evidence=item.evidence,
                        messages=item.messages,
                        resolved=item.resolved,
                        resolved_at=item.resolved_at,
                        resolved_by=item.resolved_by,
                        seller_amount=item.seller_amount,
                        buyer_amount=item.buyer_amount,
                        assigned_to=user_id,
                        assigned_at=item.assigned_at or datetime.now(timezone.utc),
                    )
                    self._disputes[index] = updated
                    await self._repository.persist_disputes(list(self._disputes))
                    return updated
        raise LookupError("Спор не найден")
