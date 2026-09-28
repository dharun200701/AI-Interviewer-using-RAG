from datetime import datetime
from typing import Optional

from sqlalchemy import (
    String,
    Text,
    Integer,
    Float,
    ForeignKey,
    DateTime,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.connection import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    resumes = relationship(
        "Resume",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    interviews = relationship(
        "InterviewSession",
        back_populates="user",
        cascade="all, delete-orphan"
    )


class Resume(Base):
    __tablename__ = "resumes"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    file_name: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )

    file_url: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )

    raw_text: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )

    structured_data: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    user = relationship(
        "User",
        back_populates="resumes"
    )

    interviews = relationship(
        "InterviewSession",
        back_populates="resume",
        cascade="all, delete-orphan"
    )


class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    resume_id: Mapped[int] = mapped_column(
        ForeignKey("resumes.id"),
        nullable=False
    )

    interview_type: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )

    difficulty: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="created"
    )

    overall_score: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True
    )

    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True
    )

    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    user = relationship(
        "User",
        back_populates="interviews"
    )

    resume = relationship(
        "Resume",
        back_populates="interviews"
    )

    questions = relationship(
        "Question",
        back_populates="interview",
        cascade="all, delete-orphan"
    )


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    interview_id: Mapped[int] = mapped_column(
        ForeignKey("interview_sessions.id"),
        nullable=False
    )

    question: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    category: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )

    difficulty: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True
    )

    source: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )

    resume_reference: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )

    expected_concepts: Mapped[Optional[list]] = mapped_column(
        JSONB,
        nullable=True
    )

    question_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    interview = relationship(
        "InterviewSession",
        back_populates="questions"
    )

    answers = relationship(
        "Answer",
        back_populates="question",
        cascade="all, delete-orphan"
    )


class Answer(Base):
    __tablename__ = "answers"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    question_id: Mapped[int] = mapped_column(
        ForeignKey("questions.id"),
        nullable=False
    )

    answer: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    correctness: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True
    )

    relevance: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True
    )

    technical_depth: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True
    )

    clarity: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True
    )

    completeness: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True
    )

    resume_consistency: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True
    )

    evaluation: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    question = relationship(
        "Question",
        back_populates="answers"
    )