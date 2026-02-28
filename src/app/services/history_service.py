import uuid

from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.models.correction_history import CorrectionHistory


class HistoryService:

    @staticmethod
    async def save(
        db: AsyncSession,
        user_id: uuid.UUID,
        original_comment: str,
        corrected_comment: str,
        is_corrected: bool,
        severity: str | None = None,
        confidence: float | None = None,
        problem_types: list[str] | None = None,
        reason: str | None = None,
    ) -> CorrectionHistory:
        history = CorrectionHistory(
            user_id=user_id,
            original_comment=original_comment,
            corrected_comment=corrected_comment,
            is_corrected=is_corrected,
            severity=severity,
            confidence=confidence,
            problem_types=problem_types,
            reason=reason,
        )
        db.add(history)
        await db.commit()
        await db.refresh(history)
        return history

    @staticmethod
    async def list_by_user(
        db: AsyncSession, user_id: uuid.UUID, page: int = 1, size: int = 20
    ) -> tuple[list[CorrectionHistory], int]:
        # 총 개수
        count_result = await db.execute(
            select(func.count()).select_from(CorrectionHistory).where(
                CorrectionHistory.user_id == user_id
            )
        )
        total = count_result.scalar_one()

        # 페이지네이션 조회
        offset = (page - 1) * size
        result = await db.execute(
            select(CorrectionHistory)
            .where(CorrectionHistory.user_id == user_id)
            .order_by(CorrectionHistory.created_at.desc())
            .offset(offset)
            .limit(size)
        )
        items = list(result.scalars().all())
        return items, total

    @staticmethod
    async def get_by_id(
        db: AsyncSession, history_id: uuid.UUID, user_id: uuid.UUID
    ) -> CorrectionHistory | None:
        result = await db.execute(
            select(CorrectionHistory).where(
                CorrectionHistory.id == history_id,
                CorrectionHistory.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def delete_by_id(
        db: AsyncSession, history_id: uuid.UUID, user_id: uuid.UUID
    ) -> bool:
        result = await db.execute(
            delete(CorrectionHistory).where(
                CorrectionHistory.id == history_id,
                CorrectionHistory.user_id == user_id,
            )
        )
        await db.commit()
        return result.rowcount > 0
