"""
Personal Finance & Budget Tracker  -  Tkinter front-end
Run:  python finance_tracker.py
Data is saved automatically to finance_data.json (same folder).
"""
import csv
import json
import os
import tkinter as tk
from datetime import date, datetime
from tkinter import filedialog, messagebox, ttk

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "finance_data.json")
CURRENCY = "₹"

CATEGORIES = {
    "Income": ["Salary", "Freelance", "Gift", "Other Income"],
    "Expense": ["Food", "Rent", "Transport", "Shopping", "Bills", "Health", "Entertainment", "Other"],
}
DEFAULT_BUDGETS = {"Food": 8000, "Rent": 15000, "Transport": 3000, "Shopping": 5000,
                   "Bills": 4000, "Health": 2000, "Entertainment": 3000, "Other": 2000}

# Colour palette
BG = "#f4f6fb"
CARD = "#ffffff"
PRIMARY = "#4f46e5"
GREEN = "#16a34a"
RED = "#dc2626"
TEXT = "#1f2937"
MUTED = "#6b7280"
BAR_COLORS = ["#4f46e5", "#0ea5e9", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899", "#14b8a6"]


def money(value):
    return f"{CURRENCY}{value:,.2f}"


class FinanceApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Personal Finance & Budget Tracker")
        self.geometry("1000x650")
        self.minsize(900, 600)
        self.configure(bg=BG)

        self.transactions, self.budgets = self.load_data()
        self.budget_rows = {}

        self.setup_styles()
        self.build_header()
        self.build_tabs()
        self.refresh_all()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    # ------------------------------------------------------------------ data
    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return data.get("transactions", []), data.get("budgets", dict(DEFAULT_BUDGETS))
            except (json.JSONDecodeError, OSError):
                pass
        return [], dict(DEFAULT_BUDGETS)

    def save_data(self):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump({"transactions": self.transactions, "budgets": self.budgets}, f, indent=2)
        except OSError as e:
            messagebox.showerror("Save error", str(e))

    def on_close(self):
        self.save_data()
        self.destroy()

    # ---------------------------------------------------------------- styles
    def setup_styles(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure("TNotebook", background=BG, borderwidth=0)
        s.configure("TNotebook.Tab", padding=(20, 8), font=("Segoe UI", 10, "bold"))
        s.map("TNotebook.Tab", background=[("selected", CARD)], foreground=[("selected", PRIMARY)])
        s.configure("TFrame", background=BG)
        s.configure("Card.TFrame", background=CARD)
        s.configure("TLabel", background=BG, foreground=TEXT, font=("Segoe UI", 10))
        s.configure("Card.TLabel", background=CARD)
        s.configure("Muted.TLabel", background=CARD, foreground=MUTED, font=("Segoe UI", 9))
        s.configure("Title.TLabel", background=CARD, font=("Segoe UI", 12, "bold"))
        s.configure("TRadiobutton", background=CARD, font=("Segoe UI", 10))
        s.configure("Accent.TButton", background=PRIMARY, foreground="white",
                    font=("Segoe UI", 10, "bold"), padding=8, borderwidth=0)
        s.map("Accent.TButton", background=[("active", "#4338ca")])
        s.configure("Danger.TButton", background=RED, foreground="white",
                    font=("Segoe UI", 10), padding=6, borderwidth=0)
        s.map("Danger.TButton", background=[("active", "#b91c1c")])
        s.configure("Treeview", rowheight=28, font=("Segoe UI", 10), background=CARD, fieldbackground=CARD)
        s.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background="#e5e7eb")
        s.configure("Ok.Horizontal.TProgressbar", troughcolor="#e5e7eb", background=GREEN, thickness=14)
        s.configure("Over.Horizontal.TProgressbar", troughcolor="#e5e7eb", background=RED, thickness=14)

    # ---------------------------------------------------------------- layout
    def build_header(self):
        header = tk.Frame(self, bg=PRIMARY, height=60)
        header.pack(fill="x")
        tk.Label(header, text="💰  Personal Finance & Budget Tracker", bg=PRIMARY, fg="white",
                 font=("Segoe UI", 16, "bold")).pack(side="left", padx=20, pady=12)
        tk.Label(header, text=date.today().strftime("%A, %d %B %Y"), bg=PRIMARY, fg="#c7d2fe",
                 font=("Segoe UI", 10)).pack(side="right", padx=20)

    def build_tabs(self):
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=15, pady=15)
        self.tab_dash = ttk.Frame(nb)
        self.tab_tx = ttk.Frame(nb)
        self.tab_budget = ttk.Frame(nb)
        nb.add(self.tab_dash, text="  Dashboard  ")
        nb.add(self.tab_tx, text="  Transactions  ")
        nb.add(self.tab_budget, text="  Budgets  ")
        self.build_dashboard()
        self.build_transactions()
        self.build_budgets()

    # ------------------------------------------------------------- dashboard
    def build_dashboard(self):
        cards = ttk.Frame(self.tab_dash)
        cards.pack(fill="x", pady=(10, 15))
        self.card_vars = {}
        for i, (key, title, color) in enumerate([
            ("income", "Income (this month)", GREEN),
            ("expense", "Expenses (this month)", RED),
            ("savings", "Savings (this month)", PRIMARY),
            ("balance", "Overall Balance", TEXT),
        ]):
            cards.columnconfigure(i, weight=1, uniform="c")
            f = tk.Frame(cards, bg=CARD, highlightbackground="#e5e7eb", highlightthickness=1)
            f.grid(row=0, column=i, padx=6, sticky="nsew")
            tk.Frame(f, bg=color, height=4).pack(fill="x")
            tk.Label(f, text=title, bg=CARD, fg=MUTED, font=("Segoe UI", 9)).pack(anchor="w", padx=14, pady=(10, 0))
            var = tk.StringVar(value=money(0))
            tk.Label(f, textvariable=var, bg=CARD, fg=color, font=("Segoe UI", 18, "bold")).pack(
                anchor="w", padx=14, pady=(2, 14))
            self.card_vars[key] = var

        chart_box = ttk.Frame(self.tab_dash, style="Card.TFrame")
        chart_box.pack(fill="both", expand=True, padx=6)
        ttk.Label(chart_box, text="Spending by category (this month)", style="Title.TLabel").pack(
            anchor="w", padx=15, pady=(12, 0))
        self.canvas = tk.Canvas(chart_box, bg=CARD, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=10, pady=10)
        self.canvas.bind("<Configure>", lambda e: self.draw_chart())

    def draw_chart(self):
        c = self.canvas
        c.delete("all")
        w, h = c.winfo_width(), c.winfo_height()
        spent = {k: v for k, v in self.month_spending().items() if v > 0}
        if not spent:
            c.create_text(w / 2, h / 2, text="No expenses recorded this month yet.",
                          fill=MUTED, font=("Segoe UI", 11))
            return
        items = sorted(spent.items(), key=lambda kv: kv[1], reverse=True)
        max_v = max(v for _, v in items)
        left, right, top, bottom = 20, 20, 30, 40
        slot = (w - left - right) / len(items)
        bar_w = min(70, slot * 0.6)
        base_y = h - bottom
        c.create_line(left, base_y, w - right, base_y, fill="#d1d5db")
        for i, (cat, val) in enumerate(items):
            x = left + slot * i + (slot - bar_w) / 2
            bar_h = (val / max_v) * (base_y - top - 20)
            c.create_rectangle(x, base_y - bar_h, x + bar_w, base_y,
                               fill=BAR_COLORS[i % len(BAR_COLORS)], outline="")
            c.create_text(x + bar_w / 2, base_y - bar_h - 10, text=money(val),
                          fill=TEXT, font=("Segoe UI", 9, "bold"))
            c.create_text(x + bar_w / 2, base_y + 16, text=cat, fill=MUTED, font=("Segoe UI", 9))

    # ---------------------------------------------------------- transactions
    def build_transactions(self):
        self.tab_tx.columnconfigure(1, weight=1)
        self.tab_tx.rowconfigure(0, weight=1)

        # ---- form (left)
        form = ttk.Frame(self.tab_tx, style="Card.TFrame")
        form.grid(row=0, column=0, sticky="ns", padx=(6, 10), pady=10)
        ttk.Label(form, text="Add Transaction", style="Title.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w", padx=15, pady=(15, 10))

        self.type_var = tk.StringVar(value="Expense")
        radios = ttk.Frame(form, style="Card.TFrame")
        radios.grid(row=1, column=0, columnspan=2, sticky="w", padx=15)
        for t in ("Expense", "Income"):
            ttk.Radiobutton(radios, text=t, value=t, variable=self.type_var,
                            command=self.update_category_list).pack(side="left", padx=(0, 15))

        self.date_var = tk.StringVar(value=date.today().isoformat())
        self.cat_var = tk.StringVar()
        self.amount_var = tk.StringVar()
        self.note_var = tk.StringVar()

        ttk.Label(form, text="Date (YYYY-MM-DD)", style="Muted.TLabel").grid(row=2, column=0, sticky="w", padx=15, pady=(12, 0))
        ttk.Entry(form, textvariable=self.date_var, width=26).grid(row=3, column=0, columnspan=2, padx=15, sticky="we")
        ttk.Label(form, text="Category", style="Muted.TLabel").grid(row=4, column=0, sticky="w", padx=15, pady=(10, 0))
        self.cat_combo = ttk.Combobox(form, textvariable=self.cat_var, state="readonly", width=24)
        self.cat_combo.grid(row=5, column=0, columnspan=2, padx=15, sticky="we")
        ttk.Label(form, text=f"Amount ({CURRENCY})", style="Muted.TLabel").grid(row=6, column=0, sticky="w", padx=15, pady=(10, 0))
        ttk.Entry(form, textvariable=self.amount_var, width=26).grid(row=7, column=0, columnspan=2, padx=15, sticky="we")
        ttk.Label(form, text="Note (optional)", style="Muted.TLabel").grid(row=8, column=0, sticky="w", padx=15, pady=(10, 0))
        ttk.Entry(form, textvariable=self.note_var, width=26).grid(row=9, column=0, columnspan=2, padx=15, sticky="we")

        ttk.Button(form, text="+ Add", style="Accent.TButton", command=self.add_transaction).grid(
            row=10, column=0, columnspan=2, padx=15, pady=(18, 15), sticky="we")
        self.update_category_list()

        # ---- table (right)
        right = ttk.Frame(self.tab_tx, style="Card.TFrame")
        right.grid(row=0, column=1, sticky="nsew", pady=10, padx=(0, 6))
        right.columnconfigure(0, weight=1)
        right.rowconfigure(1, weight=1)

        bar = ttk.Frame(right, style="Card.TFrame")
        bar.grid(row=0, column=0, columnspan=2, sticky="we", padx=12, pady=12)
        ttk.Label(bar, text="History", style="Title.TLabel").pack(side="left")
        self.filter_var = tk.StringVar(value="All")
        flt = ttk.Combobox(bar, textvariable=self.filter_var, state="readonly", width=10,
                           values=["All", "Income", "Expense"])
        flt.pack(side="left", padx=15)
        flt.bind("<<ComboboxSelected>>", lambda e: self.refresh_table())
        ttk.Button(bar, text="Export CSV", command=self.export_csv).pack(side="right")
        ttk.Button(bar, text="Delete Selected", style="Danger.TButton",
                   command=self.delete_selected).pack(side="right", padx=8)

        cols = ("date", "type", "category", "amount", "note")
        self.tree = ttk.Treeview(right, columns=cols, show="headings", selectmode="extended")
        for col, text, width, anchor in [("date", "Date", 100, "w"), ("type", "Type", 80, "w"),
                                         ("category", "Category", 120, "w"), ("amount", "Amount", 110, "e"),
                                         ("note", "Note", 220, "w")]:
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width, anchor=anchor)
        self.tree.tag_configure("income", foreground=GREEN)
        self.tree.tag_configure("expense", foreground=RED)
        self.tree.grid(row=1, column=0, sticky="nsew", padx=(12, 0), pady=(0, 12))
        sb = ttk.Scrollbar(right, orient="vertical", command=self.tree.yview)
        sb.grid(row=1, column=1, sticky="ns", padx=(0, 12), pady=(0, 12))
        self.tree.configure(yscrollcommand=sb.set)

    def update_category_list(self):
        cats = CATEGORIES[self.type_var.get()]
        self.cat_combo["values"] = cats
        self.cat_var.set(cats[0])

    def add_transaction(self):
        try:
            d = datetime.strptime(self.date_var.get().strip(), "%Y-%m-%d").date().isoformat()
        except ValueError:
            messagebox.showwarning("Invalid date", "Please enter the date as YYYY-MM-DD.")
            return
        try:
            amount = float(self.amount_var.get().replace(",", ""))
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Invalid amount", "Please enter a positive number for the amount.")
            return
        self.transactions.append({"date": d, "type": self.type_var.get(), "category": self.cat_var.get(),
                                  "amount": amount, "note": self.note_var.get().strip()})
        self.amount_var.set("")
        self.note_var.set("")
        self.save_data()
        self.refresh_all()

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Delete", "Select one or more rows first.")
            return
        if not messagebox.askyesno("Confirm", f"Delete {len(selected)} transaction(s)?"):
            return
        for idx in sorted((int(i) for i in selected), reverse=True):
            del self.transactions[idx]
        self.save_data()
        self.refresh_all()

    def export_csv(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")],
                                            initialfile="transactions.csv")
        if not path:
            return
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["date", "type", "category", "amount", "note"])
            writer.writeheader()
            writer.writerows(self.transactions)
        messagebox.showinfo("Exported", f"Saved to:\n{path}")

    def refresh_table(self):
        self.tree.delete(*self.tree.get_children())
        flt = self.filter_var.get()
        order = sorted(range(len(self.transactions)), key=lambda i: self.transactions[i]["date"], reverse=True)
        for i in order:
            t = self.transactions[i]
            if flt != "All" and t["type"] != flt:
                continue
            sign = "+" if t["type"] == "Income" else "-"
            self.tree.insert("", "end", iid=str(i), tags=(t["type"].lower(),),
                             values=(t["date"], t["type"], t["category"], f"{sign}{money(t['amount'])}", t["note"]))

    # --------------------------------------------------------------- budgets
    def build_budgets(self):
        box = ttk.Frame(self.tab_budget, style="Card.TFrame")
        box.pack(fill="both", expand=True, padx=6, pady=10)
        ttk.Label(box, text="Monthly Budgets", style="Title.TLabel").grid(
            row=0, column=0, columnspan=4, sticky="w", padx=20, pady=(15, 0))
        ttk.Label(box, text="Set a limit per category. Bars turn red when you go over budget.",
                  style="Muted.TLabel").grid(row=1, column=0, columnspan=4, sticky="w", padx=20, pady=(0, 10))
        box.columnconfigure(2, weight=1)

        for r, cat in enumerate(CATEGORIES["Expense"], start=2):
            ttk.Label(box, text=cat, style="Card.TLabel", width=14).grid(row=r, column=0, padx=(20, 5), pady=8, sticky="w")
            var = tk.StringVar(value=str(self.budgets.get(cat, 0)))
            ttk.Entry(box, textvariable=var, width=10).grid(row=r, column=1, padx=5)
            bar = ttk.Progressbar(box, maximum=100, style="Ok.Horizontal.TProgressbar")
            bar.grid(row=r, column=2, sticky="we", padx=10)
            lbl = ttk.Label(box, text="", style="Card.TLabel", width=26)
            lbl.grid(row=r, column=3, padx=(5, 20), sticky="w")
            self.budget_rows[cat] = (var, bar, lbl)

        ttk.Button(box, text="Save Budgets", style="Accent.TButton", command=self.save_budgets).grid(
            row=len(CATEGORIES["Expense"]) + 2, column=0, columnspan=2, padx=20, pady=20, sticky="w")

    def save_budgets(self):
        try:
            for cat, (var, _, _) in self.budget_rows.items():
                value = float(var.get().replace(",", ""))
                if value < 0:
                    raise ValueError
                self.budgets[cat] = value
        except ValueError:
            messagebox.showwarning("Invalid budget", "Budget limits must be non-negative numbers.")
            return
        self.save_data()
        self.refresh_all()
        messagebox.showinfo("Saved", "Budgets updated.")

    def refresh_budgets(self):
        spent = self.month_spending()
        for cat, (_, bar, lbl) in self.budget_rows.items():
            limit = self.budgets.get(cat, 0)
            used = spent.get(cat, 0)
            pct = (used / limit * 100) if limit > 0 else (100 if used > 0 else 0)
            bar["value"] = min(pct, 100)
            bar.configure(style="Over.Horizontal.TProgressbar" if used > limit else "Ok.Horizontal.TProgressbar")
            lbl.configure(text=f"{money(used)} / {money(limit)}", foreground=RED if used > limit else TEXT)

    # ---------------------------------------------------------------- shared
    def month_spending(self):
        prefix = date.today().strftime("%Y-%m")
        spent = {}
        for t in self.transactions:
            if t["type"] == "Expense" and t["date"].startswith(prefix):
                spent[t["category"]] = spent.get(t["category"], 0) + t["amount"]
        return spent

    def refresh_all(self):
        prefix = date.today().strftime("%Y-%m")
        m_income = sum(t["amount"] for t in self.transactions if t["type"] == "Income" and t["date"].startswith(prefix))
        m_expense = sum(t["amount"] for t in self.transactions if t["type"] == "Expense" and t["date"].startswith(prefix))
        total = sum(t["amount"] if t["type"] == "Income" else -t["amount"] for t in self.transactions)
        self.card_vars["income"].set(money(m_income))
        self.card_vars["expense"].set(money(m_expense))
        self.card_vars["savings"].set(money(m_income - m_expense))
        self.card_vars["balance"].set(money(total))
        self.refresh_table()
        self.refresh_budgets()
        self.draw_chart()


if __name__ == "__main__":
    FinanceApp().mainloop()
