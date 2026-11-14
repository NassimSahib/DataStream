
import pandas as pd
import pytest

from src.alm_processing import calculate_alm_report
from src.ingestion import load_alm_csv


@pytest.fixture
def sample_data():
    """Jeu de données ALM fictif pour les tests."""

    return pd.DataFrame({
        "observation_date": pd.to_datetime([
            "2026-06-30",
            "2026-06-30",
        ]),
        "entity": ["BANK_DEMO", "BANK_DEMO"],
        "indicator": ["EVE", "EVE"],
        "scenario": ["BASE", "RATE_UP_200BP"],
        "value": [1210.0, 1125.0],
        "unit": ["EUR_M", "EUR_M"],
    })


def test_delta_absolu(sample_data):
    """Vérifie le calcul de la variation absolue."""

    report = calculate_alm_report(sample_data, "EVE")

    assert report.iloc[0]["delta_value"] == -85.0


def test_delta_relatif(sample_data):
    """Vérifie le calcul de la variation en pourcentage."""

    report = calculate_alm_report(sample_data, "EVE")

    assert report.iloc[0]["delta_pct"] == pytest.approx(
        -85 / 1210 * 100
    )


def test_scenario_manquant(sample_data):
    """Vérifie le rejet d'une paire de scénarios incomplète."""

    incomplete = sample_data[
        sample_data["scenario"] == "BASE"
    ].copy()

    with pytest.raises(ValueError):
        calculate_alm_report(incomplete, "EVE")


def test_doublon(sample_data):
    """Vérifie le rejet d'observations dupliquées."""

    duplicated = pd.concat(
        [sample_data, sample_data.iloc[[0]]],
        ignore_index=True,
    )

    with pytest.raises(ValueError, match="dupliquées"):
        calculate_alm_report(duplicated, "EVE")


def test_indicateur_inexistant(sample_data):
    """Vérifie le comportement pour un indicateur absent."""

    with pytest.raises(ValueError):
        calculate_alm_report(sample_data, "NII")


def test_ingestion_colonne_manquante(tmp_path):
    """Vérifie le rejet d'un CSV mal structuré."""

    csv_path = tmp_path / "invalid.csv"

    pd.DataFrame({
        "observation_date": ["2026-06-30"],
        "entity": ["BANK_DEMO"],
        "value": [1210.0],
    }).to_csv(csv_path, index=False)

    with pytest.raises(ValueError, match="Colonnes manquantes"):
        load_alm_csv(csv_path)

