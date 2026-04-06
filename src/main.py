"""
CalcSolver - AP Calculus BC Problem Solver
Day 1: Project scaffold + GUI skeleton
"""

import tkinter as tk
from tkinter import filedialog, ttk
from parser import parse_image
from solver import solve


class CalcSolverApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CalcSolver — AP Calculus BC")
        self.root.geometry("700x500")
        self.root.configure(bg="#0f0f0f")

        self._build_ui()

    def _build_ui(self):
        # Header
        header = tk.Label(
            self.root,
            text="CalcSolver",
            font=("Courier New", 28, "bold"),
            fg="#00ff88",
            bg="#0f0f0f",
        )
        header.pack(pady=(30, 4))

        subtitle = tk.Label(
            self.root,
            text="AP Calculus BC · Screenshot → Answer",
            font=("Courier New", 11),
            fg="#555555",
            bg="#0f0f0f",
        )
        subtitle.pack()

        # Upload button
        self.upload_btn = tk.Button(
            self.root,
            text="[ Upload Screenshot ]",
            font=("Courier New", 13),
            fg="#00ff88",
            bg="#1a1a1a",
            activebackground="#00ff88",
            activeforeground="#0f0f0f",
            relief="flat",
            cursor="hand2",
            command=self.load_image,
            pady=12,
            padx=24,
        )
        self.upload_btn.pack(pady=30)

        # Problem display
        self.problem_label = tk.Label(
            self.root,
            text="Detected Problem:",
            font=("Courier New", 10),
            fg="#444444",
            bg="#0f0f0f",
        )
        self.problem_label.pack(anchor="w", padx=40)

        self.problem_text = tk.Text(
            self.root,
            height=4,
            font=("Courier New", 12),
            fg="#cccccc",
            bg="#1a1a1a",
            relief="flat",
            padx=12,
            pady=8,
            state="disabled",
        )
        self.problem_text.pack(fill="x", padx=40, pady=(4, 16))

        # Answer display
        self.answer_label = tk.Label(
            self.root,
            text="Answer:",
            font=("Courier New", 10),
            fg="#444444",
            bg="#0f0f0f",
        )
        self.answer_label.pack(anchor="w", padx=40)

        self.answer_text = tk.Label(
            self.root,
            text="—",
            font=("Courier New", 20, "bold"),
            fg="#00ff88",
            bg="#1a1a1a",
            pady=14,
            relief="flat",
        )
        self.answer_text.pack(fill="x", padx=40, pady=(4, 0))

        # Status bar
        self.status = tk.Label(
            self.root,
            text="Ready. Upload a screenshot to begin.",
            font=("Courier New", 9),
            fg="#333333",
            bg="#0f0f0f",
        )
        self.status.pack(side="bottom", pady=10)

    def load_image(self):
        path = filedialog.askopenfilename(
            filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp *.tiff")]
        )
        if not path:
            return

        self.status.config(text=f"Parsing: {path.split('/')[-1]} ...")
        self.root.update()

        problem = parse_image(path)
        self._set_problem(problem)

        answer = solve(problem)
        self.answer_text.config(text=answer)
        self.status.config(text="Done.")

    def _set_problem(self, text):
        self.problem_text.config(state="normal")
        self.problem_text.delete("1.0", "end")
        self.problem_text.insert("end", text)
        self.problem_text.config(state="disabled")


if __name__ == "__main__":
    root = tk.Tk()
    app = CalcSolverApp(root)
    root.mainloop()