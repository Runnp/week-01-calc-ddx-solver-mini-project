"""Manual text parser for the symbolic calculus desktop app."""

from __future__ import annotations

from dataclasses import dataclass
import re


@dataclass(frozen=True)
class ParsedRequest:
    operation: str
    expression_text: str
    bounds: tuple[str, str] | None = None
    variable: str = "x"
    original_text: str = ""
    normalized_text: str = ""


def normalize_input(text: str) -> str:
    """Convert user input into a SymPy-friendly text form."""
    cleaned = (text or "").strip()
    replacements = [
        ("\u2212", "-"),
        ("\u2013", "-"),
        ("\u2014", "-"),
        ("\u00d7", "*"),
        ("\u00f7", "/"),
        ("\u222b", "int "),
        ("\u03c0", "pi"),
        ("\u221e", "oo"),
    ]
    for old, new in replacements:
        cleaned = cleaned.replace(old, new)

    cleaned = re.sub(r"\s+", " ", cleaned)
    cleaned = re.sub(r"\bderivative of\b", "diff ", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\bintegral of\b", "int ", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\banti-?derivative of\b", "int ", cleaned, flags=re.IGNORECASE)
    return cleaned.strip()


def extract_topic(text: str) -> str:
    """Detect whether the user asked for a derivative or an integral."""
    lowered = normalize_input(text).lower()

    derivative_markers = (
        "d/dx",
        "differentiate",
        "derivative",
        "diff",
    )
    integral_markers = (
        "integrate",
        "integral",
        "antiderivative",
        "int",
    )

    if any(marker in lowered for marker in derivative_markers):
        return "derivative"
    if any(marker in lowered for marker in integral_markers):
        return "integral"
    return "unknown"


def parse_request(text: str) -> ParsedRequest:
    """Split the user's text into operation, expression, and optional bounds."""
    normalized = normalize_input(text)
    operation = extract_topic(normalized)

    if operation == "unknown":
        raise ValueError(
            "Start with 'diff' or 'int'. Example: diff x^3*sin(x)"
        )

    bounds = _extract_bounds(normalized) if operation == "integral" else None
    expression_text = _strip_operation_words(normalized, operation)
    expression_text = _strip_bounds_text(expression_text)
    expression_text = _strip_differential_suffix(expression_text)
    expression_text = expression_text.strip(" ,")

    if not expression_text:
        raise ValueError("Enter an expression after the operation.")

    return ParsedRequest(
        operation=operation,
        expression_text=expression_text,
        bounds=bounds,
        original_text=text,
        normalized_text=normalized,
    )


def _strip_operation_words(text: str, operation: str) -> str:
    cleaned = text
    if operation == "derivative":
        cleaned = re.sub(r"^\s*d/dx\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"^\s*diff(?:erentiate)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"^\s*derivative\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"^\s*of\s+", "", cleaned, flags=re.IGNORECASE)
    else:
        cleaned = re.sub(r"^\s*int\s+", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"^\s*integrate\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"^\s*integral\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"^\s*of\s+", "", cleaned, flags=re.IGNORECASE)
    return cleaned.strip()


def _strip_bounds_text(text: str) -> str:
    cleaned = re.sub(
        r"\s+from\s+(.+?)\s+to\s+(.+)$",
        "",
        text,
        flags=re.IGNORECASE,
    )
    return cleaned.strip()


def _strip_differential_suffix(text: str) -> str:
    return re.sub(r"\s*d([a-zA-Z])\s*$", "", text).strip()


def _extract_bounds(text: str) -> tuple[str, str] | None:
    match = re.search(r"\bfrom\s+(.+?)\s+to\s+(.+)$", text, flags=re.IGNORECASE)
    if not match:
        return None
    lower = match.group(1).strip()
    upper = match.group(2).strip()
    if not lower or not upper:
        return None
    return lower, upper
