from datetime import date

from sqlalchemy import(
    BigInteger,
    Date,
    Float,
    String,
    UniqueConstraint,
    URL,
    create_engine,
)

from sqlalchemy.orm import(
    DeclarativeBase,
    Mapped,
    mapped_column
)

class Base(DeclarativeBase):
    pass

class MarketPrice(Base):
    __tablename__ = "market_prices"

    __table_args__ = (
        UniqueConstraint(
            "symbol",
            "date",
            name="uq_market_prices_symbol_date"
        ),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )

    symbol: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    date: Mapped[date] = mapped_column(
        Date,
        nullable=False
    )

    open: Mapped[float] = mapped_column(Float, nullable=False)
    high: Mapped[float] = mapped_column(Float, nullable=False)
    low: Mapped[float] = mapped_column(Float, nullable=False)
    close: Mapped[float] = mapped_column(Float, nullable=False)

    volume: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False
    )

def create_database_engine(password: str):
    database_url = URL.create(
        drivername="postgresql+psycopg",
        username="postgres",
        password=password,
        host="localhost",
        port=5432,
        database="datastream_db",
    )

    return create_engine(database_url, pool_pre_ping=True)


def initialize_database(engine):
    Base.metadata.create_all(engine)



