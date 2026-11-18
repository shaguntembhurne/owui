from __future__ import annotations

import uuid

from open_webui.internal.db import Base, get_async_db_context
from pydantic import BaseModel, ConfigDict
from sqlalchemy import Boolean, Column, Integer, String, select, update
from sqlalchemy.ext.asyncio import AsyncSession


class OtpChallenge(Base):
    __tablename__ = 'otp_challenge'

    id = Column(String, primary_key=True, unique=True)
    email = Column(String, nullable=False, index=True)
    code_hash = Column(String, nullable=False)
    created_at = Column(Integer, nullable=False)
    expires_at = Column(Integer, nullable=False)
    attempts = Column(Integer, nullable=False, default=0)
    consumed = Column(Boolean, nullable=False, default=False)


class OtpChallengeModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str
    code_hash: str
    created_at: int
    expires_at: int
    attempts: int
    consumed: bool


class OtpChallengesTable:
    async def get_latest_active(self, email: str, db: AsyncSession | None = None) -> OtpChallengeModel | None:
        async with get_async_db_context(db) as session:
            row = (
                await session.execute(
                    select(OtpChallenge)
                    .where(OtpChallenge.email == email, OtpChallenge.consumed.is_(False))
                    .order_by(OtpChallenge.created_at.desc())
                    .limit(1)
                )
            ).scalar_one_or_none()
            return OtpChallengeModel.model_validate(row) if row else None

    async def count_recent(self, email: str, since: int, db: AsyncSession | None = None) -> int:
        async with get_async_db_context(db) as session:
            from sqlalchemy import func

            return int(
                await session.scalar(
                    select(func.count()).select_from(OtpChallenge).where(
                        OtpChallenge.email == email,
                        OtpChallenge.created_at >= since,
                    )
                )
                or 0
            )

    async def create(
        self,
        email: str,
        code_hash: str,
        created_at: int,
        expires_at: int,
        db: AsyncSession | None = None,
    ) -> OtpChallengeModel:
        async with get_async_db_context(db) as session:
            await session.execute(
                update(OtpChallenge)
                .where(OtpChallenge.email == email, OtpChallenge.consumed.is_(False))
                .values(consumed=True)
            )
            row = OtpChallenge(
                id=str(uuid.uuid4()),
                email=email,
                code_hash=code_hash,
                created_at=created_at,
                expires_at=expires_at,
                attempts=0,
                consumed=False,
            )
            session.add(row)
            await session.commit()
            return OtpChallengeModel.model_validate(row)

    async def record_attempt(self, challenge_id: str, db: AsyncSession | None = None) -> int | None:
        async with get_async_db_context(db) as session:
            result = await session.execute(
                update(OtpChallenge)
                .where(
                    OtpChallenge.id == challenge_id,
                    OtpChallenge.consumed.is_(False),
                )
                .values(attempts=OtpChallenge.attempts + 1)
                .returning(OtpChallenge.attempts)
            )
            await session.commit()
            return result.scalar_one_or_none()

    async def consume_if_valid(
        self,
        challenge_id: str,
        email: str,
        code_hash: str,
        now: int,
        max_attempts: int,
        db: AsyncSession | None = None,
    ) -> bool:
        async with get_async_db_context(db) as session:
            result = await session.execute(
                update(OtpChallenge)
                .where(
                    OtpChallenge.id == challenge_id,
                    OtpChallenge.email == email,
                    OtpChallenge.code_hash == code_hash,
                    OtpChallenge.expires_at > now,
                    OtpChallenge.attempts < max_attempts,
                    OtpChallenge.consumed.is_(False),
                )
                .values(consumed=True)
                .execution_options(synchronize_session=False)
            )
            await session.commit()
            return result.rowcount == 1

    async def invalidate(self, challenge_id: str, db: AsyncSession | None = None) -> None:
        async with get_async_db_context(db) as session:
            await session.execute(
                update(OtpChallenge).where(OtpChallenge.id == challenge_id).values(consumed=True)
            )
            await session.commit()


OtpChallenges = OtpChallengesTable()
