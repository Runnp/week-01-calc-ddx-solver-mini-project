"""
CalcSolver - AP Calculus BC Problem Solver
Day 7, Push 1: Direct text input — type problems without needing a screenshot.
Day 7, Push 2: Smart error messages + input validation + suggestions.
Day 7, Push 3: Final polish — keyboard shortcuts, clear button, window icon title.
"""

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import threading
from parser import parse_image, extract_topic
from solver import solve

TOPIC_COLORS = {
    "limits":      "#00aaff",
    "derivatives": "#ff9900",
    "integrals":   "#cc66ff",
    "series":      "#ff4466",
}

# Push 2: helpful suggestions shown when topic is unknown
SUGGESTIONS = [
    "Limits:      lim(x->0) sin(x)/x",
    "Derivative:  d/dx x^3 + 2*x",
    "Implicit:    x^2 + y^2 = 25",
    "Integral:    integrate x^2",
    "Definite:    integrate x^2 from 0 to 1",
    "IBP:         integrate x*ln(x)",
    "Maclaurin:   maclaurin sin(x)",
    "Taylor:      taylor e^x at x=1",
    "Ratio test:  ratio test n!/2^n",
    "p-series:    p-series p=3",
]


class CalcSolverApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CalcSolver — AP Calculus BC")
        self.root.geometry("740x820")
        self.root.configure(bg="#0f0f0f")
        self.root.resizable(False, False)
        self.history = []
        self._build_ui()
        # Push 3: keyboard shortcuts
        self.root.bind("<Return>", lambda e: self._solve_typed())
        self.root.bind("<Control-o>", lambda e: self.load_image())
        self.root.bind("<Control-l>", lambda e: self._clear_all())

    def _build_ui(self):
        # ── Header ────────────────────────────────────────────────────────────
        tk.Label(self.root, text="CalcSolver",
            font=("Courier New", 24, "bold"), fg="#00ff88", bg="#0f0f0f"
        ).pack(pady=(16, 2))
        tk.Label(self.root, text="AP Calculus BC · Type or Screenshot → Answer",
            font=("Courier New", 10), fg="#555555", bg="#0f0f0f"
        ).pack()

        # ── Push 1: Direct text input ─────────────────────────────────────────
        tk.Label(self.root, text="Type a problem:",
            font=("Courier New", 9), fg="#444444", bg="#0f0f0f"
        ).pack(anchor="w", padx=40, pady=(14, 0))

        input_row = tk.Frame(self.root, bg="#0f0f0f")
        input_row.pack(fill="x", padx=40, pady=(4, 0))

        self.input_entry = tk.Entry(input_row,
            font=("Courier New", 12), fg="#cccccc", bg="#1a1a1a",
            relief="flat", insertbackground="#00ff88",
        )
        self.input_entry.pack(side="left", fill="x", expand=True, ipady=8, padx=(0, 8))

        self.solve_btn = tk.Button(input_row,
            text="[ Solve ]",
            font=("Courier New", 11), fg="#00ff88", bg="#1a1a1a",
            activebackground="#00ff88", activeforeground="#0f0f0f",
            relief="flat", cursor="hand2", command=self._solve_typed,
            padx=12, pady=4,
        )
        self.solve_btn.pack(side="right")

        # Push 2: example hint below input
        self.hint_label = tk.Label(self.root,
            text="e.g.  d/dx x^3 + 2*x   |   integrate x*ln(x)   |   maclaurin sin(x)",
            font=("Courier New", 8), fg="#2a2a2a", bg="#0f0f0f"
        )
        self.hint_label.pack(anchor="w", padx=40, pady=(3, 0))

        # ── Divider ───────────────────────────────────────────────────────────
        tk.Label(self.root, text="── or upload a screenshot ──",
            font=("Courier New", 8), fg="#2a2a2a", bg="#0f0f0f"
        ).pack(pady=(10, 4))

        btn_row = tk.Frame(self.root, bg="#0f0f0f")
        btn_row.pack()

        self.upload_btn = tk.Button(btn_row,
            text="[ Upload Screenshot ]",
            font=("Courier New", 10), fg="#555555", bg="#1a1a1a",
            activebackground="#555555", activeforeground="#0f0f0f",
            relief="flat", cursor="hand2", command=self.load_image,
            pady=6, padx=16,
        )
        self.upload_btn.pack(side="left", padx=(0, 8))

        # Push 3: clear button
        tk.Button(btn_row,
            text="[ Clear ]",
            font=("Courier New", 10), fg="#333333", bg="#1a1a1a",
            activebackground="#333333", activeforeground="#0f0f0f",
            relief="flat", cursor="hand2", command=self._clear_all,
            pady=6, padx=12,
        ).pack(side="left")

        # ── Detected problem ──────────────────────────────────────────────────
        tk.Label(self.root, text="Problem:",
            font=("Courier New", 9), fg="#444444", bg="#0f0f0f"
        ).pack(anchor="w", padx=40, pady=(12, 0))

        self.problem_text = tk.Text(self.root,
            height=2, font=("Courier New", 11), fg="#cccccc", bg="#1a1a1a",
            relief="flat", padx=10, pady=6, state="disabled", wrap="word",
        )
        self.problem_text.pack(fill="x", padx=40, pady=(2, 4))

        self.topic_label = tk.Label(self.root, text="",
            font=("Courier New", 9), fg="#00ff88", bg="#0f0f0f"
        )
        self.topic_label.pack(anchor="w", padx=40)

        # ── Steps ─────────────────────────────────────────────────────────────
        tk.Label(self.root, text="Steps:",
            font=("Courier New", 9), fg="#444444", bg="#0f0f0f"
        ).pack(anchor="w", padx=40, pady=(8, 0))

        self.steps_text = scrolledtext.ScrolledText(self.root,
            height=5, font=("Courier New", 10), fg="#888888", bg="#111111",
            relief="flat", padx=10, pady=6, state="disabled", wrap="word",
        )
        self.steps_text.pack(fill="x", padx=40, pady=(2, 8))

        # ── Answer ────────────────────────────────────────────────────────────
        tk.Label(self.root, text="Answer:",
            font=("Courier New", 9), fg="#444444", bg="#0f0f0f"
        ).pack(anchor="w", padx=40)

        answer_row = tk.Frame(self.root, bg="#0f0f0f")
        answer_row.pack(fill="x", padx=40, pady=(2, 0))

        self.answer_text = tk.Label(answer_row,
            text="—", font=("Courier New", 18, "bold"),
            fg="#00ff88", bg="#1a1a1a", pady=10,
            relief="flat", anchor="w", padx=12,
        )
        self.answer_text.pack(side="left", fill="x", expand=True)

        self.copy_btn = tk.Button(answer_row,
            text="copy", font=("Courier New", 9),
            fg="#555555", bg="#1a1a1a", relief="flat",
            cursor="hand2", command=self.copy_answer, padx=10,
        )
        self.copy_btn.pack(side="right", fill="y")

        # ── Push 2: suggestions panel (shown on unknown topic) ────────────────
        self.suggestions_frame = tk.Frame(self.root, bg="#0f0f0f")
        self.suggestions_frame.pack(fill="x", padx=40, pady=(6, 0))
        self.suggestions_label = tk.Label(self.suggestions_frame,
            text="", font=("Courier New", 9), fg="#ff4444",
            bg="#0f0f0f", justify="left", wraplength=640,
        )
        self.suggestions_label.pack(anchor="w")

        # ── History ───────────────────────────────────────────────────────────
        tk.Label(self.root, text="History:",
            font=("Courier New", 9), fg="#444444", bg="#0f0f0f"
        ).pack(anchor="w", padx=40, pady=(12, 0))

        self.history_text = scrolledtext.ScrolledText(self.root,
            height=4, font=("Courier New", 9), fg="#555555", bg="#0a0a0a",
            relief="flat", padx=10, pady=6, state="disabled", wrap="word",
        )
        self.history_text.pack(fill="x", padx=40, pady=(2, 0))

        # ── Status bar ────────────────────────────────────────────────────────
        # Push 3: show keyboard shortcuts in status bar
        self.status = tk.Label(self.root,
            text="Ready  ·  Enter = solve  ·  Ctrl+O = upload  ·  Ctrl+L = clear",
            font=("Courier New", 8), fg="#2a2a2a", bg="#0f0f0f"
        )
        self.status.pack(side="bottom", pady=8)

    # ── Push 1: solve from typed input ───────────────────────────────────────

    def _flash_hint(self):
        """Briefly highlight the hint to guide the user."""
        self.hint_label.config(fg="#ff4444")
        self.root.after(1200, lambda: self.hint_label.config(fg="#2a2a2a"))

    # ── Upload screenshot ─────────────────────────────────────────────────────

    def load_image(self):
        path = filedialog.askopenfilename(
            filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp *.tiff *.webp")]
        )
        if not path:
            return
        self._set_busy("Reading image with OCR...")
        threading.Thread(target=self._process_image, args=(path,), daemon=True).start()

    def _process_image(self, path: str):
        try:
            problem = parse_image(path)
            self.root.after(0, self.input_entry.delete, 0, "end")
            self.root.after(0, self.input_entry.insert, 0, problem)
            self.root.after(0, self._run_solver, problem)
        except Exception as e:
            self.root.after(0, messagebox.showerror, "OCR Error", f"Could not read image:\n{e}")
            self.root.after(0, self._set_status, "OCR failed.")
            self.root.after(0, self._reset_buttons)

    # ── Core solver runner ────────────────────────────────────────────────────

    def _run_solver(self, problem: str):
        self._set_busy("Solving...")
        self._set_problem(problem)
        self.answer_text.config(text="—")
        self.suggestions_label.config(text="")
        self._set_steps([])
        threading.Thread(target=self._solve_thread, args=(problem,), daemon=True).start()

    def _solve_thread(self, problem: str):
        try:
            result = solve(problem)
            answer  = result.get("answer", "—")
            steps   = result.get("steps", [])
            topic   = result.get("topic", "unknown")

            self.root.after(0, self._set_steps, steps)
            self.root.after(0, self._set_answer, answer)
            self.root.after(0, self._add_history, problem, answer)

            # Push 2: show suggestions if topic unknown or answer is error-like
            if topic == "unknown" or answer.startswith("Could not"):
                self.root.after(0, self._show_suggestions)
            else:
                self.root.after(0, self.suggestions_label.config, {"text": ""})

            self.root.after(0, self._set_status,
                "Done  ·  Enter = solve  ·  Ctrl+O = upload  ·  Ctrl+L = clear")
        except Exception as e:
            self.root.after(0, messagebox.showerror, "Error", f"Something went wrong:\n{e}")
            self.root.after(0, self._set_status, f"Error: {e}")
        finally:
            self.root.after(0, self._reset_buttons)

    # ── Push 2: suggestions ───────────────────────────────────────────────────

    def _show_suggestions(self):
        self.suggestions_label.config(
            text="Topic not recognized. Try one of these formats:\n" +
                 "\n".join(f"  · {s}" for s in SUGGESTIONS[:5])
        )

    # ── Push 3: clear ─────────────────────────────────────────────────────────

    def _clear_all(self):
        self.input_entry.delete(0, "end")
        self._set_problem("")
        self._set_steps([])
        self.answer_text.config(text="—")
        self.topic_label.config(text="")
        self.suggestions_label.config(text="")
        self._set_status("Cleared  ·  Enter = solve  ·  Ctrl+O = upload  ·  Ctrl+L = clear")
        self.input_entry.focus()

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _set_busy(self, msg: str):
        self.upload_btn.config(state="disabled")
        self.solve_btn.config(state="disabled", text="[ ... ]")
        self._set_status(msg)
        self.root.update()

    def _reset_buttons(self):
        self.upload_btn.config(state="normal")
        self.solve_btn.config(state="normal", text="[ Solve ]")

    def _set_problem(self, text: str):
        self.problem_text.config(state="normal")
        self.problem_text.delete("1.0", "end")
        self.problem_text.insert("end", text)
        self.problem_text.config(state="disabled")
        topic = extract_topic(text)
        if topic != "unknown" and text:
            color = TOPIC_COLORS.get(topic, "#00ff88")
            self.topic_label.config(text=f"topic: {topic}", fg=color)
        else:
            self.topic_label.config(text="")

    def _set_steps(self, steps: list):
        self.steps_text.config(state="normal")
        self.steps_text.delete("1.0", "end")
        for i, step in enumerate(steps, 1):
            self.steps_text.insert("end", f"  {i}. {step}\n")
        self.steps_text.config(state="disabled")

    def _set_answer(self, answer: str):
        self.answer_text.config(text=answer)

    def copy_answer(self):
        answer = self.answer_text.cget("text")
        if answer and answer != "—":
            self.root.clipboard_clear()
            self.root.clipboard_append(answer)
            self.copy_btn.config(text="copied!", fg="#00ff88")
            self.root.after(1500, lambda: self.copy_btn.config(text="copy", fg="#555555"))

    def _add_history(self, problem: str, answer: str):
        self.history.insert(0, (problem, answer))
        self.history = self.history[:5]
        self.history_text.config(state="normal")
        self.history_text.delete("1.0", "end")
        for i, (p, a) in enumerate(self.history, 1):
            short_p = p[:42] + "..." if len(p) > 42 else p
            self.history_text.insert("end", f"  {i}. {short_p}  →  {a}\n")
        self.history_text.config(state="disabled")

    def _set_status(self, msg: str):
        self.status.config(text=msg)


if __name__ == "__main__":
    root = tk.Tk()
    app = CalcSolverApp(root)
    app.input_entry.focus()
    root.mainloop()
