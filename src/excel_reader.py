from __future__ import annotations

from dataclasses import dataclass
from typing import BinaryIO
import re
import unicodedata

import pandas as pd


REQUIRED_SHEETS = ("Bilans", "RZiS", "RPP")


FIELD_MAP = {
    "total_assets": ("Bilans", ("Aktywa razem",)),
    "fixed_assets": ("Bilans", ("A. Aktywa trwałe",)),
    "current_assets": ("Bilans", ("B. Aktywa obrotowe",)),
    "inventories": ("Bilans", ("I. Zapasy",)),
    "short_term_receivables": ("Bilans", ("II. Należności krótkoterminowe",)),
    "cash": ("Bilans", ("c) Środki pieniężne i inne aktywa pieniężne",)),
    "short_term_prepayments": ("Bilans", ("IV. Krótkoterminowe rozliczenia międzyokresowe",)),
    "equity": ("Bilans", ("A. Kapitał (fundusz) własny",)),
    "share_capital": ("Bilans", ("I. Kapitał (fundusz) podstawowy",)),
    "liabilities_and_provisions": ("Bilans", ("B. Zobowiązania i rezerwy na zobowiązania",)),
    "long_term_liabilities": ("Bilans", ("II. Zobowiązania długoterminowe",)),
    "short_term_liabilities": ("Bilans", ("III. Zobowiązania krótkoterminowe",)),
    "revenue": (
        "RZiS",
        (
            "A. Przychody netto ze sprzedaży produktów, towarów i materiałów, w tym:",
            "A. Przychody netto ze sprzedaży i zrównane z nimi, w tym:",
        ),
    ),
    "gross_profit": (
        "RZiS",
        (
            "C. Zysk (strata) brutto ze sprzedaży (A–B)",
            "C. Zysk (strata) ze sprzedaży (A–B)",
        ),
    ),
    "sales_profit": (
        "RZiS",
        (
            "F. Zysk (strata) ze sprzedaży (C–D–E)",
            "C. Zysk (strata) ze sprzedaży (A–B)",
        ),
    ),
    "other_operating_revenue": (
        "RZiS",
        (
            "G. Pozostałe przychody operacyjne",
            "D. Pozostałe przychody operacyjne",
        ),
    ),
    "operating_profit": (
        "RZiS",
        (
            "I. Zysk (strata) z działalności operacyjnej (F+G–H)",
            "F. Zysk (strata) z działalności operacyjnej (C+D–E)",
        ),
    ),
    "financial_revenue": (
        "RZiS",
        (
            "J. Przychody finansowe",
            "G. Przychody finansowe",
        ),
    ),
    "profit_before_tax": (
        "RZiS",
        (
            "L. Zysk (strata) brutto (I+J–K)",
            "I. Zysk (strata) brutto (F+G–H)",
        ),
    ),
    "income_tax": (
        "RZiS",
        (
            "M. Podatek dochodowy",
            "J. Podatek dochodowy",
        ),
    ),
    "net_profit": (
        "RZiS",
        (
            "O. Zysk (strata) netto (L–M–N)",
            "L. Zysk (strata) netto (I–J–K)",
        ),
    ),
    "operating_cash_flow": ("RPP", ("III. Przepływy pieniężne netto z działalności operacyjnej (I±II)",)),
    "capex": ("RPP", ("1. Nabycie wartości niematerialnych i prawnych oraz rzeczowych aktywów trwałych",)),
    "investing_cash_flow": ("RPP", ("III. Przepływy pieniężne netto z działalności inwestycyjnej (I–II)",)),
    "dividends_paid": ("RPP", ("2. Dywidendy i inne wypłaty na rzecz właścicieli",)),
    "interest_paid": ("RPP", ("8. Odsetki",)),
    "financing_cash_flow": ("RPP", ("III. Przepływy pieniężne netto z działalności finansowej (I–II)",)),
    "cash_flow_total": ("RPP", ("D. Przepływy pieniężne netto razem (A.III±B.III±C.III)",)),
    "cash_end": ("RPP", ("G. Środki pieniężne na koniec okresu (F±D), w tym:",)),
}


FIELD_LABELS = {
    "total_assets": "Aktywa razem",
    "fixed_assets": "Aktywa trwałe",
    "current_assets": "Aktywa obrotowe",
    "inventories": "Zapasy",
    "short_term_receivables": "Należności krótkoterminowe",
    "cash": "Środki pieniężne",
    "short_term_prepayments": "Krótkoterminowe rozliczenia międzyokresowe",
    "equity": "Kapitał własny",
    "share_capital": "Kapitał podstawowy",
    "liabilities_and_provisions": "Zobowiązania i rezerwy",
    "long_term_liabilities": "Zobowiązania długoterminowe",
    "short_term_liabilities": "Zobowiązania krótkoterminowe",
    "revenue": "Przychody netto ze sprzedaży",
    "gross_profit": "Zysk brutto ze sprzedaży",
    "sales_profit": "Zysk ze sprzedaży",
    "other_operating_revenue": "Pozostałe przychody operacyjne",
    "operating_profit": "Zysk operacyjny",
    "financial_revenue": "Przychody finansowe",
    "profit_before_tax": "Zysk brutto",
    "income_tax": "Podatek dochodowy",
    "net_profit": "Zysk netto",
    "operating_cash_flow": "Przepływy operacyjne",
    "capex": "Nabycie WNiP oraz rzeczowych aktywów trwałych",
    "investing_cash_flow": "Przepływy inwestycyjne",
    "dividends_paid": "Dywidendy i inne wypłaty dla właścicieli",
    "interest_paid": "Odsetki",
    "financing_cash_flow": "Przepływy finansowe",
    "cash_flow_total": "Przepływy pieniężne netto razem",
    "cash_end": "Środki pieniężne na koniec okresu",
}


@dataclass(frozen=True)
class FinancialStatement:
    years: list[int]
    values: dict[str, dict[int, float]]

    def get(self, field: str, year: int) -> float:
        return self.values.get(field, {}).get(year, 0.0)

    def to_frame(self) -> pd.DataFrame:
        rows = []
        for field, yearly_values in self.values.items():
            row = {"Pozycja": FIELD_LABELS.get(field, field)}
            for year in self.years:
                row[year] = yearly_values.get(year)
            rows.append(row)
        return pd.DataFrame(rows)


def read_financial_statement(file: str | BinaryIO) -> FinancialStatement:
    workbook = pd.read_excel(file, sheet_name=None, header=None, engine="openpyxl")
    missing = [sheet for sheet in REQUIRED_SHEETS if sheet not in workbook]
    if missing:
        raise ValueError(f"Brak wymaganych arkuszy: {', '.join(missing)}")

    sheet_data = {name: _prepare_sheet(df) for name, df in workbook.items() if name in REQUIRED_SHEETS}
    years = _detect_years(sheet_data)
    values: dict[str, dict[int, float]] = {}

    for field, (sheet_name, labels) in FIELD_MAP.items():
        values[field] = _extract_values(sheet_data[sheet_name], labels, years)

    return FinancialStatement(years=years, values=values)


def _prepare_sheet(df: pd.DataFrame) -> pd.DataFrame:
    return df.dropna(how="all").reset_index(drop=True)


def _detect_years(sheet_data: dict[str, pd.DataFrame]) -> list[int]:
    for df in sheet_data.values():
        for _, row in df.head(8).iterrows():
            years = []
            for value in row.iloc[1:]:
                if pd.isna(value):
                    continue
                if isinstance(value, (int, float)) and 1900 <= int(value) <= 2100:
                    years.append(int(value))
            if years:
                return years
    raise ValueError("Nie znaleziono lat w nagłówku sprawozdania.")


def _extract_values(df: pd.DataFrame, labels: tuple[str, ...], years: list[int]) -> dict[int, float]:
    source_labels = df.iloc[:, 0].fillna("").astype(str)
    normalized_source = source_labels.map(_normalize)
    normalized_source_without_codes = normalized_source.map(_remove_leading_code)

    for label in labels:
        normalized_label = _normalize(label)
        exact_matches = normalized_source[normalized_source == normalized_label]
        if not exact_matches.empty:
            return _row_values(df.loc[exact_matches.index[0]], years)

    for label in labels:
        normalized_label_without_code = _remove_leading_code(_normalize(label))
        exact_matches = normalized_source_without_codes[normalized_source_without_codes == normalized_label_without_code]
        if not exact_matches.empty:
            return _row_values(df.loc[exact_matches.index[0]], years)

    for label in labels:
        normalized_label = _normalize(label)
        contains_matches = normalized_source[normalized_source.str.contains(re.escape(normalized_label), regex=True)]
        if not contains_matches.empty:
            return _row_values(df.loc[contains_matches.index[0]], years)

    raise ValueError(f"Nie znaleziono pozycji: {' / '.join(labels)}")


def _row_values(row: pd.Series, years: list[int]) -> dict[int, float]:
    extracted = {}
    for idx, year in enumerate(years, start=1):
        extracted[year] = _to_float(row.iloc[idx])
    return extracted


def _to_float(value: object) -> float:
    if pd.isna(value):
        return 0.0
    if isinstance(value, str):
        cleaned = value.replace(" ", "").replace(",", ".")
        return float(cleaned) if cleaned else 0.0
    return float(value)


def _normalize(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    normalized = "".join(char for char in normalized if not unicodedata.combining(char))
    normalized = normalized.lower()
    normalized = normalized.replace("–", "-").replace("±", "+/-")
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip()


def _remove_leading_code(value: str) -> str:
    value = re.sub(r"^[a-z]\.\s+", "", value)
    value = re.sub(r"^[ivxlcdm]+\.\s+", "", value)
    value = re.sub(r"^\d+\.\s+", "", value)
    value = re.sub(r"^[a-z]\)\s+", "", value)
    return value.strip()
