from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.organization import Organization


class Activity(Base):
    __tablename__ = "activities"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("activities.id", ondelete="CASCADE"), nullable=True, index=True
    )
    level: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    parent: Mapped[Activity | None] = relationship(
        "Activity", remote_side="Activity.id", back_populates="children"
    )
    children: Mapped[list[Activity]] = relationship(
        "Activity", back_populates="parent", cascade="all, delete-orphan"
    )

    organizations: Mapped[list[Organization]] = relationship(
        secondary="organization_activities", back_populates="activities"
    )

    __table_args__ = (CheckConstraint("level >= 1 AND level <= 3", name="check_activity_level"),)
