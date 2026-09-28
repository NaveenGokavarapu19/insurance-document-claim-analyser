"""Reusable helpers for reading and extracting content from PDFs."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pdfplumber


def load_pdf(pdf_source: str | Path, password: str | None = None) -> pdfplumber.PDF:
    """Open a PDF source and return a pdfplumber PDF object."""
    return pdfplumber.open(pdf_source, password=password)


def get_pdf_page_count(pdf_source: str | Path, password: str | None = None) -> int:
    """Return the total number of pages in a PDF."""
    with load_pdf(pdf_source, password=password) as pdf:
        return len(pdf.pages)


def get_pdf_metadata(pdf_source: str | Path, password: str | None = None) -> dict[str, Any]:
    """Return the metadata dictionary for a PDF document."""
    with load_pdf(pdf_source, password=password) as pdf:
        return dict(pdf.metadata or {})


def extract_text_by_page(pdf_source: str | Path, password: str | None = None) -> list[str]:
    """Return a list of extracted text strings, one per page."""
    with load_pdf(pdf_source, password=password) as pdf:
        return [page.extract_text() or "" for page in pdf.pages]


def extract_text_from_pdf(pdf_source: str | Path, password: str | None = None) -> str:
    """Return the full extracted text for the PDF."""
    return "\n".join(extract_text_by_page(pdf_source, password=password))


def extract_tables_from_pdf(pdf_source: str | Path, password: str | None = None) -> list[list[list[str | None]]]:
    """Return all tables from all PDF pages."""
    tables: list[list[list[str | None]]] = []
    with load_pdf(pdf_source, password=password) as pdf:
        for page in pdf.pages:
            tables.extend(page.extract_tables())
    return tables


def pdf_contains_images(pdf_source: str | Path, password: str | None = None) -> bool:
    """Return True when any page in the PDF contains one or more image objects."""
    with load_pdf(pdf_source, password=password) as pdf:
        return any(bool(page.images) for page in pdf.pages)


def table_to_records(table: list[list[str | None]]) -> list[dict[str, str]]:
    """Convert a table into a list of row dictionaries using the first row as headers."""
    if not table:
        return []

    headers = [str(column).strip() if column else "" for column in table[0]]
    records: list[dict[str, str]] = []

    for row in table[1:]:
        record: dict[str, str] = {}
        for index, header in enumerate(headers):
            if not header:
                continue
            value = row[index] if index < len(row) else ""
            record[header] = "" if value is None else str(value).strip()
        if record:
            records.append(record)

    return records


def parse_claim_tables(raw_tables):
    def clean(val):
        return val.replace("\n", "" if "@" in val else " ").strip() if val else ""

    parsed_data = {}
    for header, *rows in raw_tables:
        if header[1] is None:  # Key-Value table
            parsed_data[header[0]] = {
                k.rstrip(":"): clean(v)
                for row in rows
                for k, v in zip(row[::2], row[1::2]) if k
            }
        else:  # Line items table
            parsed_data["LINE ITEMS"] = [
                {k: clean(v) for k, v in zip(header, row)}
                for row in rows
            ]
    return parsed_data