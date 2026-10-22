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


def extract_tables_from_pdf(pdf_object) -> list[list[list[str | None]]]:
    """Return all tables from all PDF pages."""
    tables: list[list[list[str | None]]] = []
    for page in pdf_object.pages:
        tables.extend(page.extract_tables())
    return tables


def pdf_contains_images(pdf_object) -> bool:
    """Return True when any page in the PDF contains one or more image objects."""
    for page in pdf_object.pages:
        if page.images:
            return True
        return False 

    # with load_pdf(pdf_source, password=password) as pdf:
    #     return any(bool(page.images) for page in pdf.pages)


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
    """Convert pdfplumber tables into claim sections and line-item records.

    ``raw_tables`` is the list returned by ``extract_tables_from_pdf``: each
    table is a list of rows, and each row is a list of cell values. The first
    row is treated as the table header.

    Tables are classified using the second cell of that header:

    * If it is ``None``, the table is treated as key/value data. Remaining rows
      are read as alternating key and value cells, so a row like
      ``["Claim Number:", "C-123", "Date Filed:", "2025-01-01"]`` becomes
      ``{"Claim Number": "C-123", "Date Filed": "2025-01-01"}``. These fields
      are stored under the first header cell (for example,
      ``"CLAIM INFORMATION"``).
    * Otherwise, the table is treated as a line-item table. Header cells are
      paired with each remaining row to make a list of records under
      ``"LINE ITEMS"``.

    Cell values are normalized by replacing embedded newlines with spaces and
    trimming surrounding whitespace. For values containing ``@``, newlines
    are removed instead, preserving email addresses split across PDF lines.
    ``None`` and empty cells normalize to an empty string.

    For example, key/value tables produce a structure like
    ``{"CLAIM INFORMATION": {"Claim Number": "C-123"}}``; line-item tables
    produce ``{"LINE ITEMS": [{"Description": "Repair", "Amount": "$100"}]}``.
    The result can therefore contain both section dictionaries and a
    ``"LINE ITEMS"`` list.

    Simplification opportunities: validate empty or malformed tables before
    indexing the header, and extract the key/value and line-item conversions
    into small helpers if this parser grows. It also assumes the
    project-specific table layout; ``zip`` silently ignores unmatched cells,
    while repeated section names or multiple line-item tables overwrite earlier
    entries with the same output key.
    """

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