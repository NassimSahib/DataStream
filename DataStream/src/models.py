
from datetime import date

from sqlalchemy import (
    Date,
    Float,
    ForeignKey,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Indicator(Base):
    __tablename__ = "indicators"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(255))
    unit: Mapped[str] = mapped_column(String(20), nullable=False)

    observations: Mapped[list["ALMObservation"]] = relationship(
        back_populates="indicator"
    )


class ALMObservation(Base):
    __tablename__ = "alm_observations"

    id: Mapped[int] = mapped_column(primary_key=True)

    indicator_id: Mapped[int] = mapped_column(
        ForeignKey("indicators.id"),
        nullable=False,
    )

    observation_date: Mapped[date] = mapped_column(Date, nullable=False)
    entity: Mapped[str] = mapped_column(String(100), nullable=False)
    scenario: Mapped[str] = mapped_column(String(100), nullable=False)
    value: Mapped[float] = mapped_column(Float, nullable=False)

    indicator: Mapped["Indicator"] = relationship(
        back_populates="observations"
    )

    __table_args__ = (
        UniqueConstraint(
            "indicator_id",
            "observation_date",
            "entity",
            "scenario",
            name="uq_alm_observation",
        ),
    )
