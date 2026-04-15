"""Symbolic differentiation and integration engine powered by SymPy."""

from __future__ import annotations

from dataclasses import dataclass

import sympy as sp
from sympy.parsing.sympy_parser import (
    convert_xor,
    function_exponentiation,
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)

from parser import ParsedRequest, parse_request

x = sp.symbols("x")
C = sp.Symbol("C")
TRANSFORMATIONS = standard_transformations + (
    implicit_multiplication_application,
    convert_xor,
    function_exponentiation,
)
LOCAL_DICT = {
    "x": x,
    "e": sp.E,
    "pi": sp.pi,
    "ln": sp.log,
    "log": sp.log,
    "sin": sp.sin,
    "cos": sp.cos,
    "tan": sp.tan,
    "sec": sp.sec,
    "csc": sp.csc,
    "cot": sp.cot,
    "asin": sp.asin,
    "acos": sp.acos,
    "atan": sp.atan,
    "sinh": sp.sinh,
    "cosh": sp.cosh,
    "tanh": sp.tanh,
    "sqrt": sp.sqrt,
    "exp": sp.exp,
    "abs": sp.Abs,
    "oo": sp.oo,
}


@dataclass(frozen=True)
class SolveResult:
    operation: str
    input_expression: str
    result_text: str
    steps: list[str]
    pretty_result: str
    bounds_text: str | None = None

    def as_dict(self) -> dict:
        return {
            "operation": self.operation,
            "input_expression": self.input_expression,
            "result": self.result_text,
            "steps": self.steps,
            "pretty_result": self.pretty_result,
            "bounds": self.bounds_text,
        }


def solve(problem_text: str) -> dict:
    """Parse the request and return a symbolic derivative or integral."""
    try:
        request = parse_request(problem_text)
        expression = _parse_math_expression(request.expression_text)
        _validate_supported_symbols(expression)
    except Exception as exc:
        return {
            "error": str(exc),
            "steps": [],
        }

    try:
        if request.operation == "derivative":
            result = _solve_derivative(request, expression)
        elif request.operation == "integral":
            result = _solve_integral(request, expression)
        else:
            return {"error": "Unsupported operation.", "steps": []}
    except Exception as exc:
        return {
            "error": f"Could not complete the calculation: {exc}",
            "steps": [],
        }

    return result.as_dict()


def _solve_derivative(request: ParsedRequest, expression: sp.Expr) -> SolveResult:
    derivative = sp.simplify(sp.diff(expression, x))
    readable = sp.pretty(derivative, use_unicode=True)
    steps = [
        f"Recognized a derivative request in x.",
        f"Parsed expression: {sp.sstr(expression)}",
        f"Computed d/dx of the expression.",
    ]
    return SolveResult(
        operation="Derivative",
        input_expression=sp.sstr(expression),
        result_text=sp.sstr(derivative),
        steps=steps,
        pretty_result=readable,
    )


def _solve_integral(request: ParsedRequest, expression: sp.Expr) -> SolveResult:
    if request.bounds:
        lower = _parse_math_expression(request.bounds[0])
        upper = _parse_math_expression(request.bounds[1])
        _validate_supported_symbols(lower)
        _validate_supported_symbols(upper)
        integral = sp.simplify(sp.integrate(expression, (x, lower, upper)))
        readable = sp.pretty(integral, use_unicode=True)
        steps = [
            "Recognized a definite integral in x.",
            f"Parsed integrand: {sp.sstr(expression)}",
            f"Used bounds x = {sp.sstr(lower)} to x = {sp.sstr(upper)}.",
        ]
        if _is_unevaluated_integral(integral):
            steps.append("SymPy left the definite integral unevaluated.")
            result_text = f"Integral({sp.sstr(expression)}, (x, {sp.sstr(lower)}, {sp.sstr(upper)}))"
        else:
            steps.append("Evaluated the integral symbolically.")
            result_text = sp.sstr(integral)
        bounds_text = f"from {sp.sstr(lower)} to {sp.sstr(upper)}"
        return SolveResult(
            operation="Definite Integral",
            input_expression=sp.sstr(expression),
            result_text=result_text,
            steps=steps,
            pretty_result=readable,
            bounds_text=bounds_text,
        )

    integral = sp.simplify(sp.integrate(expression, x))
    if _is_unevaluated_integral(integral):
        steps = [
            "Recognized an indefinite integral in x.",
            f"Parsed integrand: {sp.sstr(expression)}",
            "No closed-form antiderivative was found, so the result remains symbolic.",
        ]
        return SolveResult(
            operation="Indefinite Integral",
            input_expression=sp.sstr(expression),
            result_text=sp.sstr(integral),
            steps=steps,
            pretty_result=sp.pretty(integral, use_unicode=True),
        )

    result_with_constant = integral + C
    readable = sp.pretty(result_with_constant, use_unicode=True)
    steps = [
        "Recognized an indefinite integral in x.",
        f"Parsed integrand: {sp.sstr(expression)}",
        "Computed an antiderivative and appended the constant of integration.",
    ]
    return SolveResult(
        operation="Indefinite Integral",
        input_expression=sp.sstr(expression),
        result_text=sp.sstr(result_with_constant),
        steps=steps,
        pretty_result=readable,
    )


def _parse_math_expression(expression_text: str) -> sp.Expr:
    parsed = parse_expr(
        expression_text,
        local_dict=LOCAL_DICT,
        transformations=TRANSFORMATIONS,
        evaluate=True,
    )
    return sp.simplify(parsed)


def _validate_supported_symbols(expression: sp.Expr) -> None:
    unsupported = sorted(
        symbol for symbol in expression.free_symbols if symbol != x
    )
    if unsupported:
        names = ", ".join(sp.sstr(symbol) for symbol in unsupported)
        raise ValueError(f"Only expressions in x are supported right now. Unsupported symbols: {names}")


def _is_unevaluated_integral(expression: sp.Expr) -> bool:
    return bool(expression.has(sp.Integral))
