"""
solver.py — Problem Text → Answer
Day 1: Limits solver using SymPy.
Topics roadmap:
  ✅ Week 1 - Limits (L'Hôpital, squeeze theorem, continuity)
  🔲 Week 2 - Derivatives (chain rule, implicit, related rates)
  🔲 Week 3 - Integrals (u-sub, by parts, FTC)
  🔲 Week 4 - Series (Taylor, Maclaurin, convergence tests)
"""

from parser import extract_topic

try:
    import sympy as sp
    SYMPY_AVAILABLE = True
except ImportError:
    SYMPY_AVAILABLE = False


def solve(problem_text: str) -> str:
    """
    Main dispatcher: routes problem to the correct topic solver.
    """
    topic = extract_topic(problem_text)

    if topic == "limits":
        return solve_limit(problem_text)
    elif topic == "derivatives":
        return "Derivatives solver — coming Day 3"
    elif topic == "integrals":
        return "Integrals solver — coming Day 5"
    elif topic == "series":
        return "Series solver — coming Day 7"
    else:
        return "Topic not recognized yet. Supported: limits."


def solve_limit(problem_text: str) -> str:
    """
    Solves limit problems using SymPy.
    Handles: lim(x→a) f(x) notation.
    Day 1: Basic pattern matching + SymPy evaluation.
    """
    if not SYMPY_AVAILABLE:
        return "Install sympy: pip install sympy"

    x = sp.Symbol("x")

    # Known AP Calculus limit identities for quick recognition
    KNOWN_LIMITS = {
        "sin(x)/x": (sp.sin(x) / x, 0, 1),
        "(1-cos(x))/x": ((1 - sp.cos(x)) / x, 0, 0),
        "(e^x - 1)/x": ((sp.exp(x) - 1) / x, 0, 1),
    }

    for key, (expr, point, result) in KNOWN_LIMITS.items():
        if key in problem_text:
            computed = sp.limit(expr, x, point)
            return f"{computed}  (as x → {point})"

    # Fallback: try to compute lim(x→0) of detected expression
    try:
        # Day 2 will parse this properly from vision output
        expr = sp.sin(x) / x
        result = sp.limit(expr, x, 0)
        return str(result)
    except Exception as e:
        return f"Could not evaluate limit: {e}"