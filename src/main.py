"""Minimal desktop UI for symbolic differentiation and integration."""

from __future__ import annotations

import ctypes
import tkinter as tk
from tkinter import ttk

from solver import solve

WINDOW_BG = "#ffd6ea"
PANEL_BG = "#fff5fa"
ACCENT = "#f95fa9"
ACCENT_DARK = "#211E1E"
TEXT = "#ff69c8"
MUTED = "#4A0923"
ERROR = "#ff1934"
ENTRY_BG = "#fffafd"
HEADER_BG = "#ffc2df"
FONT_FAMILY = "Playfair Display"
INTEGRAL_FONT_FAMILY = "Gowun Batang"
MATH_FONT_FAMILY = "Cambria Math"

EXAMPLES = (
    "diff x^4*sin(x)",
    "int x^2*exp(x)",
    "int 1/(1+x^2) from 0 to 1",
)
STARTER_TEXT = """Type one of these forms:

- diff x^3*cos(x)
- int sin(x)
- int 1/(1+x^2) from 0 to 1

Supported input is manual text only, focused on symbolic derivatives and integrals in x."""


class CalculusCalculatorApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Symbolic Calculus Calculator")
        self.root.geometry("830x930")
        self.root.minsize(640, 500)
        self.root.configure(bg=WINDOW_BG)
        self._build_style()
        self._build_ui()
        self.root.bind("<Control-l>", lambda _event: self.clear())

    def _build_style(self) -> None:
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("App.TFrame", background=WINDOW_BG)
        style.configure("Panel.TFrame", background=PANEL_BG)
        style.configure("Header.TFrame", background=HEADER_BG)
        style.configure(
            "Title.TLabel",
            background=HEADER_BG,
            foreground=ACCENT_DARK,
            font=(FONT_FAMILY, 22, "bold"),
        )
        style.configure(
            "Body.TLabel",
            background=WINDOW_BG,
            foreground=MUTED,
            font=(FONT_FAMILY, 11),
        )
        style.configure(
            "Examples.TLabel",
            background=PANEL_BG,
            foreground=MUTED,
            font=(MATH_FONT_FAMILY, 11),
        )
        style.configure(
            "PanelTitle.TLabel",
            background=PANEL_BG,
            foreground=ACCENT_DARK,
            font=(FONT_FAMILY, 12, "bold"),
        )
        style.configure("Calc.TButton", font=(FONT_FAMILY, 11, "bold"), padding=(12, 8))

    def _build_ui(self) -> None:
        container = ttk.Frame(self.root, style="App.TFrame", padding=20)
        container.pack(fill="both", expand=True)

        header_panel = ttk.Frame(container, style="Header.TFrame", padding=(18, 14))
        header_panel.pack(fill="x")

        tk.Label(
            header_panel,
            text="∫",
            bg=HEADER_BG,
            fg=ACCENT,
            font=(INTEGRAL_FONT_FAMILY, 64, "bold"),
        ).pack(side="left", padx=(0, 12))

        header_text = ttk.Frame(header_panel, style="Header.TFrame")
        header_text.pack(side="left", fill="x", expand=True)

        ttk.Label(header_text, text="Symbolic Calculus Calculator", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            header_text,
            text="A tool made by Runnp and AI. Type your problem below. And we love Calculus!",
            style="Body.TLabel",
        ).pack(anchor="w", pady=(4, 0))

        input_panel = ttk.Frame(container, style="Panel.TFrame", padding=16)
        input_panel.pack(fill="x", pady=(16, 0))

        ttk.Label(input_panel, text="Input", style="PanelTitle.TLabel").pack(anchor="w")

        self.input_var = tk.StringVar()
        self.input_entry = tk.Entry(
            input_panel,
            textvariable=self.input_var,
            font=(MATH_FONT_FAMILY, 12),
            bg=ENTRY_BG,
            fg="#000000",
            relief="flat",
            insertbackground="#000000",
            insertwidth=1,
            highlightthickness=1,
            highlightbackground="#f59ac7",
            highlightcolor=ACCENT,
        )
        self.input_entry.pack(fill="x", pady=(10, 8), ipady=4)
        self.input_entry.bind("<Return>", lambda _event: self.calculate())

        example_text = "Examples: " + "   |   ".join(EXAMPLES)
        ttk.Label(input_panel, text=example_text, style="Examples.TLabel", wraplength=600).pack(anchor="w")

        actions = ttk.Frame(input_panel, style="Panel.TFrame")
        actions.pack(fill="x", pady=(12, 0))

        ttk.Button(actions, text="Calculate", style="Calc.TButton", command=self.calculate).pack(side="left")
        ttk.Button(actions, text="Clear", command=self.clear).pack(side="left", padx=(10, 0))

        output_panel = ttk.Frame(container, style="Panel.TFrame", padding=16)
        output_panel.pack(fill="both", expand=True, pady=(16, 0))

        ttk.Label(output_panel, text="Output", style="PanelTitle.TLabel").pack(anchor="w")

        self.status_label = tk.Label(
            output_panel,
            text="Ready",
            anchor="w",
            bg=PANEL_BG,
            fg=MUTED,
            font=(FONT_FAMILY, 11),
        )
        self.status_label.pack(fill="x", pady=(10, 8))

        self.output_text = tk.Text(
            output_panel,
            wrap="word",
            font=(MATH_FONT_FAMILY, 12),
            bg="#fffafd",
            fg=TEXT,
            relief="flat",
            padx=12,
            pady=12,
            state="disabled",
        )
        self.output_text.pack(fill="both", expand=True)

        self._set_output(STARTER_TEXT)
        self.input_entry.focus_set()

    def calculate(self) -> None:
        user_input = self.input_var.get().strip()
        if not user_input:
            self._show_message("Enter a request like 'diff x^3' or 'int sin(x)'.", is_error=True)
            return

        result = solve(user_input)
        if result.get("error"):
            self._show_message(result["error"], is_error=True)
            return

        lines = [
            f"Operation: {result['operation']}",
            f"Expression: {result['input_expression']}",
        ]
        if result.get("bounds"):
            lines.append(f"Bounds: {result['bounds']}")
        lines.extend(
            [
                "",
                "Result:",
                result["result"],
                "",
                "Pretty view:",
                result["pretty_result"],
            ]
        )

        if result.get("steps"):
            lines.append("")
            lines.append("Steps:")
            for index, step in enumerate(result["steps"], start=1):
                lines.append(f"{index}. {step}")

        self.status_label.config(text="Calculation complete.", fg=MUTED)
        self._set_output("\n".join(lines))

    def clear(self) -> None:
        self.input_var.set("")
        self.status_label.config(text="Ready", fg=MUTED)
        self._set_output(STARTER_TEXT)
        self.input_entry.focus_set()

    def _show_message(self, message: str, *, is_error: bool) -> None:
        self.status_label.config(text=message, fg=ERROR if is_error else MUTED)
        self._set_output(message)

    def _set_output(self, content: str) -> None:
        self.output_text.config(state="normal")
        self.output_text.delete("1.0", "end")
        self.output_text.insert("1.0", content)
        self.output_text.config(state="disabled")


if __name__ == "__main__":
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

    root = tk.Tk()
    app = CalculusCalculatorApp(root)
    root.mainloop()
