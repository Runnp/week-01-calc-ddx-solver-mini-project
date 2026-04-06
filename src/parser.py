"""
parser.py — Image → Problem Text
Day 1: Stub with Claude Vision API integration placeholder.
Day 2 goal: Wire up real API call to extract LaTeX/text from screenshot.
"""

import base64
import os


def parse_image(image_path: str) -> str:
    """
    Takes a screenshot path, returns the detected calculus problem as a string.
    
    Currently: returns a placeholder for Day 1 scaffold.
    Next: Use Claude Vision (or pytesseract) to extract the math expression.
    """
    # TODO (Day 2): Call Claude API with vision
    # with open(image_path, "rb") as f:
    #     b64 = base64.b64encode(f.read()).decode()
    # response = claude_client.messages.create(
    #     model="claude-opus-4-5",
    #     messages=[{
    #         "role": "user",
    #         "content": [
    #             {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": b64}},
    #             {"type": "text", "text": "Extract the calculus problem from this image. Return only the math expression."}
    #         ]
    #     }]
    # )
    # return response.content[0].text

    # Day 1 placeholder
    return f"[Image loaded: {os.path.basename(image_path)}]\nlim(x→0) sin(x)/x"


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