
from pathlib import Path

import numpy as np
import pandas as pd


# Dossier des fichiers sources
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

EVE_PATH = DATA_DIR / "alm_eve.csv"
NII_PATH = DATA_DIR / "alm_nii.csv"

SOURCE_FILES = [EVE_PATH, NII_PATH]


REQUIRED_COLUMNS = [
    "observation_date",
    "entity",
    "indicator",
    "scenario",
    "value",
    "unit",
]

KEY_COLUMNS = [
    "observation_date",
    "entity",
    "indicator",
    "scenario",
]


def load_alm_csv(file_path: str | Path = EVE_PATH) -> pd.DataFrame:
    """Charge et valide un fichier CSV ALM."""

    # 1. Lecture des données
    df = pd.read_csv(file_path)

    # 2. Vérification des colonnes
    missing_columns = set(REQUIRED_COLUMNS) - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Colonnes manquantes : {sorted(missing_columns)}"
        )

    df = df[REQUIRED_COLUMNS].copy()

    # 3. Contrôle des valeurs manquantes
    if df.isna().any().any():
        raise ValueError("Le CSV contient des valeurs manquantes")

    # 4. Nettoyage des colonnes texte
    text_columns = ["entity", "indicator", "scenario", "unit"]

    for column in text_columns:
        df[column] = df[column].astype(str).str.strip()

        if df[column].eq("").any():
            raise ValueError(f"Valeur vide : {column}")

    # 5. Conversion des types
    df["observation_date"] = pd.to_datetime(
        df["observation_date"],
        format="%Y-%m-%d",
        errors="raise",
    )

    df["value"] = pd.to_numeric(
        df["value"],
        errors="raise",
    )

    # 6. Vérification des valeurs numériques
    if not np.isfinite(df["value"].to_numpy(dtype=float)).all():
        raise ValueError("Valeurs numériques non finies")

    # 7. Recherche des doublons
    if df.duplicated(subset=KEY_COLUMNS).any():
        raise ValueError("Observations ALM dupliquées")

    # 8. Tri
    return df.sort_values(KEY_COLUMNS).reset_index(drop=True)


def load_all_alm_csv() -> pd.DataFrame:
    """Charge et consolide les différentes sources ALM."""

    dataframes = []

    for file_path in SOURCE_FILES:
        print(f"Lecture du fichier : {file_path.name}")

        df = load_alm_csv(file_path)

        print(f"Observations validées : {len(df)}")

        dataframes.append(df)

    # Consolidation des sources
    combined_df = pd.concat(dataframes, ignore_index=True)

    # Contrôle des doublons entre fichiers
    if combined_df.duplicated(subset=KEY_COLUMNS).any():
        raise ValueError("Doublons détectés entre les sources ALM")

    # Vérification des unités par indicateur
    units_per_indicator = combined_df.groupby("indicator")["unit"].nunique()

    if (units_per_indicator > 1).any():
        raise ValueError("Unités incohérentes pour un indicateur")

    return combined_df.sort_values(KEY_COLUMNS).reset_index(drop=True)


if __name__ == "__main__":

    observations = load_all_alm_csv()

    print("\nIngestion multi-source réussie")
    print(f"Total : {len(observations)} observations")

    print("\nObservations par indicateur :")
    print(observations.groupby("indicator").size())
