# CalcDdxSolver f'(x) → ∫ f(x) dx 🔴🌸🎀🦩💕🌷

A lightweight local desktop calculator for symbolic calculus.

It focuses only on two operations:

- Differentiation
- Integration

The app runs locally with `tkinter` for the desktop UI and `sympy` for symbolic math. There are no API keys, subscriptions, or paid services involved.

## Pipeline

- Accepts manual text input only
- Computes symbolic derivatives in `x`
- Computes indefinite integrals in `x`
- Computes definite integrals such as `integrate 1/(1+x^2) from 0 to 1`
- Shows a readable plain result and a pretty-printed math view

## Scope

- Supported:
  - `diff x^3*sin(x)`
  - `d/dx ln(x) + x^2`
  - `int x^2*exp(x)`
  - `int 1/(1+x^2) from 0 to 1`


## Structure

```text
src/
  main.py    # tkinter desktop UI
  parser.py  # manual text parsing and request normalization
  solver.py  # symbolic derivative/integral engine using SymPy
```

## Setup

1. Install dependencies:

```bash
pip install -r Requirements.txt
```

2. Run the app:

```bash
python src/main.py
```

## Input

```text
diff x^4*sin(x)
diff sqrt(x) + ln(x)
int sin(x)
int x^2*exp(x)
int 1/(1+x^2) from 0 to 1
```

## Notes

- Expressions are currently validated for `x`-based calculus only.
- If SymPy cannot reduce an integral to a closed form, the app keeps the result symbolic instead of pretending it was fully solved.
- The UI is intentionally small and minimal: input, output, and simple controls.
