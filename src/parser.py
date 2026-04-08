"""
parser.py — Image → Problem Text
Day 2, Push 2: Smart extraction — structured response + topic detection.
"""

import base64
import os
import re
import anthropic
from dotenv import load_dotenv

load_dotenv()


def _get_client() -> anthropic.Anthropic:
    """Create Anthropic client from env variable."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "ANTHROPIC_API_KEY not set. Copy .env.example to .env and add your key."
        )
    return anthropic.Anthropic(api_key=api_key)


def _image_to_base64(image_path: str) -> tuple[str, str]:
    """Read image file and return (base64_data, media_type)."""
    ext = image_path.lower().split(".")[-1]
    media_type_map = {
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "bmp": "image/bmp",
        "gif": "image/gif",
        "webp": "image/webp",
    }
    media_type = media_type_map.get(ext, "image/png")

    with open(image_path, "rb") as f:
        b64 = base64.standard_b64encode(f.read()).decode("utf-8")

    return b64, media_type


def _clean_expression(raw: str) -> str:
    """
    Clean up Claude's response into a solver-friendly expression.
    Strips markdown, extra whitespace, and explanation text.
    """
    raw = re.sub(r"```[a-z]*", "", raw).replace("```", "")
    lines = raw.strip().splitlines()
    math_lines = [
        line for line in lines
        if line.strip() and not re.match(
            r"^(find|evaluate|solve|compute|given|note|this|the)\b",
            line.strip(), re.IGNORECASE
        )
    ]
    return "\n".join(math_lines).strip() if math_lines else raw.strip()


def parse_image(image_path: str) -> str:
    """
    Takes a screenshot path, sends it to Claude Vision,
    and returns a clean extracted math problem string.
    Push 2: structured prompt + expression cleaning.
    """
    client = _get_client()
    b64, media_type = _image_to_base64(image_path)

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": b64,
                        },
                    },
                    {
                        "type": "text",
                        "text": (
                            "This is a screenshot of an AP Calculus BC problem.\n"
                            "Extract the math problem and return it in this exact format:\n\n"
                            "PROBLEM: <the math expression, e.g. lim(x->0) sin(x)/x>\n"
                            "TOPIC: <one of: limits, derivatives, integrals, series, other>\n\n"
                            "Use standard math notation. No explanation, no extra text."
                        ),
                    },
                ],
            }
        ],
    )

    raw = response.content[0].text
    return _parse_structured_response(raw)


def _parse_structured_response(raw: str) -> str:
    """
    Extract the PROBLEM field from Claude's structured response.
    Falls back to cleaned raw text if format is not followed.
    """
    problem_match = re.search(r"PROBLEM:\s*(.+?)(?:\nTOPIC:|$)", raw, re.DOTALL | re.IGNORECASE)
    if problem_match:
        return _clean_expression(problem_match.group(1))
    return _clean_expression(raw)


def extract_topic(problem_text: str) -> str:
    """
    Classify which calculus topic the problem belongs to.
    Returns one of: limits, derivatives, integrals, series, unknown.
    """
    p = problem_text.lower()

    if "lim" in p:
        return "limits"
    elif any(k in p for k in ["d/dx", "f'(", "derivative", "dy/dx", "d^2", "d/dt", "dy/dt", "dx/dt", "rate", "implicit"]):
        return "derivatives"
    elif any(k in p for k in ["integral", "antiderivative"]) or "∫" in problem_text:
        return "integrals"
    elif any(k in p for k in ["series", "sigma", "converge", "diverge", "taylor", "maclaurin"]) or "∑" in problem_text:
        return "series"
    else:
        return "unknown"