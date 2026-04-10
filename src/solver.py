"""
solver.py — Problem Text -> Answer
Day 5, Push 1: solve() now returns dict with steps + answer for GUI display.
Topics:
  ✅ Limits
  ✅ Derivatives - all types
  ✅ Integrals - indefinite, definite
  ✅ Step-by-step output
  🔲 Integration by parts, improper — Push 2
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


def solve(problem_text: str) -> dict:
    """
    Main dispatcher. Returns a dict:
      { "answer": str, "steps": [str, ...], "topic": str }
    """
    if not SYMPY_AVAILABLE:
        return _result("Install sympy: pip install sympy", [], "error")

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
        return solve_integral_advanced(problem_text)
    elif topic == "series":
        return _result("Series solver — coming Day 7", [], "series")
    else:
        return _try_best_guess(problem_text)


def _result(answer: str, steps: list, topic: str) -> dict:
    return {"answer": answer, "steps": steps, "topic": topic}


# ── LIMITS ────────────────────────────────────────────────────────────────────

def solve_limit(problem_text: str) -> dict:
    KNOWN = {
        "sin(x)/x":     (sp.sin(x) / x,        0),
        "(1-cos(x))/x": ((1 - sp.cos(x)) / x,  0),
        "(e^x-1)/x":    ((sp.exp(x) - 1) / x,  0),
        "(e^x - 1)/x":  ((sp.exp(x) - 1) / x,  0),
    }
    for key, (expr, point) in KNOWN.items():
        if key in problem_text:
            res = sp.limit(expr, x, point)
            steps = [
                f"Recognized standard limit identity",
                f"lim(x→{point}) {key}",
                f"= {res}",
            ]
            return _result(str(res), steps, "limits")

    point = _extract_limit_point(problem_text)
    expr = _parse_expr(problem_text)
    try:
        steps = [
            f"Evaluating limit as x → {point}",
            f"Expression: {expr}",
        ]
        # Try direct substitution first
        try:
            direct = expr.subs(x, point)
            if direct.is_finite:
                steps.append(f"Direct substitution: x = {point}")
                steps.append(f"= {sp.simplify(direct)}")
                return _result(str(sp.simplify(direct)), steps, "limits")
        except Exception:
            pass
        # Use SymPy limit (handles L'Hopital automatically)
        steps.append("Indeterminate form — applying L'Hôpital / algebraic methods")
        result = sp.limit(expr, x, point)
        steps.append(f"= {result}")
        return _result(str(result), steps, "limits")
    except Exception as e:
        return _result(f"Could not evaluate limit: {e}", [], "limits")


def _extract_limit_point(text: str):
    match = re.search(r"x\s*[→->]+\s*([^\s,)]+)", text)
    if match:
        try:
            return sp.sympify(match.group(1).strip())
        except Exception:
            pass
    return sp.Integer(0)


# ── DERIVATIVES ───────────────────────────────────────────────────────────────

def solve_derivative(problem_text: str) -> dict:
    expr = _parse_expr(problem_text)
    if expr is None:
        return _result("Could not read expression. Try: d/dx x^3 + 2x", [], "derivatives")
    try:
        order = _extract_order(problem_text)
        steps = [f"Differentiating: {expr}"]
        if order > 1:
            steps.append(f"Order: {order}")

        result = sp.simplify(sp.diff(expr, x, order))
        steps.append(f"Applying differentiation rules term by term")
        steps.append(f"= {result}")

        labels = ["f'(x)", "f''(x)", "f'''(x)"]
        lbl = labels[order - 1] if order <= 3 else f"f^({order})(x)"
        return _result(f"{lbl} = {result}", steps, "derivatives")
    except Exception as e:
        return _result(f"Could not differentiate: {e}", [], "derivatives")


def solve_implicit(problem_text: str) -> dict:
    try:
        parts = _prep(problem_text).split("=")
        if len(parts) != 2:
            return _result("Need an equation with '=' for implicit differentiation", [], "derivatives")
        lhs = sp.sympify(parts[0], locals={"x": x, "y": y})
        rhs = sp.sympify(parts[1], locals={"x": x, "y": y})
        F = lhs - rhs
        dFdx = sp.diff(F, x)
        dFdy = sp.diff(F, y)
        dydx = sp.simplify(-dFdx / dFdy)
        steps = [
            f"Implicit differentiation of F(x,y) = 0",
            f"dF/dx = {dFdx}",
            f"dF/dy = {dFdy}",
            f"dy/dx = -(dF/dx)/(dF/dy)",
            f"= {dydx}",
        ]
        return _result(f"dy/dx = {dydx}", steps, "derivatives")
    except Exception as e:
        return _result(f"Could not solve implicit: {e}", [], "derivatives")


def solve_related_rates(problem_text: str) -> dict:
    try:
        x_t = sp.Function("x")(t)
        y_t = sp.Function("y")(t)
        r_t = sp.Function("r")(t)
        parts = _prep(problem_text).split("=")
        if len(parts) < 2:
            return _result("Need an equation. Example: V = (4/3)*pi*r^3", [], "derivatives")
        loc = {"x": x_t, "y": y_t, "r": r_t, "t": t, "pi": sp.pi}
        lhs = sp.sympify(parts[0], locals=loc)
        rhs = sp.sympify(parts[1], locals=loc)
        dlhs = sp.simplify(sp.diff(lhs, t))
        drhs = sp.simplify(sp.diff(rhs, t))
        steps = [
            "Differentiating both sides with respect to t",
            f"LHS: d/dt [{lhs}] = {dlhs}",
            f"RHS: d/dt [{rhs}] = {drhs}",
        ]
        return _result(f"d/dt:  {dlhs} = {drhs}", steps, "derivatives")
    except Exception as e:
        return _result(f"Could not solve related rates: {e}", [], "derivatives")


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

def solve_integral(problem_text: str) -> dict:
    bounds = _extract_integral_bounds(problem_text)
    expr = _parse_expr(problem_text)

    if expr is None:
        return _result("Could not parse integral. Try: integrate x^2", [], "integrals")

    try:
        steps = [f"Integrating: {expr}"]
        if bounds:
            lo, hi = bounds
            steps.append(f"Bounds: [{lo}, {hi}]")
            indefinite = sp.integrate(expr, x)
            steps.append(f"Antiderivative: F(x) = {indefinite}")
            steps.append(f"Applying FTC: F({hi}) - F({lo})")
            result = sp.simplify(sp.integrate(expr, (x, lo, hi)))
            steps.append(f"= {result}")
            return _result(f"∫({lo} to {hi}) = {result}", steps, "integrals")
        else:
            result = sp.simplify(sp.integrate(expr, x))
            steps.append(f"Antiderivative: {result} + C")
            return _result(f"∫ = {result} + C", steps, "integrals")
    except Exception as e:
        return _result(f"Could not integrate: {e}", [], "integrals")


def _extract_integral_bounds(text: str):
    match = re.search(r"[∫]\s*\(\s*([^,]+)\s*,\s*([^)]+)\s*\)", text)
    if match:
        try:
            return sp.sympify(match.group(1).strip()), sp.sympify(match.group(2).strip())
        except Exception:
            pass
    match = re.search(r"from\s+([^\s]+)\s+to\s+([^\s]+)", text, re.IGNORECASE)
    if match:
        try:
            return sp.sympify(match.group(1).strip()), sp.sympify(match.group(2).strip())
        except Exception:
            pass
    match = re.search(r"∫_([^\^]+)\^([^\s]+)", text)
    if match:
        try:
            return sp.sympify(match.group(1).strip()), sp.sympify(match.group(2).strip())
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
        .replace("→", "").replace("∞", "oo")
        .replace("∫", "").replace(" dx", "").replace(" dy", "")
    )


def _parse_expr(text: str):
    cleaned = _prep(text).split("=")[0].strip()
    cleaned = re.sub(r"^\([^)]+\)", "", cleaned).strip()
    try:
        return sp.sympify(cleaned, locals={"x": x, "y": y, "t": t})
    except Exception:
        return None


def _try_best_guess(text: str) -> dict:
    expr = _parse_expr(text)
    if expr and x in expr.free_symbols:
        try:
            result = sp.simplify(sp.diff(expr, x))
            return _result(
                f"f'(x) = {result}  (guessed derivative)",
                ["No topic prefix found — guessing derivative", f"f'(x) = {result}"],
                "unknown"
            )
        except Exception:
            pass
    return _result(
        "Could not identify topic. Try: 'd/dx x^2', 'integrate x^2', or 'lim(x->0) sin(x)/x'",
        [], "unknown"
    )


# ── INTEGRATION BY PARTS + IMPROPER ──────────────────────────────────────────
# Day 5, Push 2 additions — appended below existing solve_integral

def solve_integral_advanced(problem_text: str) -> dict:
    """
    Advanced integration:
    - Integration by parts (detects u*dv pattern)
    - Improper integrals (bounds with oo / infinity)
    - FTC evaluation with shown substitution steps
    """
    bounds = _extract_integral_bounds(problem_text)
    expr   = _parse_expr(problem_text)

    if expr is None:
        return _result("Could not parse. Try: integrate x*exp(x) or integrate x*ln(x)", [], "integrals")

    # Check for improper integral
    is_improper = bounds and any(
        str(b) in ("oo", "-oo", "inf", "-inf") for b in bounds
    )

    try:
        steps = [f"Integrating: {expr}"]

        # Try integration by parts detection: product of two different function types
        ibp_result = _try_integration_by_parts(expr)
        if ibp_result:
            u, dv, du, v, result_expr = ibp_result
            steps += [
                "Integration by parts: ∫u dv = uv - ∫v du",
                f"Let u = {u},  dv = {dv} dx",
                f"Then du = {du} dx,  v = {v}",
                f"= {u}·{v} - ∫{sp.expand(v * du)} dx",
                f"= {sp.simplify(result_expr)}",
            ]
            if bounds:
                lo, hi = bounds
                steps.append(f"Evaluating from {lo} to {hi}")
                definite = sp.simplify(result_expr.subs(x, hi) - result_expr.subs(x, lo))
                steps.append(f"= {definite}")
                return _result(f"∫({lo} to {hi}) = {definite}", steps, "integrals")
            return _result(f"∫ = {sp.simplify(result_expr)} + C", steps, "integrals")

        # Standard integration
        antideriv = sp.integrate(expr, x)
        steps.append(f"Antiderivative: F(x) = {antideriv}")

        if is_improper:
            lo, hi = bounds
            steps.append(f"Improper integral — taking limit at infinity")
            result = sp.simplify(sp.integrate(expr, (x, lo, hi)))
            steps.append(f"= {result}")
            converges = result.is_finite
            steps.append("Converges" if converges else "Diverges")
            return _result(f"∫ = {result}  ({'converges' if converges else 'diverges'})", steps, "integrals")

        if bounds:
            lo, hi = bounds
            steps += [
                f"Applying FTC: F({hi}) - F({lo})",
                f"F({hi}) = {sp.simplify(antideriv.subs(x, hi))}",
                f"F({lo}) = {sp.simplify(antideriv.subs(x, lo))}",
            ]
            result = sp.simplify(sp.integrate(expr, (x, lo, hi)))
            steps.append(f"= {result}")
            return _result(f"∫({lo} to {hi}) = {result}", steps, "integrals")

        return _result(f"∫ = {sp.simplify(antideriv)} + C", steps, "integrals")

    except Exception as e:
        return _result(f"Could not integrate: {e}", [], "integrals")


def _try_integration_by_parts(expr):
    """
    Detect if expr is a product suited for IBP.
    Returns (u, dv, du, v, uv - int(v*du)) or None.
    Priority order: LIATE — Log, Inverse trig, Algebraic, Trig, Exponential.
    """
    if not expr.is_Mul:
        return None

    factors = expr.as_ordered_factors()
    if len(factors) < 2:
        return None

    def liate_rank(f):
        if f.has(sp.log):           return 0
        if f.has(sp.atan, sp.asin): return 1
        if f.is_polynomial(x):      return 2
        if f.has(sp.sin, sp.cos):   return 3
        if f.has(sp.exp):           return 4
        return 5

    factors_sorted = sorted(factors, key=liate_rank)
    u  = factors_sorted[0]
    dv = sp.Mul(*factors_sorted[1:])

    du = sp.diff(u, x)
    v  = sp.integrate(dv, x)

    result = sp.expand(u * v - sp.integrate(v * du, x))
    return u, dv, du, v, result