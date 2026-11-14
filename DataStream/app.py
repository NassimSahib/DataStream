
from io import BytesIO

import pandas as pd
import plotly.express as px
import streamlit as st

from src.reporting import (
    get_available_indicators,
    get_alm_report,
)


# --------------------------------------------------
# CONFIGURATION GÉNÉRALE
# --------------------------------------------------

st.set_page_config(
    page_title="DataStream ALM",
    page_icon="📊",
    layout="wide",
)

st.title("DataStream | Tableau de bord ALM")
st.caption(
    "Suivi des indicateurs de risques financiers "
    "- Données de démonstration"
)


# --------------------------------------------------
# CHARGEMENT DES DONNÉES
# --------------------------------------------------

@st.cache_data(ttl=60)
def load_indicators():
    return get_available_indicators()


@st.cache_data(ttl=60)
def load_report(indicator: str):
    return get_alm_report(indicator)


try:
    available_indicators = load_indicators()

except Exception as exc:
    st.error("Impossible de récupérer les indicateurs depuis PostgreSQL.")
    st.exception(exc)
    st.stop()


if not available_indicators:
    st.warning("Aucun indicateur disponible dans la base.")
    st.stop()


# --------------------------------------------------
# FILTRES
# --------------------------------------------------

st.sidebar.header("Filtres du reporting")

indicator_labels = {
    "EVE": "EVE - Valeur économique",
    "NII": "NII - Marge nette d'intérêts",
}

selected_indicator = st.sidebar.selectbox(
    "Indicateur financier",
    available_indicators,
    format_func=lambda code: indicator_labels.get(code, code),
)

try:
    df = load_report(selected_indicator)

except Exception as exc:
    st.error("Impossible de générer le reporting demandé.")
    st.exception(exc)
    st.stop()


if df.empty:
    st.warning("Aucune observation disponible.")
    st.stop()


entities = sorted(df["entity"].unique())

selected_entity = st.sidebar.selectbox(
    "Entité bancaire",
    entities,
)

entity_df = df[
    df["entity"] == selected_entity
].copy()

min_date = entity_df["observation_date"].min().date()
max_date = entity_df["observation_date"].max().date()

date_range = st.sidebar.date_input(
    "Période d'observation",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
    format="DD/MM/YYYY",
)

if not isinstance(date_range, tuple) or len(date_range) != 2:
    st.info("Sélectionne une date de début et de fin.")
    st.stop()

start_date, end_date = date_range

filtered_df = entity_df[
    (entity_df["observation_date"].dt.date >= start_date)
    & (entity_df["observation_date"].dt.date <= end_date)
].copy()

if filtered_df.empty:
    st.warning("Aucune donnée pour la période sélectionnée.")
    st.stop()

filtered_df = filtered_df.sort_values("observation_date")

unit = filtered_df["unit"].iloc[0]
unit_label = "M€" if unit == "EUR_M" else unit

indicator_name = indicator_labels.get(
    selected_indicator,
    selected_indicator,
)


# --------------------------------------------------
# INDICATEURS CLÉS
# --------------------------------------------------

st.subheader(f"Indicateurs clés - {indicator_name}")

latest = filtered_df.iloc[-1]

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Scénario de référence",
    f"{latest['BASE']:,.1f} {unit_label}",
)

col2.metric(
    "Scénario de choc (+200 pb)",
    f"{latest['RATE_UP_200BP']:,.1f} {unit_label}",
)

col3.metric(
    "Variation absolue",
    f"{latest['delta_value']:,.1f} {unit_label}",
)

col4.metric(
    "Variation relative",
    f"{latest['delta_pct']:.2f} %",
)

st.caption(
    f"Dernière observation sélectionnée : "
    f"{latest['observation_date']:%d/%m/%Y}"
)


# --------------------------------------------------
# GRAPHIQUE HISTORIQUE
# --------------------------------------------------

st.subheader("Évolution historique")

chart_df = filtered_df.melt(
    id_vars=["observation_date"],
    value_vars=["BASE", "RATE_UP_200BP"],
    var_name="Scénario",
    value_name="Valeur",
)

chart_df["Scénario"] = chart_df["Scénario"].replace({
    "BASE": "Référence",
    "RATE_UP_200BP": "Choc +200 pb",
})

fig = px.line(
    chart_df,
    x="observation_date",
    y="Valeur",
    color="Scénario",
    markers=True,
    title=f"Évolution de {selected_indicator} par scénario",
)

fig.update_layout(
    xaxis_title="Date d'observation",
    yaxis_title=f"Valeur ({unit_label})",
    legend_title="Scénario",
    hovermode="x unified",
)

st.plotly_chart(fig, use_container_width=True)


# --------------------------------------------------
# TABLEAU HISTORIQUE
# --------------------------------------------------

st.subheader("Historique des observations")

display_df = filtered_df[
    [
        "observation_date",
        "entity",
        "BASE",
        "RATE_UP_200BP",
        "delta_value",
        "delta_pct",
    ]
].rename(
    columns={
        "observation_date": "Date",
        "entity": "Entité",
        "BASE": f"Référence ({unit_label})",
        "RATE_UP_200BP": f"Choc +200 pb ({unit_label})",
        "delta_value": f"Variation ({unit_label})",
        "delta_pct": "Variation (%)",
    }
).copy()

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True,
)


# --------------------------------------------------
# EXPORT EXCEL
# --------------------------------------------------

st.subheader("Export du reporting")

output = BytesIO()

with pd.ExcelWriter(output, engine="openpyxl") as writer:
    display_df.to_excel(
        writer,
        sheet_name=f"Reporting {selected_indicator}",
        index=False,
    )

st.download_button(
    label=f"Télécharger le reporting {selected_indicator}",
    data=output.getvalue(),
    file_name=f"datastream_{selected_indicator.lower()}_reporting.xlsx",
    mime=(
        "application/vnd.openxmlformats-officedocument."
        "spreadsheetml.sheet"
    ),
)


# --------------------------------------------------
# PIED DE PAGE
# --------------------------------------------------

st.divider()

st.caption(
    "DataStream ALM - Prototype de reporting financier. "
    "Les données présentées sont entièrement fictives."
)
