"""
parser.py — Image -> Problem Text
Day 7 fix: Replaced pytesseract with EasyOCR — 100% open source, no external install.
pip install easyocr
"""

import re
from PIL import Image, ImageFilter, ImageEnhance

# Lazy-load EasyOCR so the app starts fast — loaded on first image use
_reader = None

def _get_reader():
    global _reader
    if _reader is None:
        import easyocr
        # English only, GPU off — works on any machine
        _reader = easyocr.Reader(["en"], gpu=False, verbose=False)
    return _reader


def _preprocess_image(image_path: str) -> str:
    """
    Preprocess image for better OCR accuracy.
    Grayscale -> contrast boost -> sharpen -> upscale if small.
    Returns path to processed temp image.
    """
    import tempfile, os
    img = Image.open(image_path).convert("L")

    w, h = img.size
    if w < 800:
        scale = 800 / w
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)

    img = ImageEnhance.Contrast(img).enhance(2.5)
    img = img.filter(ImageFilter.SHARPEN)
    img = img.filter(ImageFilter.SHARPEN)

    # Save to temp file for EasyOCR
    tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    img.save(tmp.name)
    return tmp.name


def _normalize_math(text: str) -> str:
    """Normalize OCR output into SymPy-friendly math notation."""
    replacements = [
        (r"\bX\b",        "x"),
        (r"\bY\b",        "y"),
        (r"×",            "*"),
        (r"÷",            "/"),
        (r"²",            "^2"),
        (r"³",            "^3"),
        (r"(\d)\s+x",     r"\1*x"),   # 3 x -> 3*x
        (r"(\d)\s+\(",    r"\1*("),   # 3 ( -> 3*(
        (r"\bSin\b",      "sin"),
        (r"\bCos\b",      "cos"),
        (r"\bTan\b",      "tan"),
        (r"\bLn\b",       "ln"),
        (r"\bLog\b",      "log"),
        (r"\bE\b",        "e"),
        (r"[—–]",         "-"),
        (r"\s{2,}",       " "),
    ]
    for pattern, replacement in replacements:
        text = re.sub(pattern, replacement, text)
    return text.strip()


def parse_image(image_path: str) -> str:
    """
    Takes a screenshot path, runs EasyOCR, returns cleaned math string.
    100% open source — no API, no external binary needed.
    First call downloads the EasyOCR model (~100MB, once only).
    """
    import os
    tmp_path = _preprocess_image(image_path)

    try:
        reader = _get_reader()
        results = reader.readtext(tmp_path, detail=1, paragraph=False)
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass

    if not results:
        return ""

    # Each result: (bbox, text, confidence)
    # Pick the line with highest math symbol density
    lines = [(text, conf) for _, text, conf in results if text.strip()]

    if not lines:
        return ""

    # Score each line: math symbols weighted by confidence
    def math_score(line_conf):
        text, conf = line_conf
        math_chars = len(re.findall(r"[x\d\+\-\*/\^\(\)=∫∑]", text))
        return math_chars * conf

    best_text = max(lines, key=math_score)[0]

    # If multiple lines detected, join them (handles multi-line problems)
    if len(lines) > 1:
        joined = " ".join(t for t, _ in lines)
        if math_score((joined, 1.0)) > math_score((best_text, 1.0)):
            best_text = joined

    return _normalize_math(best_text)


def extract_topic(problem_text: str) -> str:
    """Classify calculus topic from problem text."""
    p = problem_text.lower()

    if "lim" in p:
        return "limits"
    elif any(k in p for k in ["d/dx", "f'(", "derivative", "dy/dx", "d^2",
                                "d/dt", "dy/dt", "dx/dt", "rate", "implicit"]):
        return "derivatives"
    elif any(k in p for k in ["integral", "antiderivative", "integrate"]) or "∫" in problem_text:
        return "integrals"
    elif any(k in p for k in ["series", "sigma", "converge", "diverge", "taylor",
                                "maclaurin", "ratio test", "root test", "p-series",
                                "geometric", "expand"]) or "∑" in problem_text:
        return "series"
    else:
        return "unknown"
