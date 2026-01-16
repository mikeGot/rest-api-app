from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.activity import Activity
    from app.models.building import Building


organization_activities = Table(
    "organization_activities",
    Base.metadata,
    Column(
        "organization_id",
        Integer,
        ForeignKey("organizations.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "activity_id", Integer, ForeignKey("activities.id", ondelete="CASCADE"), primary_key=True
    ),
)


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(300), nullable=False, index=True)
    building_id: Mapped[int] = mapped_column(
        ForeignKey("buildings.id", ondelete="CASCADE"), nullable=False, index=True
    )

    building: Mapped["Building"] = relationship(back_populates="organizations")
    phones: Mapped[list["OrganizationPhone"]] = relationship(
        back_populates="organization", cascade="all, delete-orphan"
    )
    activities: Mapped[list["Activity"]] = relationship(
        secondary="organization_activities", back_populates="organizations"
    )


class OrganizationPhone(Base):
    __tablename__ = "organization_phones"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    phone_number: Mapped[str] = mapped_column(String(20), nullable=False)
    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )

    organization: Mapped["Organization"] = relationship(back_populates="phones")
