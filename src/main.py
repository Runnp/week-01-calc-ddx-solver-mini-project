"""
CalcSolver - AP Calculus BC Problem Solver
Day 2, Push 3: Full pipeline connected — Vision API → parser → solver → GUI.
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import threading
from parser import parse_image
from solver import solve


class CalcSolverApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CalcSolver — AP Calculus BC")
        self.root.geometry("700x520")
        self.root.configure(bg="#0f0f0f")
        self.root.resizable(False, False)

        self._build_ui()

    def _build_ui(self):
        # Header
        tk.Label(
            self.root,
            text="CalcSolver",
            font=("Courier New", 28, "bold"),
            fg="#00ff88",
            bg="#0f0f0f",
        ).pack(pady=(30, 4))

        tk.Label(
            self.root,
            text="AP Calculus BC · Screenshot → Answer",
            font=("Courier New", 11),
            fg="#555555",
            bg="#0f0f0f",
        ).pack()

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
        self.upload_btn.pack(pady=24)

        # Problem display
        tk.Label(
            self.root,
            text="Detected Problem:",
            font=("Courier New", 10),
            fg="#444444",
            bg="#0f0f0f",
        ).pack(anchor="w", padx=40)

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
            wrap="word",
        )
        self.problem_text.pack(fill="x", padx=40, pady=(4, 16))

        # Topic badge
        self.topic_label = tk.Label(
            self.root,
            text="",
            font=("Courier New", 10),
            fg="#00ff88",
            bg="#0f0f0f",
        )
        self.topic_label.pack(anchor="w", padx=40)

        # Answer display
        tk.Label(
            self.root,
            text="Answer:",
            font=("Courier New", 10),
            fg="#444444",
            bg="#0f0f0f",
        ).pack(anchor="w", padx=40, pady=(8, 0))

        self.answer_text = tk.Label(
            self.root,
            text="—",
            font=("Courier New", 22, "bold"),
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
            filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp *.tiff *.webp")]
        )
        if not path:
            return

        # Disable button during processing
        self.upload_btn.config(state="disabled", text="[ Processing... ]")
        self._set_status("Sending to Claude Vision API...")
        self.answer_text.config(text="—")
        self.topic_label.config(text="")
        self.root.update()

        # Run in background thread so GUI doesn't freeze
        thread = threading.Thread(target=self._process_image, args=(path,), daemon=True)
        thread.start()

    def _process_image(self, path: str):
        """Runs in background thread — calls API then updates GUI on main thread."""
        try:
            self.root.after(0, self._set_status, "Extracting problem from image...")
            problem = parse_image(path)

            self.root.after(0, self._set_problem, problem)
            self.root.after(0, self._set_status, "Solving...")

            answer = solve(problem)

            self.root.after(0, self._set_answer, answer)
            self.root.after(0, self._set_status, "Done.")

        except EnvironmentError as e:
            self.root.after(0, messagebox.showerror, "API Key Missing", str(e))
            self.root.after(0, self._set_status, "Error: API key not set.")
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

        from parser import extract_topic
        topic = extract_topic(text)
        if topic != "unknown":
            self.topic_label.config(text=f"topic: {topic}")

    def _set_answer(self, answer: str):
        self.answer_text.config(text=answer)

    def _set_status(self, msg: str):
        self.status.config(text=msg)

    def _reset_button(self):
        self.upload_btn.config(state="normal", text="[ Upload Screenshot ]")


if __name__ == "__main__":
    root = tk.Tk()
    app = CalcSolverApp(root)
    root.mainloop()