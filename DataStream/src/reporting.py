
import pandas as pd

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.database import engine
from src.models import Indicator, ALMObservation
from src.alm_processing import calculate_alm_report


def get_available_indicators() -> list[str]:
    """Retourne les indicateurs disponibles dans PostgreSQL."""

    query = (
        select(Indicator.code)
        .join(
            ALMObservation,
            ALMObservation.indicator_id == Indicator.id,
        )
        .distinct()
        .order_by(Indicator.code)
    )

    with Session(engine) as session:
        return list(session.scalars(query).all())


def get_alm_observations(indicator: str) -> pd.DataFrame:
    """Récupère les observations d'un indicateur depuis PostgreSQL."""

    # 1. Requête SQL filtrée sur l'indicateur
    query = (
        select(
            ALMObservation.observation_date,
            ALMObservation.entity,
            Indicator.code.label("indicator"),
            ALMObservation.scenario,
            ALMObservation.value,
            Indicator.unit,
        )
        .join(
            Indicator,
            ALMObservation.indicator_id == Indicator.id,
        )
        .where(Indicator.code == indicator)
        .order_by(
            ALMObservation.observation_date,
            ALMObservation.entity,
            ALMObservation.scenario,
        )
    )

    # 2. Exécution SQL et conversion en DataFrame
    with Session(engine) as session:
        df = pd.read_sql(query, session.connection())

    # 3. Conversion des dates
    df["observation_date"] = pd.to_datetime(
        df["observation_date"]
    )

    return df


def get_alm_report(indicator: str) -> pd.DataFrame:
    """Construit le reporting d'un indicateur ALM."""

    observations = get_alm_observations(indicator)

    if observations.empty:
        raise ValueError(
            f"Aucune observation disponible pour {indicator}"
        )

    return calculate_alm_report(
        observations,
        indicator,
    )


if __name__ == "__main__":

    print("Indicateurs disponibles :")
    indicators = get_available_indicators()
    print(indicators)

    for indicator in indicators:
        report = get_alm_report(indicator)

        print(f"\nREPORTING {indicator}")
        print(report.tail(5).to_string(index=False))
