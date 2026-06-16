from __future__ import annotations

import base64
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
from PIL import Image

from src.excel_reader import FIELD_LABELS, read_financial_statement
from src.ratios import calculate_ratios, format_ratio_value
from src.statement_merge import NamedFinancialStatement, merge_named_financial_statements
from src.xml_reader import read_xml_financial_statement


APP_ICON = Image.open(Path(__file__).parent / "assets" / "app_icon.png")
ASSETS_DIR = Path(__file__).parent / "assets"


def image_data_uri(path: Path) -> str:
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def render_footer() -> None:
    st.markdown(
        """
        <div style="margin-top:3rem; padding-top:1.25rem; border-top:1px solid rgba(49,51,63,0.18); color:#5f6368; font-size:0.92rem; line-height:1.6; display:flex; justify-content:space-between; gap:1.5rem; flex-wrap:wrap;">
            <div>
                <strong>FinReveal</strong> — narzędzie do analizy sprawozdań finansowych<br>
                Autor: Rafał Kopliński<br>
                Analiza finansowa • Python • Przetwarzanie danych<br>
                © 2026
            </div>
            <div style="text-align:right; max-width:320px;">
                Masz uwagi dotyczące aplikacji?<br>
                <a href="https://forms.gle/cxUfcSjjggh8k4jC6" target="_blank" rel="noopener noreferrer" style="color:inherit; font-weight:600;">
                    Podziel się opinią!
                </a>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def format_polish_axis_value(value: float) -> str:
    def decimal(number: float) -> str:
        return f"{number:.1f}".replace(".", ",")

    abs_value = abs(value)
    if abs_value >= 1_000_000_000:
        return f"{decimal(value / 1_000_000_000)} mld"
    if abs_value >= 1_000_000:
        return f"{decimal(value / 1_000_000)} mln"
    if abs_value >= 1_000:
        return f"{decimal(value / 1_000)} tys."
    return f"{value:.0f}".replace(".", ",")


def apply_year_axis(fig, years: list[int]) -> None:
    sorted_years = sorted(years)
    fig.update_xaxes(
        type="category",
        categoryorder="array",
        categoryarray=[str(year) for year in sorted_years],
        tickmode="array",
        tickvals=[str(year) for year in sorted_years],
        ticktext=[str(year) for year in sorted_years],
        title_text="",
    )


def apply_polish_money_axis(fig, values: pd.Series) -> None:
    numeric_values = pd.to_numeric(values, errors="coerce").dropna()
    if numeric_values.empty:
        return

    min_value = min(0, numeric_values.min())
    max_value = numeric_values.max()
    tick_values = pd.Series([min_value + (max_value - min_value) * i / 5 for i in range(6)]).drop_duplicates()
    fig.update_yaxes(
        tickmode="array",
        tickvals=tick_values.tolist(),
        ticktext=[format_polish_axis_value(value) for value in tick_values],
        title_text="PLN",
    )


def apply_ratio_axis(fig, values: pd.Series, formats: pd.Series) -> None:
    numeric_values = pd.to_numeric(values, errors="coerce").dropna()
    if numeric_values.empty:
        return

    min_value = min(0, numeric_values.min())
    max_value = numeric_values.max()
    tick_values = pd.Series([min_value + (max_value - min_value) * i / 5 for i in range(6)]).drop_duplicates()
    unique_formats = set(formats.dropna().tolist())

    if unique_formats == {"percent"}:
        tick_text = [f"{value:.1%}".replace(".", ",") for value in tick_values]
    elif unique_formats == {"days"}:
        tick_text = [f"{value:.0f} dni".replace(".", ",") for value in tick_values]
    else:
        tick_text = [f"{value:.2f}".replace(".", ",") for value in tick_values]

    fig.update_yaxes(
        tickmode="array",
        tickvals=tick_values.tolist(),
        ticktext=tick_text,
        title_text="Wartość wskaźnika",
    )


st.set_page_config(
    page_title="FinReveal",
    page_icon=APP_ICON,
    layout="wide",
)

github_icon = image_data_uri(ASSETS_DIR / "github.png")
linkedin_icon = image_data_uri(ASSETS_DIR / "linkedin.png")
finreveal_logo = image_data_uri(ASSETS_DIR / "finreveal_logo_mask.png")

st.markdown(
    f"""
    <style>
        .social-icon {{
            display: block;
            width: 32px;
            height: 32px;
            color: inherit !important;
            background-color: currentColor !important;
            mask-position: center;
            mask-repeat: no-repeat;
            mask-size: contain;
            -webkit-mask-position: center;
            -webkit-mask-repeat: no-repeat;
            -webkit-mask-size: contain;
        }}

        .social-icon.linkedin {{
            mask-image: url("{linkedin_icon}");
            -webkit-mask-image: url("{linkedin_icon}");
        }}

        .social-icon.github {{
            mask-image: url("{github_icon}");
            -webkit-mask-image: url("{github_icon}");
        }}

        .app-header {{
            color: inherit;
        }}

        .app-header a,
        .app-header a:visited,
        .app-header a:hover,
        .app-header a:active {{
            color: inherit !important;
            text-decoration: none;
        }}

        .brand-lockup {{
            display: flex;
            align-items: center;
            gap: 0.75rem;
            min-width: 0;
        }}

        .brand-logo {{
            display: block;
            width: 120px;
            height: 46px;
            color: inherit !important;
            background-color: currentColor !important;
            mask-image: url("{finreveal_logo}");
            mask-position: center;
            mask-repeat: no-repeat;
            mask-size: contain;
            -webkit-mask-image: url("{finreveal_logo}");
            -webkit-mask-position: center;
            -webkit-mask-repeat: no-repeat;
            -webkit-mask-size: contain;
        }}

        .brand-lockup h1 {{
            color: inherit;
        }}
    </style>
    <div class="app-header" style="display:flex; align-items:center; justify-content:space-between; gap:1rem; margin-bottom:0.75rem;">
        <div class="brand-lockup">
            <h1 style="margin:0; padding:0;">FinReveal</h1>
            <span class="brand-logo" role="img" aria-label="FinReveal logo"></span>
        </div>
        <div style="display:flex; align-items:center; gap:0.85rem;">
            <a href="https://www.linkedin.com/in/rafal-koplinski/" target="_blank" rel="noopener noreferrer" title="LinkedIn">
                <span class="social-icon linkedin" role="img" aria-label="LinkedIn"></span>
            </a>
            <a href="https://github.com/abcrafau" target="_blank" rel="noopener noreferrer" title="GitHub">
                <span class="social-icon github" role="img" aria-label="GitHub"></span>
            </a>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.caption("Wczytaj jedno lub kilka sprawozdań finansowych w formacie Excel albo XML/XAdES.")

uploaded_files = st.file_uploader(
    "Pliki ze sprawozdaniami finansowymi",
    type=["xlsx", "xml", "xades"],
    accept_multiple_files=True,
    help=(
        "Możesz dodać kilka plików tej samej spółki z różnych okresów. "
        "Jeśli rok się powtarza, aplikacja wybierze dane z raportu o wyższym roku."
    ),
)

if not uploaded_files:
    st.info("Dodaj co najmniej jeden plik, aby rozpocząć analizę.")
    render_footer()
    st.stop()


def read_uploaded_statement(uploaded_file):
    file_name = uploaded_file.name.lower()
    if file_name.endswith((".xml", ".xades")):
        return read_xml_financial_statement(uploaded_file)
    if file_name.endswith(".xlsx"):
        return read_financial_statement(uploaded_file)
    raise ValueError(f"Nieobsługiwany format pliku: {uploaded_file.name}")


try:
    statements = [
        NamedFinancialStatement(name=file.name, statement=read_uploaded_statement(file))
        for file in uploaded_files
    ]
    statement = merge_named_financial_statements(statements)
except Exception as exc:
    st.error("Nie udało się wczytać sprawozdania. Sprawdź, czy pliki są obsługiwanymi XLSX, XML albo XAdES.")
    st.exception(exc)
    st.stop()

years = statement.years
st.caption(
    "Wczytane okresy: "
    + ", ".join(str(year) for year in years)
    + f" | Liczba plików: {len(uploaded_files)}"
)

selected_year = st.selectbox(
    "Rok analizy",
    options=years,
    index=0,
    help="Wybierz okres, dla którego aplikacja ma policzyć wskaźniki finansowe.",
)
ratios = calculate_ratios(statement, selected_year)

st.subheader(f"Podsumowanie: {selected_year}")

summary_cols = st.columns(4)
summary_items = [
    ("Przychody", statement.get("revenue", selected_year)),
    ("Zysk netto", statement.get("net_profit", selected_year)),
    ("Aktywa razem", statement.get("total_assets", selected_year)),
    ("Kapitał własny", statement.get("equity", selected_year)),
]

for col, (label, value) in zip(summary_cols, summary_items):
    col.metric(label, f"{value:,.0f} PLN".replace(",", " "))

ratio_df = pd.DataFrame(
    [
        {
            "Kategoria": ratio.category,
            "Wskaźnik": ratio.label,
            "Wartość": format_ratio_value(ratio.value, ratio.format),
            "Wzór": ratio.formula,
        }
        for ratio in ratios
    ]
)

st.subheader("Wskaźniki finansowe")
if ratio_df.empty:
    st.info("Brak kompletu danych do obliczenia wskaznikow dla wybranego roku.")
    render_footer()
    st.stop()

categories = list(dict.fromkeys(ratio_df["Kategoria"].tolist()))
tabs = st.tabs(categories)

for tab, category in zip(tabs, categories):
    with tab:
        category_df = ratio_df[ratio_df["Kategoria"] == category]
        st.dataframe(
            category_df[["Wskaźnik", "Wartość", "Wzór"]],
            use_container_width=True,
            hide_index=True,
        )

with st.expander("Wszystkie wskaźniki w jednej tabeli"):
    st.dataframe(
        ratio_df[["Kategoria", "Wskaźnik", "Wartość", "Wzór"]],
        use_container_width=True,
        hide_index=True,
    )

st.subheader("Trendy")
statement_trend_tab, ratio_trend_tab = st.tabs(["Pozycje finansowe", "Wskaźniki finansowe"])

with statement_trend_tab:
    available_statement_items = {
        FIELD_LABELS.get(field, field): field
        for field in statement.values.keys()
    }
    default_statement_items = [
        label
        for label in ["Przychody netto ze sprzedaży", "Zysk netto", "Aktywa razem", "Kapitał własny"]
        if label in available_statement_items
    ]
    selected_statement_items = st.multiselect(
        "Pozycje finansowe na wykresie",
        options=list(available_statement_items.keys()),
        default=default_statement_items,
    )

    if selected_statement_items:
        statement_trend_df = pd.DataFrame(
            [
                {
                    "Rok": str(year),
                    "Pozycja": label,
                    "Wartość": statement.get(available_statement_items[label], year),
                }
                for year in sorted(years)
                for label in selected_statement_items
            ]
        )
        statement_trend_df["Wartość formatowana"] = statement_trend_df["Wartość"].apply(
            format_polish_axis_value
        )
        fig = px.line(
            statement_trend_df,
            x="Rok",
            y="Wartość",
            color="Pozycja",
            markers=True,
            custom_data=["Wartość formatowana"],
        )
        apply_year_axis(fig, years)
        apply_polish_money_axis(fig, statement_trend_df["Wartość"])
        fig.update_traces(
            hovertemplate="Rok: %{x}<br>%{fullData.name}: %{customdata[0]}<extra></extra>",
        )
        fig.update_layout(legend_title="")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Wybierz co najmniej jedną pozycję finansową.")

with ratio_trend_tab:
    ratio_rows = []
    for year in sorted(years):
        for ratio in calculate_ratios(statement, year):
            ratio_rows.append(
                {
                    "Rok": str(year),
                    "Kategoria": ratio.category,
                    "Wskaźnik": ratio.label,
                    "Wartość": ratio.value,
                    "Format": ratio.format,
                }
            )
    ratio_trend_df = pd.DataFrame(ratio_rows)
    ratio_categories = list(dict.fromkeys(ratio_trend_df["Kategoria"].tolist()))
    selected_ratio_category = st.selectbox(
        "Kategoria wskaźników",
        options=ratio_categories,
    )
    available_ratios = ratio_trend_df.loc[
        ratio_trend_df["Kategoria"] == selected_ratio_category,
        "Wskaźnik",
    ].drop_duplicates().tolist()
    selected_ratios = st.multiselect(
        "Wskaźniki na wykresie",
        options=available_ratios,
        default=available_ratios[: min(3, len(available_ratios))],
    )

    if selected_ratios:
        selected_ratio_df = ratio_trend_df[
            (ratio_trend_df["Kategoria"] == selected_ratio_category)
            & (ratio_trend_df["Wskaźnik"].isin(selected_ratios))
        ].copy()
        selected_ratio_df["Wartość formatowana"] = selected_ratio_df.apply(
            lambda row: format_ratio_value(row["Wartość"], row["Format"]),
            axis=1,
        )
        fig = px.line(
            selected_ratio_df,
            x="Rok",
            y="Wartość",
            color="Wskaźnik",
            markers=True,
            custom_data=["Wartość formatowana"],
        )
        apply_year_axis(fig, years)
        apply_ratio_axis(fig, selected_ratio_df["Wartość"], selected_ratio_df["Format"])
        fig.update_traces(
            hovertemplate="Rok: %{x}<br>%{fullData.name}: %{customdata[0]}<extra></extra>",
        )
        fig.update_layout(legend_title="")
        st.plotly_chart(fig, use_container_width=True)

        with st.expander("Dane wskaźników na wykresie"):
            display_df = selected_ratio_df.copy()
            display_df["Wartość"] = display_df["Wartość formatowana"]
            st.dataframe(
                display_df[["Rok", "Wskaźnik", "Wartość"]],
                use_container_width=True,
                hide_index=True,
            )
    else:
        st.info("Wybierz co najmniej jeden wskaźnik.")

with st.expander("Dane rozpoznane przez aplikację"):
    extracted = statement.to_frame()
    st.dataframe(extracted, use_container_width=True)

render_footer()
