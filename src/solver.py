"""
solver.py — Problem Text -> Answer
Day 4, Push 3: Integrals added — indefinite, definite, u-substitution via SymPy.
Topics:
  ✅ Limits
  ✅ Derivatives - all types
  ✅ Integrals - indefinite, definite, automatic
  🔲 Series — Day 7
"""

import re
from parser import extract_topic

try:
    import sympy as sp
    SYMPY_AVAILABLE = True
except ImportError:
    SYMPY_AVAILABLE = False

x, y, t, a, b = sp.symbols("x y t a b")


def solve(problem_text: str) -> str:
    """Main dispatcher."""
    if not SYMPY_AVAILABLE:
        return "Install sympy: pip install sympy"

    topic = extract_topic(problem_text)

    if topic == "limits":
        return solve_limit(problem_text)
    elif topic == "derivatives":
        if _is_related_rates(problem_text):
            return solve_related_rates(problem_text)
        if _is_implicit(problem_text):
            return solve_implicit(problem_text)
        return solve_derivative(problem_text)
    elif topic == "integrals":
        return solve_integral(problem_text)
    elif topic == "series":
        return "Series solver — coming Day 7"
    else:
        return _try_best_guess(problem_text)


# ── LIMITS ────────────────────────────────────────────────────────────────────

def solve_limit(problem_text: str) -> str:
    KNOWN = {
        "sin(x)/x":     (sp.sin(x) / x,        0),
        "(1-cos(x))/x": ((1 - sp.cos(x)) / x,  0),
        "(e^x-1)/x":    ((sp.exp(x) - 1) / x,  0),
        "(e^x - 1)/x":  ((sp.exp(x) - 1) / x,  0),
    }
    for key, (expr, point) in KNOWN.items():
        if key in problem_text:
            return f"{sp.limit(expr, x, point)}  (as x → {point})"

    point = _extract_limit_point(problem_text)
    expr = _parse_expr(problem_text)
    try:
        result = sp.limit(expr, x, point)
        return f"{result}  (as x → {point})"
    except Exception as e:
        return f"Could not evaluate limit: {e}"


def _extract_limit_point(text: str):
    match = re.search(r"x\s*[→->]+\s*([^\s,)]+)", text)
    if match:
        try:
            return sp.sympify(match.group(1).strip())
        except Exception:
            pass
    return sp.Integer(0)


# ── DERIVATIVES ───────────────────────────────────────────────────────────────

def solve_derivative(problem_text: str) -> str:
    expr = _parse_expr(problem_text)
    if expr is None:
        return "Could not read expression. Try: d/dx x^3 + 2x"
    try:
        order = _extract_order(problem_text)
        result = sp.simplify(sp.diff(expr, x, order))
        label = ["f'(x)", "f''(x)", "f'''(x)"]
        lbl = label[order - 1] if order <= 3 else f"f^({order})(x)"
        return f"{lbl} = {result}"
    except Exception as e:
        return f"Could not differentiate: {e}"


def solve_implicit(problem_text: str) -> str:
    try:
        parts = _prep(problem_text).split("=")
        if len(parts) != 2:
            return "Need an equation with '=' for implicit differentiation"
        lhs = sp.sympify(parts[0], locals={"x": x, "y": y})
        rhs = sp.sympify(parts[1], locals={"x": x, "y": y})
        F = lhs - rhs
        dydx = sp.simplify(-sp.diff(F, x) / sp.diff(F, y))
        return f"dy/dx = {dydx}"
    except Exception as e:
        return f"Could not solve implicit: {e}"


def solve_related_rates(problem_text: str) -> str:
    try:
        x_t = sp.Function("x")(t)
        y_t = sp.Function("y")(t)
        r_t = sp.Function("r")(t)
        parts = _prep(problem_text).split("=")
        if len(parts) < 2:
            return "Need an equation. Example: V = (4/3)*pi*r^3"
        loc = {"x": x_t, "y": y_t, "r": r_t, "t": t, "pi": sp.pi}
        lhs = sp.sympify(parts[0], locals=loc)
        rhs = sp.sympify(parts[1], locals=loc)
        dlhs = sp.diff(lhs, t)
        drhs = sp.diff(rhs, t)
        return f"d/dt:  {sp.simplify(dlhs)} = {sp.simplify(drhs)}"
    except Exception as e:
        return f"Could not solve related rates: {e}"


def _is_implicit(text: str) -> bool:
    return bool(re.search(r"\by\b|\by\^|\by\*", text.lower())) and "=" in text


def _is_related_rates(text: str) -> bool:
    p = text.lower()
    return any(k in p for k in ["d/dt", "dy/dt", "dx/dt", "dv/dt", "dr/dt", "rate", "with respect to t"])


def _extract_order(text: str) -> int:
    if "d²" in text or "d^2" in text or "second" in text.lower():
        return 2
    if "third" in text.lower() or "d^3" in text:
        return 3
    match = re.search(r"d\^?(\d)", text)
    if match:
        return int(match.group(1))
    return 1


# ── INTEGRALS ─────────────────────────────────────────────────────────────────

def solve_integral(problem_text: str) -> str:
    """
    Solves integrals using SymPy.
    Handles:
      - Indefinite: ∫ x^2 dx  →  x^3/3 + C
      - Definite:   ∫(0,1) x^2 dx  →  1/3
    """
    bounds = _extract_integral_bounds(problem_text)
    expr = _parse_expr(problem_text)

    if expr is None:
        return "Could not parse integral. Try: integrate x^2 or ∫(0,1) x^2 dx"

    try:
        if bounds:
            lo, hi = bounds
            result = sp.integrate(expr, (x, lo, hi))
            result = sp.simplify(result)
            return f"∫({lo} to {hi}) = {result}"
        else:
            result = sp.integrate(expr, x)
            result = sp.simplify(result)
            return f"∫ = {result} + C"
    except Exception as e:
        return f"Could not integrate: {e}"


def _extract_integral_bounds(text: str):
    """
    Look for bounds in forms like:
      ∫(0,1), integral from 0 to 1, ∫_0^1
    """
    # ∫(0,1) or integral(0,1)
    match = re.search(r"[∫(integral)]\s*\(\s*([^,]+)\s*,\s*([^)]+)\s*\)", text, re.IGNORECASE)
    if match:
        try:
            lo = sp.sympify(match.group(1).strip())
            hi = sp.sympify(match.group(2).strip())
            return lo, hi
        except Exception:
            pass

    # "from A to B"
    match = re.search(r"from\s+([^\s]+)\s+to\s+([^\s]+)", text, re.IGNORECASE)
    if match:
        try:
            lo = sp.sympify(match.group(1).strip())
            hi = sp.sympify(match.group(2).strip())
            return lo, hi
        except Exception:
            pass

    # ∫_0^1
    match = re.search(r"∫_([^\^]+)\^([^\s]+)", text)
    if match:
        try:
            lo = sp.sympify(match.group(1).strip())
            hi = sp.sympify(match.group(2).strip())
            return lo, hi
        except Exception:
            pass

    return None


# ── HELPERS ───────────────────────────────────────────────────────────────────

def _prep(text: str) -> str:
    text = re.sub(
        r"(d/dx|d²y/dx²|d\^2y/dx\^2|dy/dx|d/dt|lim\s*\([^)]+\)|derivative of|integrate|antiderivative of)",
        "", text, flags=re.IGNORECASE
    ).strip()
    return (text
        .replace("^", "**")
        .replace("e**x", "exp(x)")
        .replace("e**(", "exp(")
        .replace("ln(", "log(")
        .replace("π", "pi")
        .replace("→", "")
        .replace("∞", "oo")
        .replace("∫", "")
        .replace(" dx", "")
        .replace(" dy", "")
    )


def _parse_expr(text: str):
    cleaned = _prep(text).split("=")[0].strip()
    # Remove bounds like (0,1)
    cleaned = re.sub(r"^\([^)]+\)", "", cleaned).strip()
    try:
        return sp.sympify(cleaned, locals={"x": x, "y": y, "t": t})
    except Exception:
        return None


def _try_best_guess(text: str):
    expr = _parse_expr(text)
    if expr and x in expr.free_symbols:
        try:
            result = sp.simplify(sp.diff(expr, x))
            return f"f'(x) = {result}  (guessed derivative)"
        except Exception:
            pass
    return "Could not identify topic. Try: 'd/dx x^2', 'integrate x^2', or 'lim(x->0) sin(x)/x'"