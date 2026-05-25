from __future__ import annotations

from src.excel_reader import FinancialStatement
from src.ratios import RatioResult, format_ratio_value


def build_rule_based_analysis(
    statement: FinancialStatement,
    ratios: list[RatioResult],
    year: int | None = None,
) -> list[str]:
    year = year or statement.years[0]
    ratio_map = {ratio.label: ratio for ratio in ratios}

    revenue = statement.get("revenue", year)
    net_profit = statement.get("net_profit", year)
    operating_cash_flow = statement.get("operating_cash_flow", year)

    paragraphs = [
        (
            f"W {year} roku spółka osiągnęła przychody netto ze sprzedaży na poziomie "
            f"{_money(revenue)} oraz zysk netto w wysokości {_money(net_profit)}."
        )
    ]

    ros = ratio_map.get("ROS")
    roa = ratio_map.get("ROA")
    roe = ratio_map.get("ROE")
    current_ratio = ratio_map.get("III poziom płynności (wskaźnik bieżącej płynności finansowej)")
    debt_ratio = ratio_map.get("Wskaźnik ogólnego zadłużenia")
    cash_cycle = ratio_map.get("Cykl środków pieniężnych")

    if ros and roa and roe:
        paragraphs.append(
            "Rentowność według nowych wzorów wynosi: "
            f"ROS {format_ratio_value(ros.value, ros.format)}, "
            f"ROA {format_ratio_value(roa.value, roa.format)} oraz "
            f"ROE {format_ratio_value(roe.value, roe.format)}."
        )

    if current_ratio and debt_ratio:
        paragraphs.append(
            "Płynność i zadłużenie można ocenić przez: "
            f"III poziom płynności {format_ratio_value(current_ratio.value, current_ratio.format)} oraz "
            f"wskaźnik ogólnego zadłużenia {format_ratio_value(debt_ratio.value, debt_ratio.format)}."
        )

    if cash_cycle:
        paragraphs.append(
            f"Przepływy operacyjne wyniosły {_money(operating_cash_flow)}, a cykl środków pieniężnych "
            f"według przyjętego wzoru wynosi {format_ratio_value(cash_cycle.value, cash_cycle.format)}."
        )

    paragraphs.append(
        "Tabela wskaźników zawiera pełny zestaw z przekazanego pliku: rentowność, płynność, "
        "zadłużenie oraz sprawność działania. W kolejnym etapie warto dodać progi interpretacyjne "
        "dla branży, żeby aplikacja automatycznie oceniała, czy wynik jest mocny, neutralny czy ryzykowny."
    )
    return paragraphs


def _money(value: float) -> str:
    return f"{value:,.0f} PLN".replace(",", " ")
