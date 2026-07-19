"""Shared themed data-table renderer for harness output (selector baseline, scoreboard).

Reuses the .data-table / .status-badge CSS classes from theme.css instead of Streamlit's
default st.table — the built-in table renders low-contrast text against this app's dark
background, and hand-rendered HTML lets status values (OK/FAIL, yes/no, MET/NOT MET) reuse
the same colored-badge language the pipeline view already established.
"""
from __future__ import annotations

from html import escape
from typing import Iterable

import streamlit as st


def badge(value: str, kind: str) -> str:
    """A colored pill matching the pipeline view's pass/fail/running/neutral badges."""
    return f'<span class="status-badge {kind}">{escape(str(value))}</span>'


def cell(value: object) -> str:
    """Escape a plain-text cell value (as opposed to pre-built badge() HTML)."""
    return escape(str(value))


def mono_cell(value: object) -> str:
    """Escape and monospace-style a cell value (selectors, code-like strings)."""
    return f'<span class="mono">{escape(str(value))}</span>'


def render_table(headers: Iterable[str], rows: Iterable[Iterable[str]]) -> None:
    """Render a themed HTML table. Cell values may contain pre-built badge() HTML."""
    head_html = "".join(f"<th>{escape(h)}</th>" for h in headers)
    body_html = "".join(
        "<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>"
        for row in rows
    )
    st.html(
        f'<div class="data-table-wrap"><table class="data-table">'
        f"<thead><tr>{head_html}</tr></thead><tbody>{body_html}</tbody>"
        f"</table></div>"
    )
