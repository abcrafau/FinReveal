from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from src.excel_reader import FinancialStatement


@dataclass(frozen=True)
class RatioResult:
    category: str
    label: str
    value: float
    format: str
    formula: str


def calculate_ratios(statement: FinancialStatement, year: int | None = None) -> list[RatioResult]:
    year = year or statement.years[0]

    revenue = statement.get("revenue", year)
    other_operating_revenue = statement.get("other_operating_revenue", year)
    financial_revenue = statement.get("financial_revenue", year)
    total_income = revenue + other_operating_revenue + financial_revenue

    net_profit = statement.get("net_profit", year)
    profit_before_tax = statement.get("profit_before_tax", year)
    total_assets = statement.get("total_assets", year)
    fixed_assets = statement.get("fixed_assets", year)
    current_assets = statement.get("current_assets", year)
    inventories = statement.get("inventories", year)
    short_term_prepayments = statement.get("short_term_prepayments", year)
    short_term_receivables = statement.get("short_term_receivables", year)
    cash = statement.get("cash", year)
    equity = statement.get("equity", year)
    share_capital = statement.get("share_capital", year)
    liabilities = statement.get("liabilities_and_provisions", year)
    long_term_liabilities = statement.get("long_term_liabilities", year)
    short_term_liabilities = statement.get("short_term_liabilities", year)
    operating_cash_flow = statement.get("operating_cash_flow", year)
    capex = statement.get("capex", year)
    dividends_paid = statement.get("dividends_paid", year)
    interest_paid = statement.get("interest_paid", year)

    inv_days = _safe_divide(inventories * 365, revenue)
    receivables_days = _safe_divide(short_term_receivables * 365, revenue)
    liabilities_days = _safe_divide(short_term_liabilities * 365, revenue)

    definitions: list[tuple[str, str, float, str, str]] = [
        (
            "Rentowność",
            "ROS",
            _safe_divide(net_profit, revenue),
            "percent",
            "Zysk (strata) netto / Przychody netto ze sprzedaży",
        ),
        (
            "Rentowność",
            "Wskaźnik rentowności sprzedaży brutto",
            _safe_divide(profit_before_tax, total_income),
            "percent",
            "Zysk (strata) brutto / (Przychody netto ze sprzedaży + Pozostałe przychody operacyjne + Przychody finansowe)",
        ),
        (
            "Rentowność",
            "Wskaźnik rentowności sprzedaży netto",
            _safe_divide(net_profit, total_income),
            "percent",
            "Zysk (strata) netto / (Przychody netto ze sprzedaży + Pozostałe przychody operacyjne + Przychody finansowe)",
        ),
        (
            "Rentowność",
            "ROA",
            _safe_divide(net_profit, total_assets),
            "percent",
            "Zysk (strata) netto / Aktywa razem",
        ),
        (
            "Rentowność",
            "ROE",
            _safe_divide(net_profit, equity),
            "percent",
            "Zysk (strata) netto / Kapitał (fundusz) własny",
        ),
        (
            "Rentowność",
            "Wskaźnik rentowności kapitału podstawowego",
            _safe_divide(net_profit, share_capital),
            "percent",
            "Zysk (strata) netto / Kapitał (fundusz) podstawowy",
        ),
        (
            "Płynność",
            "I poziom płynności (wskaźnik płynności gotówkowej)",
            _safe_divide(cash, short_term_liabilities),
            "number",
            "Środki pieniężne i inne aktywa pieniężne / Zobowiązania krótkoterminowe",
        ),
        (
            "Płynność",
            "II poziom płynności (wskaźnik szybkiej płynności finansowej)",
            _safe_divide(current_assets - inventories - short_term_prepayments, short_term_liabilities),
            "number",
            "(Aktywa obrotowe - Zapasy - Krótkoterminowe rozliczenia międzyokresowe) / Zobowiązania krótkoterminowe",
        ),
        (
            "Płynność",
            "III poziom płynności (wskaźnik bieżącej płynności finansowej)",
            _safe_divide(current_assets, short_term_liabilities),
            "number",
            "Aktywa obrotowe / Zobowiązania krótkoterminowe",
        ),
        (
            "Płynność",
            "Kapitał obrotowy netto",
            current_assets - short_term_liabilities,
            "money",
            "Aktywa obrotowe - Zobowiązania krótkoterminowe",
        ),
        (
            "Płynność",
            "Wskaźnik ogólnej wystarczalności gotówki",
            _safe_divide(operating_cash_flow, capex + dividends_paid + interest_paid),
            "number",
            "Przepływy pieniężne netto z działalności operacyjnej / (Nabycie WNiP i rzeczowych aktywów trwałych + Dywidendy i inne wypłaty + Odsetki)",
        ),
        (
            "Płynność",
            "Wskaźnik wydajności gotówkowej majątku",
            _safe_divide(operating_cash_flow, total_assets),
            "percent",
            "Przepływy pieniężne netto z działalności operacyjnej / Aktywa razem",
        ),
        (
            "Zadłużenie",
            "Wskaźnik ogólnego zadłużenia",
            _safe_divide(liabilities, total_assets),
            "percent",
            "Zobowiązania i rezerwy na zobowiązania / Aktywa razem",
        ),
        (
            "Zadłużenie",
            "Wskaźnik pokrycia majątku kapitałem własnym",
            _safe_divide(equity, total_assets),
            "percent",
            "Kapitał (fundusz) własny / Aktywa razem",
        ),
        (
            "Zadłużenie",
            "Wskaźnik struktury zobowiązań",
            _safe_divide(long_term_liabilities, liabilities),
            "percent",
            "Zobowiązania długoterminowe / Zobowiązania i rezerwy na zobowiązania",
        ),
        (
            "Sprawność działania",
            "Wskaźnik obrotowości majątku",
            _safe_divide(total_income, total_assets),
            "number",
            "(Przychody netto ze sprzedaży + Pozostałe przychody operacyjne + Przychody finansowe) / Aktywa razem",
        ),
        (
            "Sprawność działania",
            "Wskaźnik obrotowości majątku trwałego",
            _safe_divide(total_income, fixed_assets),
            "number",
            "(Przychody netto ze sprzedaży + Pozostałe przychody operacyjne + Przychody finansowe) / Aktywa trwałe",
        ),
        (
            "Sprawność działania",
            "Wskaźnik obrotowości majątku obcego",
            _safe_divide(total_income, current_assets),
            "number",
            "(Przychody netto ze sprzedaży + Pozostałe przychody operacyjne + Przychody finansowe) / Aktywa obrotowe",
        ),
        (
            "Sprawność działania",
            "Wskaźnik rotacji zapasów",
            _safe_divide(revenue, inventories),
            "number",
            "Przychody netto ze sprzedaży / Zapasy",
        ),
        (
            "Sprawność działania",
            "Wskaźnik cyklu obrotowości zapasów w dniach",
            inv_days,
            "days",
            "Zapasy * 365 / Przychody netto ze sprzedaży",
        ),
        (
            "Sprawność działania",
            "Wskaźnik cyklu inkasa należności w dniach",
            receivables_days,
            "days",
            "Należności krótkoterminowe * 365 / Przychody netto ze sprzedaży",
        ),
        (
            "Sprawność działania",
            "Wskaźnik okresu spłaty zobowiązań w dniach",
            liabilities_days,
            "days",
            "Zobowiązania krótkoterminowe * 365 / Przychody netto ze sprzedaży",
        ),
        (
            "Sprawność działania",
            "Cykl środków pieniężnych",
            inv_days + receivables_days - liabilities_days,
            "days",
            "Wskaźnik cyklu obrotowości zapasów w dniach + Wskaźnik cyklu inkasa należności w dniach - Wskaźnik okresu spłaty zobowiązań w dniach",
        ),
    ]

    return [
        RatioResult(category=category, label=label, value=value, format=fmt, formula=formula)
        for category, label, value, fmt, formula in definitions
    ]


def format_ratio_value(value: float, fmt: str) -> str:
    formatters: dict[str, Callable[[float], str]] = {
        "percent": lambda number: f"{number:.1%}".replace(".", ","),
        "number": lambda number: f"{number:.2f}".replace(".", ","),
        "money": lambda number: f"{number:,.0f} PLN".replace(",", " "),
        "days": lambda number: f"{number:.1f} dni".replace(".", ","),
    }
    return formatters.get(fmt, lambda number: str(number))(value)


def _safe_divide(numerator: float, denominator: float) -> float:
    return numerator / denominator if denominator else 0.0
