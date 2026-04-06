# CalcSolver 🧮

A desktop app that analyzes screenshots of AP Calculus BC problems and returns exact answers.

## Vision
Upload a photo or screenshot of a handwritten or printed calculus problem → get the exact answer instantly.

## Topics Roadmap
| Day | Topic | Status |
|-----|-------|--------|
| 1 | Project scaffold + Limits (SymPy) | ✅ |
| 2 | Claude Vision API integration (parse images) | 🔲 |
| 3 | Derivatives solver | 🔲 |
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
- Python 3.10+
- sympy — symbolic math engine
- anthropic — Claude Vision API (Day 2)
- tkinter — built into Python standard library

## AP Calculus BC Topics Covered
1. **Limits** — L'Hôpital's rule, squeeze theorem, continuity
2. Derivatives (coming)
3. Integrals (coming)
4. Differential equations (coming)
5. Parametric & polar (coming)
6. Series & sequences (coming)
