from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from src.excel_reader import FinancialStatement


@dataclass(frozen=True)
class NamedFinancialStatement:
    name: str
    statement: FinancialStatement


def merge_financial_statements(statements: Iterable[FinancialStatement]) -> FinancialStatement:
    named_statements = [
        NamedFinancialStatement(name=f"Plik {index}", statement=statement)
        for index, statement in enumerate(statements, start=1)
    ]
    return merge_named_financial_statements(named_statements)


def merge_named_financial_statements(statements: Iterable[NamedFinancialStatement]) -> FinancialStatement:
    merged_values: dict[str, dict[int, float]] = {}
    merged_years: set[int] = set()
    year_sources: dict[int, tuple[int, str]] = {}
    seen_report_years: dict[int, str] = {}

    sorted_statements = sorted(
        statements,
        key=lambda item: _report_year(item.statement),
    )

    for named_statement in sorted_statements:
        statement = named_statement.statement
        report_year = _report_year(statement)

        if report_year in seen_report_years:
            raise ValueError(
                f"Pliki '{seen_report_years[report_year]}' oraz '{named_statement.name}' "
                f"dotyczą tego samego roku sprawozdania: {report_year}. "
                "Usuń jeden z nich, aby nie zdublować danych."
            )
        seen_report_years[report_year] = named_statement.name

        merged_years.update(statement.years)
        for field, yearly_values in statement.values.items():
            merged_values.setdefault(field, {})
            for year, value in yearly_values.items():
                current_source = year_sources.get(year)
                if current_source and current_source[0] > report_year:
                    continue
                merged_values[field][year] = value
                year_sources[year] = (report_year, named_statement.name)

    if not merged_years:
        raise ValueError("Nie znaleziono żadnych okresów do analizy.")

    return FinancialStatement(
        years=sorted(merged_years, reverse=True),
        values=merged_values,
    )


def _report_year(statement: FinancialStatement) -> int:
    if not statement.years:
        raise ValueError("Sprawozdanie nie zawiera okresów.")
    return max(statement.years)
