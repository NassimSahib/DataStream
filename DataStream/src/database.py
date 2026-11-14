import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from src.ingestion import load_all_alm_csv
from src.models import Base, Indicator, ALMObservation


# Load environment variables
ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(ENV_PATH)

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is missing from .env")


# PostgreSQL connection
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)


def initialize_database():
    """Create tables if they do not exist."""

    Base.metadata.create_all(engine)
    print("Database tables initialized successfully")


def import_alm_observations(df: pd.DataFrame):
    """Insert validated ALM observations into PostgreSQL."""

    with Session(engine) as session:

        for row in df.itertuples(index=False):

            # Find existing indicator
            indicator = session.scalar(
                select(Indicator).where(
                    Indicator.code == row.indicator
                )
            )

            # Create indicator if it does not exist
            if indicator is None:
                indicator = Indicator(
                    code=row.indicator,
                    description=f"ALM indicator {row.indicator}",
                    unit=row.unit,
                )
                session.add(indicator)
                session.flush()

            elif indicator.unit != row.unit:
                raise ValueError(
                    f"Unit mismatch for indicator {row.indicator}"
                )

            # Check if observation already exists
            existing = session.scalar(
                select(ALMObservation).where(
                    ALMObservation.indicator_id == indicator.id,
                    ALMObservation.observation_date == row.observation_date.date(),
                    ALMObservation.entity == row.entity,
                    ALMObservation.scenario == row.scenario,
                )
            )

            if existing is None:
                observation = ALMObservation(
                    indicator_id=indicator.id,
                    observation_date=row.observation_date.date(),
                    entity=row.entity,
                    scenario=row.scenario,
                    value=float(row.value),
                )

                session.add(observation)

        # Commit all inserts
        session.commit()

    print("ALM observations imported successfully")



if __name__ == "__main__":

    # 1. Création des tables si nécessaire
    initialize_database()

    # 2. Chargement et validation des deux sources
    observations = load_all_alm_csv()

    # 3. Insertion en base PostgreSQL
    import_alm_observations(observations)

    # 4. Résumé du traitement
    print("\nImport multi-source terminé")
    print(f"Observations traitées : {len(observations)}")

    print("\nRépartition par indicateur :")
    print(observations.groupby("indicator").size())

