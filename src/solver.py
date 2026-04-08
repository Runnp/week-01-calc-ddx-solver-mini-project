"""
solver.py — Problem Text -> Answer
Day 3, Push 3: Related rates + higher order derivatives. Derivatives fully complete.
Topics roadmap:
  ✅ Limits
  ✅ Derivatives - basic (power, trig, exp, log)
  ✅ Derivatives - implicit differentiation
  ✅ Derivatives - higher order (2nd, 3rd)
  ✅ Derivatives - related rates (d/dt)
  🔲 Integrals — Day 5
  🔲 Series — Day 7
"""

import re
from parser import extract_topic

try:
    import sympy as sp
    SYMPY_AVAILABLE = True
except ImportError:
    SYMPY_AVAILABLE = False

x, y, t = sp.symbols("x y t")


def solve(problem_text: str) -> str:
    """Main dispatcher: routes problem to the correct topic solver."""
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
        return "Integrals solver — coming Day 5"
    elif topic == "series":
        return "Series solver — coming Day 7"
    else:
        return "Topic not recognized. Supported: limits, derivatives."


# ── LIMITS ────────────────────────────────────────────────────────────────────

def solve_limit(problem_text: str) -> str:
    if not SYMPY_AVAILABLE:
        return "Install sympy: pip install sympy"

    KNOWN = {
        "sin(x)/x":     (sp.sin(x) / x,        0),
        "(1-cos(x))/x": ((1 - sp.cos(x)) / x,  0),
        "(e^x-1)/x":    ((sp.exp(x) - 1) / x,  0),
        "(e^x - 1)/x":  ((sp.exp(x) - 1) / x,  0),
    }
    for key, (expr, point) in KNOWN.items():
        if key in problem_text:
            result = sp.limit(expr, x, point)
            return f"{result}  (as x → {point})"

    point = _extract_limit_point(problem_text)
    expr  = _extract_expression(problem_text)
    try:
        return str(sp.limit(expr, x, point))
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

def _is_implicit(text: str) -> bool:
    p = text.lower()
    has_y = bool(re.search(r"\by\b|\by\^|\by\*", p))
    return has_y and "=" in text


def _is_related_rates(text: str) -> bool:
    p = text.lower()
    return any(k in p for k in ["d/dt", "dy/dt", "dx/dt", "dv/dt", "dr/dt", "rate", "with respect to t"])


def solve_derivative(problem_text: str) -> str:
    """Explicit derivative — supports 1st, 2nd, 3rd order."""
    if not SYMPY_AVAILABLE:
        return "Install sympy: pip install sympy"

    expr = _extract_expression(problem_text)
    if expr is None:
        return "Could not parse expression. Try: d/dx x^3 + 2x"

    try:
        order = _extract_derivative_order(problem_text)
        result = sp.diff(expr, x, order)
        simplified = sp.simplify(result)
        label = {1: "f'(x)", 2: "f''(x)", 3: "f'''(x)"}.get(order, f"f^({order})(x)")
        return f"{label} = {simplified}"
    except Exception as e:
        return f"Could not differentiate: {e}"


def solve_implicit(problem_text: str) -> str:
    """Implicit differentiation: finds dy/dx for F(x,y) = C."""
    if not SYMPY_AVAILABLE:
        return "Install sympy: pip install sympy"
    try:
        parts = problem_text.replace("^", "**").split("=")
        if len(parts) != 2:
            return "Implicit form needs an equation with '='"

        lhs = sp.sympify(parts[0].strip(), locals={"x": x, "y": y})
        rhs = sp.sympify(parts[1].strip(), locals={"x": x, "y": y})
        F = lhs - rhs

        dFdx = sp.diff(F, x)
        dFdy = sp.diff(F, y)

        if dFdy == 0:
            return "dy/dx is undefined (dF/dy = 0)"

        dydx = sp.simplify(-dFdx / dFdy)
        return f"dy/dx = {dydx}"
    except Exception as e:
        return f"Could not solve implicit differentiation: {e}"


def solve_related_rates(problem_text: str) -> str:
    """
    Related rates: differentiates a relation with respect to t.
    Example: 'x^2 + y^2 = r^2, find dy/dt'  →  differentiates both sides wrt t.
    """
    if not SYMPY_AVAILABLE:
        return "Install sympy: pip install sympy"

    try:
        # Define x, y, r as functions of t for implicit t-differentiation
        x_t = sp.Function("x")(t)
        y_t = sp.Function("y")(t)
        r_t = sp.Function("r")(t)

        parts = problem_text.replace("^", "**").split("=")
        if len(parts) < 2:
            return "Related rates needs an equation. Example: V = (4/3)*pi*r^3"

        lhs_raw = parts[0].strip()
        rhs_raw = parts[1].strip()

        local_map = {"x": x_t, "y": y_t, "r": r_t, "t": t, "pi": sp.pi}
        lhs = sp.sympify(lhs_raw, locals=local_map)
        rhs = sp.sympify(rhs_raw, locals=local_map)

        # Differentiate both sides wrt t
        dlhs = sp.diff(lhs, t)
        drhs = sp.diff(rhs, t)

        result = sp.simplify(dlhs - drhs)
        return f"d/dt: {sp.simplify(dlhs)} = {sp.simplify(drhs)}"

    except Exception as e:
        return f"Could not solve related rates: {e}"


def _extract_derivative_order(text: str) -> int:
    match = re.search(r"d[\^²]?([23])?[y/]", text)
    if match and match.group(1):
        return int(match.group(1))
    if "d²" in text or "d^2" in text or "second" in text.lower():
        return 2
    if "third" in text.lower() or "d^3" in text:
        return 3
    return 1


def _extract_expression(text: str):
    cleaned = re.sub(
        r"(d/dx|d²y/dx²|d\^2y/dx\^2|dy/dx|d/dt|lim\s*\([^)]+\)|derivative of|find f'\(x\) if)",
        "", text, flags=re.IGNORECASE
    ).strip()

    cleaned = (cleaned
        .replace("^", "**")
        .replace("e^x", "exp(x)")
        .replace("e^(", "exp(")
        .replace("ln(", "log(")
        .replace("π", "pi")
        .replace("→", "")
        .replace("∞", "oo")
    )
    cleaned = cleaned.split("=")[0].strip()

    try:
        return sp.sympify(cleaned, locals={"x": x, "y": y, "t": t})
    except Exception:
        return None