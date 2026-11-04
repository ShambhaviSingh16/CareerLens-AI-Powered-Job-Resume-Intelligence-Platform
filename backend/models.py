from datetime import date, datetime, timezone
from typing import Any

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class DailyUsage(Base):
    """Anonymous daily total, so account deletion cannot reset the provider budget."""
    __tablename__ = "daily_usage"
    day: Mapped[date] = mapped_column(Date, primary_key=True)
    attempts: Mapped[int] = mapped_column(Integer, default=0)


class AnalysisAttempt(Base):
    """Quota accounting survives result deletion; contains no document content."""
    __tablename__ = "analysis_attempts"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True
    )
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    resumes: Mapped[list["Resume"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )

    jobs: Mapped[list["Job"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )

    analyses: Mapped[list["Analysis"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )


class Resume(Base):
    __tablename__ = "resumes"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        index=True
    )
    filename: Mapped[str] = mapped_column(String(255))
    extracted_text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    user: Mapped["User"] = relationship(
        back_populates="resumes"
    )

    analyses: Mapped[list["Analysis"]] = relationship(
        back_populates="resume"
    )


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        index=True
    )
    title: Mapped[str] = mapped_column(String(255))
    company: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )
    description: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    user: Mapped["User"] = relationship(
        back_populates="jobs"
    )

    analyses: Mapped[list["Analysis"]] = relationship(
        back_populates="job"
    )


class Analysis(Base):
    __tablename__ = "analyses"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        index=True
    )

    resume_id: Mapped[int] = mapped_column(
        ForeignKey("resumes.id"),
        index=True
    )

    job_id: Mapped[int] = mapped_column(
        ForeignKey("jobs.id"),
        index=True
    )

    match_score: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    result: Mapped[dict[str, Any] | None] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    user: Mapped["User"] = relationship(
        back_populates="analyses"
    )

    resume: Mapped["Resume"] = relationship(
        back_populates="analyses"
    )

    job: Mapped["Job"] = relationship(
        back_populates="analyses"
    )
