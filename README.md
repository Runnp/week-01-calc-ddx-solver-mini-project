# CalcDdxSolver f'(x) → ∫ f(x) dx

Created by Runnp + Claude

A desktop app that analyzes Calculus problems on Differentiation and Integration to return their solutions.

## Vision
Taking an integral is the most popular and widely used operation in calculus analysis, more frequently than taking the derivative of a function. My goal is to build a tool that would get the exact answer to my problem instantly, being able to implement fundamental theorem of calculus.


## Topics Roadmap
| Day | Topic | Status |
|-----|-------|--------|
| 1 | Project scaffold + Limits (SymPy) | ✅ |
| 2 | Claude Vision API integration (parse images) | ✅ |
| 3 | Derivatives solver | ✅ |
| 4 | Implicit differentiation + related rates | 🔲 |
| 5 | Integrals (u-sub, by parts) | 🔲 |
| 6 | FTC + improper integrals | 🔲 |
| 7 | Series + polish UI | 🔲 |

## Project Structure
```
calculus-solver/
├── src/
│   ├── main.py      # GUI window (tkinter)
│   ├── parser.py    # Screenshot → problem text (Claude Vision)
│   └── solver.py    # Problem text → answer (SymPy)
├── tests/
│   └── sample_problems/   # Test screenshots
├── requirements.txt
└── README.md
```

## Setup
```bash
pip install -r requirements.txt
python src/main.py
```

## Requirements
- python 3.10+
- sympy — symbolic math engine
- pillow — python imagining library
- tkinter — built into python standard library
- anthropic — Claude Vision API


## AP Calculus BC Topics Covered
1. **Limits** — L'Hôpital's rule, squeeze theorem, continuity
2. Derivatives (coming)
3. Integrals (coming)
4. Differential equations (coming)
5. Parametric & polar (coming)
6. Series & sequences (coming)
