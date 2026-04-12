"""
parser.py — Image -> Problem Text
Day 4, Push 1: Replaced Claude Vision with pytesseract OCR. 100% free, offline.
"""

import re
import os
from PIL import Image, ImageFilter, ImageEnhance
import pytesseract


# On Windows, tesseract needs its path set explicitly
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
if os.path.exists(TESSERACT_PATH):
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH


def _preprocess_image(image_path: str) -> Image.Image:
    """
    Preprocess image so OCR reads math symbols accurately.
    Steps: grayscale -> contrast boost -> sharpen -> upscale
    """
    img = Image.open(image_path).convert("L")  # grayscale

    # Upscale small images — tesseract reads larger text better
    w, h = img.size
    if w < 800:
        scale = 800 / w
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)

    # Boost contrast
    img = ImageEnhance.Contrast(img).enhance(2.5)

    # Sharpen edges
    img = img.filter(ImageFilter.SHARPEN)
    img = img.filter(ImageFilter.SHARPEN)

    return img


def _normalize_math(text: str) -> str:
    """
    Normalize OCR output into SymPy-friendly math notation.
    Fixes common OCR misreads on math symbols.
    """
    # Common OCR mistakes on math
    replacements = [
        (r"\bX\b",          "x"),
        (r"\bY\b",          "y"),
        (r"×",              "*"),
        (r"÷",              "/"),
        (r"²",              "^2"),
        (r"³",              "^3"),
        (r"\^(\d)",         r"^\1"),
        (r"(\d)\s*x",       r"\1*x"),  # 3x -> 3*x
        (r"(\d)\s*\(",      r"\1*("),  # 3( -> 3*(
        (r"Sin\b",          "sin"),
        (r"Cos\b",          "cos"),
        (r"Tan\b",          "tan"),
        (r"Ln\b",           "ln"),
        (r"Log\b",          "log"),
        (r"\bE\b",          "e"),
        (r"—",              "-"),
        (r"–",              "-"),
    ]
    for pattern, replacement in replacements:
        text = re.sub(pattern, replacement, text)
    return text.strip()


def parse_image(image_path: str) -> str:
    """
    Takes a screenshot path, runs OCR, returns cleaned math problem string.
    Works 100% offline — no API needed.
    """
    img = _preprocess_image(image_path)

    # Tesseract config: treat as single line of math text
    config = "--psm 6 -c tessedit_char_whitelist=0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ+-*/^()=.,∫∑πe '"
    raw = pytesseract.image_to_string(img, config=config)

    # Take the most math-looking line
    lines = [l.strip() for l in raw.splitlines() if l.strip()]
    best = max(lines, key=lambda l: len(re.findall(r"[x\d\+\-\*/\^\(\)=]", l))) if lines else raw

    return _normalize_math(best)


def extract_topic(problem_text: str) -> str:
    """Classify calculus topic from problem text."""
    p = problem_text.lower()

    if "lim" in p:
        return "limits"
    elif any(k in p for k in ["d/dx", "f'(", "derivative", "dy/dx", "d^2", "d/dt", "dy/dt", "dx/dt", "rate", "implicit"]):
        return "derivatives"
    elif any(k in p for k in ["integral", "antiderivative", "integrate"]) or "∫" in problem_text:
        return "integrals"
    elif any(k in p for k in ["series", "sigma", "converge", "diverge", "taylor", "maclaurin", "ratio test", "root test", "p-series", "geometric", "expand"]) or "∑" in problem_text:
        return "series"
    else:
        return "unknown"