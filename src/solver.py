"""
solver.py — Problem Text -> Answer
Day 6, Push 3: Series fully wired in.
Topics:
  ✅ Limits
  ✅ Derivatives - all types
  ✅ Integrals - indefinite, definite, IBP, improper
  ✅ Series - Taylor, Maclaurin, convergence tests
  ✅ Step-by-step output
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
        return solve_series(problem_text)
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


# ══════════════════════════════════════════════════════════════════════════════
# DAY 6 — SERIES
# Push 1: Taylor & Maclaurin series expansions
# Push 2: Convergence tests
# Push 3: Wired into dispatcher (see updated solve() below)
# ══════════════════════════════════════════════════════════════════════════════

n, k = sp.symbols("n k", positive=True, integer=True)


# ── PUSH 1: TAYLOR & MACLAURIN ────────────────────────────────────────────────

# Known closed-form Maclaurin series for fast display
MACLAURIN_KNOWN = {
    "sin(x)":   ("sin(x)",  "x - x³/3! + x⁵/5! - x⁷/7! + ...",  "all reals"),
    "cos(x)":   ("cos(x)",  "1 - x²/2! + x⁴/4! - x⁶/6! + ...",  "all reals"),
    "exp(x)":   ("e^x",     "1 + x + x²/2! + x³/3! + ...",        "all reals"),
    "e^x":      ("e^x",     "1 + x + x²/2! + x³/3! + ...",        "all reals"),
    "ln(1+x)":  ("ln(1+x)", "x - x²/2 + x³/3 - x⁴/4 + ...",      "(-1, 1]"),
    "1/(1-x)":  ("1/(1-x)", "1 + x + x² + x³ + ...",              "(-1, 1)"),
    "1/(1+x)":  ("1/(1+x)", "1 - x + x² - x³ + ...",              "(-1, 1)"),
    "arctan(x)":("arctan(x)","x - x³/3 + x⁵/5 - x⁷/7 + ...",     "[-1, 1]"),
}


def solve_series(problem_text: str) -> dict:
    """
    Main series dispatcher — detects subtype and routes accordingly.
    Subtypes: taylor, maclaurin, convergence tests, nth-term.
    """
    p = problem_text.lower()

    if any(k in p for k in ["taylor", "maclaurin", "expand", "series for", "series of"]):
        return solve_taylor_maclaurin(problem_text)
    elif any(k in p for k in ["converge", "diverge", "convergence", "ratio test", "root test",
                               "integral test", "comparison", "geometric", "p-series"]):
        return solve_convergence(problem_text)
    else:
        # Default: try Taylor expansion
        return solve_taylor_maclaurin(problem_text)


def solve_taylor_maclaurin(problem_text: str) -> dict:
    """
    Computes Taylor or Maclaurin series for a function.
    - Maclaurin: centered at a=0
    - Taylor: centered at a=given point
    """
    p = problem_text.lower()

    # Check known Maclaurin series first (fast + clean output)
    for key, (name, expansion, interval) in MACLAURIN_KNOWN.items():
        if key in p:
            steps = [
                f"Recognized standard Maclaurin series for {name}",
                f"Centered at a = 0",
                f"Series: {expansion}",
                f"Interval of convergence: {interval}",
            ]
            return _result(expansion, steps, "series")

    # Extract center point (Taylor) — default 0 (Maclaurin)
    center = _extract_series_center(problem_text)
    order  = _extract_series_order(problem_text)
    expr   = _parse_expr(problem_text)

    if expr is None:
        return _result(
            "Could not parse. Try: taylor sin(x) or maclaurin e^x or taylor ln(x) at x=1",
            [], "series"
        )

    try:
        label = "Maclaurin" if center == 0 else f"Taylor (a={center})"
        steps = [
            f"{label} series for: {expr}",
            f"Centered at a = {center}",
            f"Computing up to order {order}",
        ]

        # Compute series using SymPy
        series_expr = sp.series(expr, x, center, order + 1)
        # Remove the O() remainder term for clean display
        poly = series_expr.removeO()

        steps.append(f"= {poly} + ...")

        # Show individual term generation
        for i in range(min(4, order + 1)):
            deriv_i = sp.diff(expr, x, i).subs(x, center)
            factorial_i = sp.factorial(i)
            term = sp.Rational(deriv_i, factorial_i) * (x - center)**i
            if term != 0:
                steps.append(f"  term {i}: f^({i})({center})/{i}! · (x-{center})^{i} = {sp.simplify(term)}")

        return _result(str(poly) + " + ...", steps, "series")

    except Exception as e:
        return _result(f"Could not compute series: {e}", [], "series")


def _extract_series_center(text: str):
    """Extract Taylor center point from 'at x=a' or 'centered at a' notation."""
    match = re.search(r"at\s+x\s*=\s*([^\s,]+)", text, re.IGNORECASE)
    if match:
        try:
            return sp.sympify(match.group(1).strip())
        except Exception:
            pass
    match = re.search(r"centered\s+at\s+([^\s,]+)", text, re.IGNORECASE)
    if match:
        try:
            return sp.sympify(match.group(1).strip())
        except Exception:
            pass
    return sp.Integer(0)


def _extract_series_order(text: str) -> int:
    """Extract desired number of terms from 'order N' or 'N terms'."""
    match = re.search(r"order\s+(\d+)", text, re.IGNORECASE)
    if match:
        return int(match.group(1))
    match = re.search(r"(\d+)\s+terms?", text, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return 5  # default: show 5 terms


# ── PUSH 2: CONVERGENCE TESTS ─────────────────────────────────────────────────

def solve_convergence(problem_text: str) -> dict:
    """
    Runs appropriate convergence test on a series.
    Auto-selects best test or uses explicitly named test.
    Supports: geometric, p-series, ratio, root, integral, nth-term divergence.
    """
    p = problem_text.lower()

    # Route to named test if specified
    if "ratio" in p:
        return _ratio_test(problem_text)
    if "root" in p:
        return _root_test(problem_text)
    if "geometric" in p:
        return _geometric_series(problem_text)
    if "p-series" in p or "p series" in p:
        return _p_series_test(problem_text)
    if "integral test" in p:
        return _integral_test(problem_text)

    # Auto-detect best test
    return _auto_convergence(problem_text)


def _auto_convergence(problem_text: str) -> dict:
    """Auto-select and apply the most appropriate convergence test."""
    expr = _parse_series_term(problem_text)
    if expr is None:
        return _result("Could not parse series term.", [], "series")

    steps = [f"Series term: a(n) = {expr}", "Auto-selecting convergence test..."]

    # Check geometric: r^n pattern
    if _looks_geometric(expr):
        return _geometric_series(problem_text)

    # Check p-series: 1/n^p pattern
    if _looks_p_series(expr):
        return _p_series_test(problem_text)

    # Default: ratio test
    steps.append("Applying Ratio Test (most general)")
    return _ratio_test(problem_text)


def _ratio_test(problem_text: str) -> dict:
    """Ratio Test: lim |a(n+1)/a(n)| as n→∞."""
    expr = _parse_series_term(problem_text)
    if expr is None:
        return _result("Could not parse series term for ratio test.", [], "series")

    try:
        an   = expr
        an1  = expr.subs(n, n + 1)
        ratio = sp.simplify(sp.Abs(an1 / an))
        L = sp.limit(ratio, n, sp.oo)
        L_simplified = sp.simplify(L)

        steps = [
            f"Ratio Test: lim(n→∞) |a(n+1)/a(n)|",
            f"a(n) = {an}",
            f"a(n+1) = {an1}",
            f"|a(n+1)/a(n)| = {ratio}",
            f"L = lim(n→∞) = {L_simplified}",
        ]

        if L_simplified < 1:
            verdict = "CONVERGES (L < 1)"
        elif L_simplified > 1:
            verdict = "DIVERGES (L > 1)"
        else:
            verdict = "INCONCLUSIVE (L = 1) — try another test"

        steps.append(verdict)
        return _result(verdict, steps, "series")

    except Exception as e:
        return _result(f"Ratio test failed: {e}", [], "series")


def _root_test(problem_text: str) -> dict:
    """Root Test: lim |a(n)|^(1/n) as n→∞."""
    expr = _parse_series_term(problem_text)
    if expr is None:
        return _result("Could not parse series term for root test.", [], "series")

    try:
        L = sp.limit(sp.Abs(expr) ** (sp.Rational(1, 1) / n), n, sp.oo)
        L = sp.simplify(L)

        steps = [
            "Root Test: lim(n→∞) |a(n)|^(1/n)",
            f"a(n) = {expr}",
            f"L = {L}",
        ]

        if L < 1:
            verdict = "CONVERGES (L < 1)"
        elif L > 1:
            verdict = "DIVERGES (L > 1)"
        else:
            verdict = "INCONCLUSIVE (L = 1)"

        steps.append(verdict)
        return _result(verdict, steps, "series")

    except Exception as e:
        return _result(f"Root test failed: {e}", [], "series")


def _geometric_series(problem_text: str) -> dict:
    """Geometric series: ∑ a·r^n converges iff |r| < 1, sum = a/(1-r)."""
    expr = _parse_series_term(problem_text)
    steps = ["Geometric Series Test: ∑ a·rⁿ"]

    try:
        # Extract ratio r by computing a(n+1)/a(n)
        if expr is not None:
            ratio = sp.simplify(expr.subs(n, n + 1) / expr)
            r = sp.limit(ratio, n, sp.oo)
            r = sp.simplify(r)
            steps.append(f"Common ratio r = {r}")
            r_abs = sp.Abs(r)

            if r_abs < 1:
                # Try to find first term a
                a = sp.limit(expr / r**n, n, 0) if r != 0 else expr.subs(n, 0)
                series_sum = sp.simplify(a / (1 - r))
                steps += [
                    f"|r| = {sp.simplify(r_abs)} < 1 → CONVERGES",
                    f"Sum = a/(1-r) = {series_sum}",
                ]
                return _result(f"CONVERGES  |  Sum = {series_sum}", steps, "series")
            else:
                steps.append(f"|r| = {sp.simplify(r_abs)} ≥ 1 → DIVERGES")
                return _result("DIVERGES (|r| ≥ 1)", steps, "series")

    except Exception as e:
        steps.append(f"Could not evaluate: {e}")

    return _result("Could not determine — check ratio manually", steps, "series")


def _p_series_test(problem_text: str) -> dict:
    """p-series: ∑ 1/n^p converges iff p > 1."""
    steps = ["p-Series Test: ∑ 1/nᵖ"]
    p_val = _extract_p_value(problem_text)

    if p_val is None:
        return _result("Could not extract p value. Try: p-series p=2", steps, "series")

    steps.append(f"p = {p_val}")
    if p_val > 1:
        steps.append("p > 1 → CONVERGES")
        return _result(f"CONVERGES (p = {p_val} > 1)", steps, "series")
    else:
        steps.append("p ≤ 1 → DIVERGES")
        return _result(f"DIVERGES (p = {p_val} ≤ 1)", steps, "series")


def _integral_test(problem_text: str) -> dict:
    """Integral Test: ∑a(n) and ∫a(x)dx converge/diverge together."""
    expr_n = _parse_series_term(problem_text)
    if expr_n is None:
        return _result("Could not parse series term.", [], "series")

    expr_x = expr_n.subs(n, x)
    steps = [
        "Integral Test: ∑a(n) converges ↔ ∫a(x)dx converges",
        f"f(x) = {expr_x}",
    ]

    try:
        integral = sp.integrate(expr_x, (x, 1, sp.oo))
        integral = sp.simplify(integral)
        steps.append(f"∫(1→∞) f(x) dx = {integral}")

        if integral.is_finite and integral > 0:
            steps.append("Integral converges → Series CONVERGES")
            return _result(f"CONVERGES  (∫ = {integral})", steps, "series")
        else:
            steps.append("Integral diverges → Series DIVERGES")
            return _result("DIVERGES", steps, "series")
    except Exception as e:
        return _result(f"Integral test failed: {e}", steps, "series")


def _looks_geometric(expr) -> bool:
    return expr.has(sp.Pow) and any(
        str(s) in ("n", "k") for s in expr.free_symbols
    )


def _looks_p_series(expr) -> bool:
    return "1/n" in str(expr) or "n**-" in str(expr)


def _extract_p_value(text: str):
    match = re.search(r"p\s*=\s*([^\s,]+)", text, re.IGNORECASE)
    if match:
        try:
            return float(sp.sympify(match.group(1)))
        except Exception:
            pass
    # Try to infer from 1/n^p
    match = re.search(r"1/n\^([^\s,]+)", text)
    if match:
        try:
            return float(sp.sympify(match.group(1)))
        except Exception:
            pass
    return None


def _parse_series_term(text: str):
    """Parse the nth-term of a series from the problem text."""
    cleaned = re.sub(
        r"(series|sum|sigma|∑|converge[s]?|diverge[s]?|ratio test|root test|integral test|geometric|p-series|taylor|maclaurin)",
        "", text, flags=re.IGNORECASE
    ).strip()

    cleaned = (cleaned
        .replace("^", "**")
        .replace("n!", "factorial(n)")
        .replace("(n+1)!", "factorial(n+1)")
        .replace("ln(", "log(")
        .replace("π", "pi")
        .replace("∞", "oo")
    )
    cleaned = cleaned.split("=")[-1].strip()

    try:
        return sp.sympify(cleaned, locals={"n": n, "k": k, "x": x})
    except Exception:
        return None