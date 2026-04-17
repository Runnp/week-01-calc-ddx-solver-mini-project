"""Minimal desktop UI for symbolic differentiation and integration."""

from __future__ import annotations

import ctypes
from pathlib import Path
import tkinter as tk
from tkinter import ttk

import numpy as np
from PIL import Image, ImageOps, ImageTk
import sympy as sp
from sympy.parsing.sympy_parser import parse_expr

from solver import LOCAL_DICT, TRANSFORMATIONS, solve, x

WINDOW_BG = "#ffd6ea"
PANEL_BG = "#fff5fa"
ACCENT = "#f95fa9"
ACCENT_DARK = "#211E1E"
TEXT = "#ff69c8"
MUTED = "#4A0923"
ERROR = "#ff1934"
ENTRY_BG = "#fffafd"
HEADER_BG = "#ffc2df"
FONT_FAMILY = "AntykwaTorunskaCond Light"
INTEGRAL_FONT_FAMILY = "Biz UDPMincho"
#BIZ UDPMincho
MATH_FONT_FAMILY = "AntykwaTorunskaCond Medium"

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
        self.root.geometry("1140x620")
        self.root.minsize(1075, 765)
        self.root.configure(bg=WINDOW_BG)
        self.current_graph_expression: str | None = None
        self.header_portraits: list[ImageTk.PhotoImage] = []
        self._panes_initialized = False
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
            font=(FONT_FAMILY, 16, "bold"),
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
        style.configure("Calc.TButton", font=(FONT_FAMILY, 11, "bold"), padding=(8, 6))

    def _build_ui(self) -> None:
        container = ttk.Frame(self.root, style="App.TFrame", padding=20)
        container.pack(fill="both", expand=True)

        header_panel = ttk.Frame(container, style="Header.TFrame", padding=(18, 10))
        header_panel.pack(fill="x", pady=(0, 16))
        header_panel.columnconfigure(1, weight=1)

        integral_frame = tk.Frame(header_panel, bg=HEADER_BG)
        integral_frame.grid(row=0, column=0, sticky="nsw", padx=(0, 14))

        tk.Label(integral_frame, text="∫", bg=HEADER_BG, fg=ACCENT,
            font=(INTEGRAL_FONT_FAMILY, 50, "normal")).pack(side="left")

        tk.Label(
            integral_frame,
            text="dx",
            bg=HEADER_BG,
            fg=ACCENT,
            font=(INTEGRAL_FONT_FAMILY, 15, "bold")
        ).pack(side="left", pady=(0, 0))
        
        header_text = ttk.Frame(header_panel, style="Header.TFrame")
        header_text.grid(row=0, column=1, sticky="nsew")
        header_text.columnconfigure(0, weight=1)
        header_text.rowconfigure(0, weight=1)
        header_text.rowconfigure(3, weight=1)

        ttk.Frame(header_text, style="Header.TFrame").grid(row=0, column=0, sticky="nsew")
        ttk.Label(header_text, text="      Symbolic Calculus Calculator", style="Title.TLabel").grid(
            row=1,
            column=0,
            sticky="w",
        )
        ttk.Label(
            header_text,
            text="  Type your problem below. Made by Runnp and AI. We love Calculus!  ",
            style="Body.TLabel",
        ).grid(row=2, column=0, sticky="w", pady=(4, 0))
        ttk.Frame(header_text, style="Header.TFrame").grid(row=3, column=0, sticky="nsew")

        portraits_frame = tk.Frame(header_panel, bg=HEADER_BG, bd=0, highlightthickness=0)
        portraits_frame.grid(row=0, column=2, sticky="nse", padx=(18, 0))

        for index, filename in enumerate(("Sir_Isaac_Newton.jpg", "Christoph_Bernhard_Leibniz.jpg")):
            portrait = self._load_portrait(filename, (176, 158))
            if portrait is None:
                continue
            self.header_portraits.append(portrait)
            tk.Label(
                portraits_frame,
                image=portrait,
                bg=HEADER_BG,
                bd=0,
                highlightthickness=0,
            ).pack(side="left", padx=(0, 8) if index == 0 else 0)

        content_area = tk.PanedWindow(
            container,
            orient="horizontal",
            bg=WINDOW_BG,
            bd=0,
            sashwidth=10,
            sashrelief="raised",
            showhandle=False,
        )
        content_area.pack(fill="both", expand=True)
        content_area.bind("<Configure>", self._initialize_panes, add="+")

        input_panel = ttk.Frame(content_area, style="Panel.TFrame", padding=16)
        content_area.add(input_panel, minsize=240, stretch="always")

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

        example_text = "Examples:\n" + "\n".join(EXAMPLES)
        ttk.Label(input_panel, text=example_text, style="Examples.TLabel").pack(anchor="w", pady=(8, 0))

        actions = ttk.Frame(input_panel, style="Panel.TFrame")
        actions.pack(fill="x", pady=(12, 0))

        button_row = ttk.Frame(actions, style="Panel.TFrame")
        button_row.pack(anchor="center")

        ttk.Button(button_row, text="Calculate", style="Calc.TButton", command=self.calculate).pack(side="left")
        ttk.Button(button_row, text="Clear", command=self.clear).pack(side="left", padx=(10, 0))

        output_panel = ttk.Frame(content_area, style="Panel.TFrame", padding=16)
        content_area.add(output_panel, minsize=240, stretch="always")

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
            padx=10,
            pady=10,
            state="disabled",
            spacing1=4,
            spacing2=2,
            spacing3=4,
        )
        self.output_text.pack(fill="both", expand=True)

        graph_panel = ttk.Frame(content_area, style="Panel.TFrame", padding=16)
        content_area.add(graph_panel, minsize=240, stretch="always")

        ttk.Label(graph_panel, text="Graph", style="PanelTitle.TLabel").pack(anchor="w")

        self.graph_canvas = tk.Canvas(
            graph_panel,
            bg="#fffafd",
            highlightthickness=1,
            highlightbackground="#f3adc8",
            relief="flat",
        )
        self.graph_canvas.pack(fill="both", expand=True, pady=(10, 0))
        self.graph_canvas.bind("<Configure>", lambda _event: self._refresh_graph())

        ttk.Button(graph_panel, text="Reset Graph", command=self.reset_graph).pack(anchor="center", pady=(8, 0))

        self._set_output(STARTER_TEXT)
        self.reset_graph()
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
        self._plot_function(result["input_expression"])

    def clear(self) -> None:
        self.input_var.set("")
        self.status_label.config(text="Ready", fg=MUTED)
        self._set_output(STARTER_TEXT)
        self.reset_graph()
        self.input_entry.focus_set()

    def _show_message(self, message: str, *, is_error: bool) -> None:
        self.status_label.config(text=message, fg=ERROR if is_error else MUTED)
        self._set_output(message)

    def _set_output(self, content: str) -> None:
        self.output_text.config(state="normal")
        self.output_text.delete("1.0", "end")
        self.output_text.insert("1.0", content)
        self.output_text.config(state="disabled")

    def _initialize_panes(self, event: tk.Event) -> None:
        if self._panes_initialized or event.width <= 0:
            return

        third = max(event.width // 3, 240)
        try:
            event.widget.sash_place(0, third, 1)
            event.widget.sash_place(1, third * 2, 1)
            self._panes_initialized = True
        except tk.TclError:
            pass

    def _load_portrait(self, filename: str, size: tuple[int, int]) -> ImageTk.PhotoImage | None:
        image_path = Path(__file__).resolve().parent.parent / filename
        if not image_path.exists():
            return None

        image = Image.open(image_path).convert("RGB")
        fitted = ImageOps.fit(image, size, method=Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(fitted)

    def _refresh_graph(self) -> None:
        if self.current_graph_expression:
            self._plot_function(self.current_graph_expression)
        else:
            self._draw_graph_placeholder("f(x)", "Run a calculation to plot the input function.", MUTED)

    def reset_graph(self) -> None:
        self.current_graph_expression = None
        self._draw_graph_placeholder("f(x)", "Run a calculation to plot the input function.", MUTED)

    def _draw_graph_placeholder(self, title: str, message: str, message_color: str) -> None:
        self.graph_canvas.delete("all")
        width = max(self.graph_canvas.winfo_width(), 320)
        height = max(self.graph_canvas.winfo_height(), 220)
        self.graph_canvas.create_text(
            width / 2,
            26,
            text=title,
            fill=ACCENT_DARK,
            font=(FONT_FAMILY, 12, "bold"),
        )
        self.graph_canvas.create_text(
            width / 2,
            height / 2,
            text=message,
            fill=message_color,
            font=(FONT_FAMILY, 10),
            width=max(width - 48, 180),
        )

    def _plot_function(self, expression_text: str) -> None:
        self.current_graph_expression = expression_text
        try:
            expression = parse_expr(
                expression_text,
                local_dict=LOCAL_DICT,
                transformations=TRANSFORMATIONS,
                evaluate=True,
            )
            function = sp.lambdify(x, expression, modules=["numpy"])
            x_values = np.linspace(-10, 10, 600)
            y_values = np.asarray(function(x_values), dtype=float)
            finite_mask = np.isfinite(y_values)

            if not finite_mask.any():
                raise ValueError("The function is not real-valued on the sampled interval.")

            y_visible = y_values[finite_mask]
            y_min = float(np.min(y_visible))
            y_max = float(np.max(y_visible))
            if y_min == y_max:
                padding = 1.0 if y_min == 0 else abs(y_min) * 0.2
                y_min -= padding
                y_max += padding

            padding_y = max((y_max - y_min) * 0.08, 1e-6)
            self._draw_plot(
                x_values=x_values[finite_mask],
                y_values=y_visible,
                title=f"y = {sp.sstr(expression)}",
                x_min=float(x_values[0]),
                x_max=float(x_values[-1]),
                y_min=y_min - padding_y,
                y_max=y_max + padding_y,
            )
        except Exception:
            self._draw_graph_placeholder(
                "Graph unavailable",
                "This expression could not be plotted on [-10, 10].",
                ERROR,
            )

    def _draw_plot(
        self,
        *,
        x_values: np.ndarray,
        y_values: np.ndarray,
        title: str,
        x_min: float,
        x_max: float,
        y_min: float,
        y_max: float,
    ) -> None:
        self.graph_canvas.delete("all")
        width = max(self.graph_canvas.winfo_width(), 320)
        height = max(self.graph_canvas.winfo_height(), 220)
        left, top, right, bottom = 44, 42, width - 20, height - 34

        self.graph_canvas.create_text(
            width / 2,
            20,
            text=title,
            fill=ACCENT_DARK,
            font=(FONT_FAMILY, 10, "bold"),
            width=max(width - 40, 180),
        )
        self.graph_canvas.create_rectangle(left, top, right, bottom, outline="#f3adc8", width=1)

        def to_canvas_x(value: float) -> float:
            return left + ((value - x_min) / (x_max - x_min)) * (right - left)

        def to_canvas_y(value: float) -> float:
            return bottom - ((value - y_min) / (y_max - y_min)) * (bottom - top)

        if x_min <= 0 <= x_max:
            axis_x = to_canvas_x(0)
            self.graph_canvas.create_line(axis_x, top, axis_x, bottom, fill="#d98ab0", width=1)
        if y_min <= 0 <= y_max:
            axis_y = to_canvas_y(0)
            self.graph_canvas.create_line(left, axis_y, right, axis_y, fill="#d98ab0", width=1)

        self.graph_canvas.create_text(left, bottom + 14, text=f"{x_min:.0f}", fill=MUTED, font=(FONT_FAMILY, 8))
        self.graph_canvas.create_text(right, bottom + 14, text=f"{x_max:.0f}", fill=MUTED, font=(FONT_FAMILY, 8))
        self.graph_canvas.create_text(left - 20, top, text=f"{y_max:.2g}", fill=MUTED, font=(FONT_FAMILY, 8))
        self.graph_canvas.create_text(left - 20, bottom, text=f"{y_min:.2g}", fill=MUTED, font=(FONT_FAMILY, 8))

        points: list[float] = []
        for x_val, y_val in zip(x_values, y_values):
            points.extend((to_canvas_x(float(x_val)), to_canvas_y(float(y_val))))

        if len(points) >= 4:
            self.graph_canvas.create_line(*points, fill=ACCENT, width=2, smooth=False)


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
