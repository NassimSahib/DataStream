
import pandas as pd


SCENARIOS = ["BASE", "RATE_UP_200BP"]


def calculate_alm_report(
    df: pd.DataFrame,
    indicator: str,
) -> pd.DataFrame:
    """Calcule les variations d'un indicateur ALM par scénario."""

    # 1. Sélection de l'indicateur
    selected_df = df.loc[
        df["indicator"] == indicator
    ].copy()

    if selected_df.empty:
        raise ValueError(
            f"Aucune observation pour l'indicateur {indicator}"
        )

    # 2. Vérification des unités
    if selected_df["unit"].nunique() != 1:
        raise ValueError(
            f"Unités incohérentes pour {indicator}"
        )

    # 3. Vérification des doublons
    keys = ["observation_date", "entity", "scenario"]

    if selected_df.duplicated(subset=keys).any():
        raise ValueError(
            f"Observations dupliquées pour {indicator}"
        )

    # 4. Transformation des scénarios en colonnes
    report = selected_df.pivot(
        index=["observation_date", "entity"],
        columns="scenario",
        values="value",
    )

    # 5. Vérification des scénarios attendus
    missing = set(SCENARIOS) - set(report.columns)

    if missing:
        raise ValueError(
            f"Scénarios manquants pour {indicator} : {sorted(missing)}"
        )

    report = report[SCENARIOS].copy()

    # 6. Vérification des paires de scénarios
    if report.isna().any().any():
        raise ValueError(
            f"Paires de scénarios incomplètes pour {indicator}"
        )

    # 7. Variation absolue
    report["delta_value"] = (
        report["RATE_UP_200BP"] - report["BASE"]
    )

    # 8. Variation relative
    report["delta_pct"] = float("nan")

    valid_base = report["BASE"] != 0

    report.loc[valid_base, "delta_pct"] = (
        report.loc[valid_base, "delta_value"]
        / report.loc[valid_base, "BASE"]
        * 100
    )

    # 9. Préparation du résultat
    report = report.reset_index()

    report["indicator"] = indicator
    report["unit"] = selected_df["unit"].iloc[0]

    return report.sort_values(
        ["observation_date", "entity"]
    ).reset_index(drop=True)


if __name__ == "__main__":

    from src.ingestion import load_all_alm_csv

    observations = load_all_alm_csv()

    for indicator in ["EVE", "NII"]:

        report = calculate_alm_report(
            observations,
            indicator,
        )

        print(f"\nREPORTING {indicator}")
        print(report.tail(5).to_string(index=False))
