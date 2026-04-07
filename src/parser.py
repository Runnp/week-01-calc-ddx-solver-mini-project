"""
parser.py — Image → Problem Text
Day 2, Push 1: API key loading + raw Claude Vision call.
"""

import base64
import os
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


def parse_image(image_path: str) -> str:
    """
    Takes a screenshot path, sends it to Claude Vision,
    and returns the raw response text.
    Push 1: raw response only — parsing comes in Push 2.
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
                            "This is a screenshot of an AP Calculus BC problem. "
                            "Extract and return the math problem exactly as written. "
                            "Return only the raw problem text, nothing else."
                        ),
                    },
                ],
            }
        ],
    )

    return response.content[0].text


def extract_topic(problem_text: str) -> str:
    """
    Classify which calculus topic the problem belongs to.
    Returns one of: limits, derivatives, integrals, series, ...
    """
    problem_lower = problem_text.lower()

    if "lim" in problem_lower:
        return "limits"
    elif "d/dx" in problem_lower or "f'(" in problem_lower or "derivative" in problem_lower:
        return "derivatives"
    elif "∫" in problem_lower or "integral" in problem_lower:
        return "integrals"
    elif "series" in problem_lower or "sigma" in problem_lower or "∑" in problem_lower:
        return "series"
    else:
        return "unknown"