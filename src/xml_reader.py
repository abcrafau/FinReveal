from __future__ import annotations

from typing import BinaryIO
import xml.etree.ElementTree as ET

from src.excel_reader import FinancialStatement


XML_FIELD_PATHS = {
    "total_assets": "Bilans/Aktywa",
    "fixed_assets": "Bilans/Aktywa/Aktywa_A",
    "current_assets": "Bilans/Aktywa/Aktywa_B",
    "inventories": "Bilans/Aktywa/Aktywa_B/Aktywa_B_I",
    "short_term_receivables": "Bilans/Aktywa/Aktywa_B/Aktywa_B_II",
    "cash": "Bilans/Aktywa/Aktywa_B/Aktywa_B_III/Aktywa_B_III_1/Aktywa_B_III_1_C",
    "short_term_prepayments": "Bilans/Aktywa/Aktywa_B/Aktywa_B_IV",
    "equity": "Bilans/Pasywa/Pasywa_A",
    "share_capital": "Bilans/Pasywa/Pasywa_A/Pasywa_A_I",
    "liabilities_and_provisions": "Bilans/Pasywa/Pasywa_B",
    "long_term_liabilities": "Bilans/Pasywa/Pasywa_B/Pasywa_B_II",
    "short_term_liabilities": "Bilans/Pasywa/Pasywa_B/Pasywa_B_III",
    "revenue": "RZiS/RZiSPor/A",
    "gross_profit": "RZiS/RZiSPor/C",
    "sales_profit": "RZiS/RZiSPor/C",
    "other_operating_revenue": "RZiS/RZiSPor/D",
    "operating_profit": "RZiS/RZiSPor/F",
    "financial_revenue": "RZiS/RZiSPor/G",
    "profit_before_tax": "RZiS/RZiSPor/I",
    "income_tax": "RZiS/RZiSPor/J",
    "net_profit": "RZiS/RZiSPor/L",
    "operating_cash_flow": "RachPrzeplywow/PrzeplywyPosr/A/A_III",
    "capex": "RachPrzeplywow/PrzeplywyPosr/B/B_II/B_II_1",
    "investing_cash_flow": "RachPrzeplywow/PrzeplywyPosr/B/B_III",
    "dividends_paid": "RachPrzeplywow/PrzeplywyPosr/C/C_II/C_II_2",
    "interest_paid": "RachPrzeplywow/PrzeplywyPosr/C/C_II/C_II_8",
    "financing_cash_flow": "RachPrzeplywow/PrzeplywyPosr/C/C_III",
    "cash_flow_total": "RachPrzeplywow/PrzeplywyPosr/D",
    "cash_end": "RachPrzeplywow/PrzeplywyPosr/G",
}


def read_xml_financial_statement(file: str | BinaryIO) -> FinancialStatement:
    root = _read_xml_root(file)
    years = _detect_years(root)
    values = {
        field: _extract_year_values(root, path, years)
        for field, path in XML_FIELD_PATHS.items()
    }
    return FinancialStatement(years=years, values=values)


def _read_xml_root(file: str | BinaryIO) -> ET.Element:
    if isinstance(file, str):
        return ET.parse(file).getroot()

    data = file.read()
    if hasattr(file, "seek"):
        file.seek(0)
    return ET.fromstring(data)


def _detect_years(root: ET.Element) -> list[int]:
    period_end = _find_first_text(root, "OkresDo") or _find_first_text(root, "DataDo")
    if not period_end:
        raise ValueError("Nie znaleziono daty końca okresu w XML.")

    current_year = int(period_end[:4])
    return [current_year, current_year - 1]


def _extract_year_values(root: ET.Element, path: str, years: list[int]) -> dict[int, float]:
    node = _find_by_local_path(root, path)
    if node is None:
        raise ValueError(f"Nie znaleziono ścieżki XML: {path}")

    values = {}
    kwota_names = ("KwotaA", "KwotaB")
    for year, kwota_name in zip(years, kwota_names):
        kwota_node = _find_direct_child(node, kwota_name)
        values[year] = _node_to_float(kwota_node)
    return values


def _find_by_local_path(root: ET.Element, path: str) -> ET.Element | None:
    parts = path.split("/")
    candidates = [element for element in root.iter() if _local_name(element.tag) == parts[0]]
    for candidate in candidates:
        current = candidate
        matched = True
        for part in parts[1:]:
            current = _find_direct_child(current, part)
            if current is None:
                matched = False
                break
        if matched:
            return current
    return None


def _find_direct_child(node: ET.Element, local_name: str) -> ET.Element | None:
    for child in list(node):
        if _local_name(child.tag) == local_name:
            return child
    return None


def _find_first_text(root: ET.Element, local_name: str) -> str | None:
    for element in root.iter():
        if _local_name(element.tag) == local_name:
            text = (element.text or "").strip()
            if text:
                return text
    return None


def _node_to_float(node: ET.Element | None) -> float:
    if node is None:
        return 0.0

    text = (node.text or "").strip()
    if text:
        return _to_float(text)

    nested_kwota = _find_direct_child(node, _local_name(node.tag))
    if nested_kwota is not None:
        return _node_to_float(nested_kwota)

    return 0.0


def _to_float(value: str) -> float:
    cleaned = value.replace(" ", "").replace(",", ".")
    return float(cleaned) if cleaned else 0.0


def _local_name(tag: str) -> str:
    return tag.split("}", 1)[-1]
