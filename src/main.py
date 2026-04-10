"""
CalcSolver - AP Calculus BC Problem Solver
Day 5, Push 3: History panel + copy answer button.
"""

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import threading
from parser import parse_image, extract_topic
from solver import solve


class CalcSolverApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CalcSolver — AP Calculus BC")
        self.root.geometry("720x720")
        self.root.configure(bg="#0f0f0f")
        self.root.resizable(False, False)
        self.history = []  # list of (problem, answer) tuples
        self._build_ui()

    def _build_ui(self):
        # Header
        tk.Label(self.root, text="CalcSolver",
            font=("Courier New", 24, "bold"), fg="#00ff88", bg="#0f0f0f"
        ).pack(pady=(16, 2))
        tk.Label(self.root, text="AP Calculus BC · Screenshot → Answer",
            font=("Courier New", 10), fg="#555555", bg="#0f0f0f"
        ).pack()

        # Upload button
        self.upload_btn = tk.Button(self.root,
            text="[ Upload Screenshot ]",
            font=("Courier New", 12), fg="#00ff88", bg="#1a1a1a",
            activebackground="#00ff88", activeforeground="#0f0f0f",
            relief="flat", cursor="hand2", command=self.load_image,
            pady=10, padx=20,
        )
        self.upload_btn.pack(pady=14)

        # Problem
        tk.Label(self.root, text="Detected Problem:",
            font=("Courier New", 9), fg="#444444", bg="#0f0f0f"
        ).pack(anchor="w", padx=40)
        self.problem_text = tk.Text(self.root,
            height=2, font=("Courier New", 11), fg="#cccccc", bg="#1a1a1a",
            relief="flat", padx=10, pady=6, state="disabled", wrap="word",
        )
        self.problem_text.pack(fill="x", padx=40, pady=(2, 4))
        self.topic_label = tk.Label(self.root, text="",
            font=("Courier New", 9), fg="#00ff88", bg="#0f0f0f"
        )
        self.topic_label.pack(anchor="w", padx=40)

        # Steps
        tk.Label(self.root, text="Steps:",
            font=("Courier New", 9), fg="#444444", bg="#0f0f0f"
        ).pack(anchor="w", padx=40, pady=(8, 0))
        self.steps_text = scrolledtext.ScrolledText(self.root,
            height=5, font=("Courier New", 10), fg="#888888", bg="#111111",
            relief="flat", padx=10, pady=6, state="disabled", wrap="word",
        )
        self.steps_text.pack(fill="x", padx=40, pady=(2, 8))

        # Answer row
        tk.Label(self.root, text="Answer:",
            font=("Courier New", 9), fg="#444444", bg="#0f0f0f"
        ).pack(anchor="w", padx=40)

        answer_row = tk.Frame(self.root, bg="#0f0f0f")
        answer_row.pack(fill="x", padx=40, pady=(2, 0))

        self.answer_text = tk.Label(answer_row,
            text="—", font=("Courier New", 18, "bold"),
            fg="#00ff88", bg="#1a1a1a", pady=10, relief="flat", anchor="w", padx=12,
        )
        self.answer_text.pack(side="left", fill="x", expand=True)

        self.copy_btn = tk.Button(answer_row,
            text="copy", font=("Courier New", 9),
            fg="#555555", bg="#1a1a1a", relief="flat",
            cursor="hand2", command=self.copy_answer,
            padx=10,
        )
        self.copy_btn.pack(side="right", fill="y")

        # History panel
        tk.Label(self.root, text="History:",
            font=("Courier New", 9), fg="#444444", bg="#0f0f0f"
        ).pack(anchor="w", padx=40, pady=(14, 0))

        self.history_text = scrolledtext.ScrolledText(self.root,
            height=5, font=("Courier New", 9), fg="#555555", bg="#0a0a0a",
            relief="flat", padx=10, pady=6, state="disabled", wrap="word",
        )
        self.history_text.pack(fill="x", padx=40, pady=(2, 0))

        # Status
        self.status = tk.Label(self.root,
            text="Ready. Upload a screenshot to begin.",
            font=("Courier New", 9), fg="#333333", bg="#0f0f0f"
        )
        self.status.pack(side="bottom", pady=8)

    def load_image(self):
        path = filedialog.askopenfilename(
            filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp *.tiff *.webp")]
        )
        if not path:
            return
        self.upload_btn.config(state="disabled", text="[ Processing... ]")
        self._set_status("Reading image with OCR...")
        self.answer_text.config(text="—")
        self.topic_label.config(text="")
        self._set_steps([])
        self.root.update()
        threading.Thread(target=self._process_image, args=(path,), daemon=True).start()

    def _process_image(self, path: str):
        try:
            self.root.after(0, self._set_status, "Extracting problem...")
            problem = parse_image(path)
            self.root.after(0, self._set_problem, problem)
            self.root.after(0, self._set_status, "Solving...")
            result = solve(problem)
            answer = result.get("answer", "—")
            steps  = result.get("steps", [])
            self.root.after(0, self._set_steps, steps)
            self.root.after(0, self._set_answer, answer)
            self.root.after(0, self._add_history, problem, answer)
            self.root.after(0, self._set_status, "Done.")
        except Exception as e:
            self.root.after(0, messagebox.showerror, "Error", f"Something went wrong:\n{e}")
            self.root.after(0, self._set_status, f"Error: {e}")
        finally:
            self.root.after(0, self._reset_button)

    def _set_problem(self, text: str):
        self.problem_text.config(state="normal")
        self.problem_text.delete("1.0", "end")
        self.problem_text.insert("end", text)
        self.problem_text.config(state="disabled")
        topic = extract_topic(text)
        if topic != "unknown":
            self.topic_label.config(text=f"topic: {topic}")

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
        self.history = self.history[:5]  # keep last 5
        self.history_text.config(state="normal")
        self.history_text.delete("1.0", "end")
        for i, (p, a) in enumerate(self.history, 1):
            short_p = p[:40] + "..." if len(p) > 40 else p
            self.history_text.insert("end", f"  {i}. {short_p}  →  {a}\n")
        self.history_text.config(state="disabled")

    def _set_status(self, msg: str):
        self.status.config(text=msg)

    def _reset_button(self):
        self.upload_btn.config(state="normal", text="[ Upload Screenshot ]")


if __name__ == "__main__":
    root = tk.Tk()
    app = CalcSolverApp(root)
    root.mainloop()