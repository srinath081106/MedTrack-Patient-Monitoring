"""
MedTrack - Patient Health Monitoring System
Educational desktop application using Python Tkinter and SQLite.
This software is for learning only and is not a medical diagnostic device.
"""

import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

DB_NAME = "medtrack.db"

# Example educational ranges only; not suitable for clinical decision-making.
HR_MIN, HR_MAX = 60, 100
SPO2_MIN = 95
TEMP_MIN, TEMP_MAX = 36.1, 37.8


class MedTrackApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MedTrack | Patient Health Monitoring System")
        self.root.geometry("1050x700")
        self.root.minsize(900, 600)
        self.selected_patient_id = None

        self.setup_database()
        self.setup_styles()
        self.build_ui()
        self.refresh_patients()

    def setup_database(self):
        with sqlite3.connect(DB_NAME) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS patients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_code TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    age INTEGER NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS readings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_id INTEGER NOT NULL,
                    heart_rate REAL NOT NULL,
                    spo2 REAL NOT NULL,
                    temperature REAL NOT NULL,
                    notes TEXT DEFAULT '',
                    recorded_at TEXT NOT NULL,
                    FOREIGN KEY(patient_id) REFERENCES patients(id)
                )
            """)

    def setup_styles(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Title.TLabel", font=("Segoe UI", 18, "bold"))
        style.configure("Heading.TLabel", font=("Segoe UI", 11, "bold"))
        style.configure("Treeview", rowheight=26, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"))

    def build_ui(self):
        header = ttk.Frame(self.root, padding=(18, 14))
        header.pack(fill="x")
        ttk.Label(header, text="MedTrack", style="Title.TLabel").pack(side="left")
        ttk.Label(
            header,
            text="Patient Health Monitoring System  |  Educational prototype",
        ).pack(side="left", padx=(16, 0), pady=(7, 0))

        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=16, pady=(0, 12))

        self.patient_tab = ttk.Frame(notebook, padding=14)
        self.reading_tab = ttk.Frame(notebook, padding=14)
        self.history_tab = ttk.Frame(notebook, padding=14)
        notebook.add(self.patient_tab, text="Patients")
        notebook.add(self.reading_tab, text="Record Vital Signs")
        notebook.add(self.history_tab, text="Reading History")

        self.build_patient_tab()
        self.build_reading_tab()
        self.build_history_tab()

        footer = ttk.Label(
            self.root,
            text="For education only — alerts are not diagnoses. Do not use for real clinical decisions.",
            foreground="#8a3b12",
            padding=(16, 0, 16, 10),
        )
        footer.pack(anchor="w")

    def build_patient_tab(self):
        form = ttk.LabelFrame(self.patient_tab, text="Register patient", padding=12)
        form.pack(fill="x")
        self.code_var = tk.StringVar()
        self.name_var = tk.StringVar()
        self.age_var = tk.StringVar()
        self.search_var = tk.StringVar()

        fields = [
            ("Patient code", self.code_var, 18),
            ("Full name", self.name_var, 25),
            ("Age", self.age_var, 8),
        ]
        for col, (label, var, width) in enumerate(fields):
            ttk.Label(form, text=label).grid(row=0, column=col, sticky="w", padx=5)
            ttk.Entry(form, textvariable=var, width=width).grid(
                row=1, column=col, sticky="w", padx=5, pady=(3, 7)
            )
        ttk.Button(form, text="Add Patient", style="Accent.TButton",
                   command=self.add_patient).grid(row=1, column=3, padx=10)

        search_frame = ttk.Frame(self.patient_tab)
        search_frame.pack(fill="x", pady=(14, 6))
        ttk.Label(search_frame, text="Search by code or name:").pack(side="left")
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side="left", padx=8)
        search_entry.bind("<KeyRelease>", lambda _event: self.refresh_patients())
        ttk.Button(search_frame, text="Clear", command=self.clear_search).pack(side="left")

        columns = ("id", "code", "name", "age", "created")
        self.patient_tree = ttk.Treeview(
            self.patient_tab, columns=columns, show="headings", selectmode="browse"
        )
        for key, heading, width in [
            ("id", "DB ID", 70), ("code", "Patient Code", 160),
            ("name", "Full Name", 260), ("age", "Age", 80),
            ("created", "Registered At", 190),
        ]:
            self.patient_tree.heading(key, text=heading)
            self.patient_tree.column(key, width=width, anchor="w")
        self.patient_tree.pack(fill="both", expand=True)
        self.patient_tree.bind("<<TreeviewSelect>>", self.on_patient_select)

        hint = ttk.Label(
            self.patient_tab,
            text="Select a patient in the table, then open Record Vital Signs to add measurements.",
            foreground="#555555",
        )
        hint.pack(anchor="w", pady=(8, 0))

    def build_reading_tab(self):
        ttk.Label(self.reading_tab, text="Record vital signs", style="Heading.TLabel").pack(anchor="w")
        self.selected_label = ttk.Label(self.reading_tab, text="Selected patient: none")
        self.selected_label.pack(anchor="w", pady=(5, 14))

        form = ttk.LabelFrame(self.reading_tab, text="Measurement details", padding=16)
        form.pack(fill="x", anchor="n")
        self.hr_var = tk.StringVar()
        self.spo2_var = tk.StringVar()
        self.temp_var = tk.StringVar()
        self.notes_var = tk.StringVar()

        for col, (label, var, unit) in enumerate([
            ("Heart rate", self.hr_var, "bpm"),
            ("SpO₂", self.spo2_var, "%"),
            ("Temperature", self.temp_var, "°C"),
        ]):
            ttk.Label(form, text=f"{label} ({unit})").grid(row=0, column=col, sticky="w", padx=8)
            ttk.Entry(form, textvariable=var, width=18).grid(
                row=1, column=col, sticky="w", padx=8, pady=(4, 12)
            )

        ttk.Label(form, text="Notes (optional)").grid(row=2, column=0, sticky="w", padx=8)
        ttk.Entry(form, textvariable=self.notes_var, width=65).grid(
            row=3, column=0, columnspan=3, sticky="w", padx=8, pady=(4, 12)
        )
        ttk.Button(form, text="Save Reading", style="Accent.TButton",
                   command=self.save_reading).grid(row=4, column=0, sticky="w", padx=8)

        ranges = (
            "Educational example ranges only:\n"
            f"• Heart rate: {HR_MIN}–{HR_MAX} bpm\n"
            f"• SpO₂: at least {SPO2_MIN}%\n"
            f"• Temperature: {TEMP_MIN}–{TEMP_MAX} °C\n\n"
            "These fixed example thresholds are not personalized and must not be used "
            "to diagnose or treat a person."
        )
        ttk.Label(self.reading_tab, text=ranges, justify="left").pack(anchor="w", pady=18)

    def build_history_tab(self):
        top = ttk.Frame(self.history_tab)
        top.pack(fill="x", pady=(0, 8))
        ttk.Label(top, text="Saved measurements", style="Heading.TLabel").pack(side="left")
        ttk.Button(top, text="Refresh history", command=self.refresh_history).pack(side="right")

        columns = ("date", "code", "name", "hr", "spo2", "temp", "status", "notes")
        self.history_tree = ttk.Treeview(
            self.history_tab, columns=columns, show="headings", selectmode="browse"
        )
        specs = [
            ("date", "Recorded At", 150), ("code", "Patient Code", 105),
            ("name", "Patient Name", 150), ("hr", "HR (bpm)", 75),
            ("spo2", "SpO₂ (%)", 75), ("temp", "Temp (°C)", 85),
            ("status", "Example Flag", 130), ("notes", "Notes", 170),
        ]
        for key, heading, width in specs:
            self.history_tree.heading(key, text=heading)
            self.history_tree.column(key, width=width, anchor="w")
        self.history_tree.pack(fill="both", expand=True)
        self.refresh_history()

    def add_patient(self):
        code = self.code_var.get().strip()
        name = self.name_var.get().strip()
        age_text = self.age_var.get().strip()

        if not code or not name or not age_text:
            messagebox.showwarning("Missing information", "Enter patient code, full name, and age.")
            return
        try:
            age = int(age_text)
            if age < 0 or age > 130:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid age", "Age must be a whole number from 0 to 130.")
            return

        try:
            with sqlite3.connect(DB_NAME) as conn:
                conn.execute(
                    "INSERT INTO patients (patient_code, name, age, created_at) VALUES (?, ?, ?, ?)",
                    (code, name, age, datetime.now().strftime("%Y-%m-%d %H:%M")),
                )
        except sqlite3.IntegrityError:
            messagebox.showerror("Duplicate code", "That patient code already exists. Choose another.")
            return

        self.code_var.set("")
        self.name_var.set("")
        self.age_var.set("")
        self.refresh_patients()
        messagebox.showinfo("Saved", f"Patient {name} was added.")

    def refresh_patients(self):
        if not hasattr(self, "patient_tree"):
            return
        query = self.search_var.get().strip() if hasattr(self, "search_var") else ""
        for item in self.patient_tree.get_children():
            self.patient_tree.delete(item)
        with sqlite3.connect(DB_NAME) as conn:
            if query:
                rows = conn.execute(
                    """SELECT id, patient_code, name, age, created_at FROM patients
                       WHERE patient_code LIKE ? OR name LIKE ? ORDER BY id DESC""",
                    (f"%{query}%", f"%{query}%"),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT id, patient_code, name, age, created_at FROM patients ORDER BY id DESC"
                ).fetchall()
        for row in rows:
            self.patient_tree.insert("", "end", values=row)

    def clear_search(self):
        self.search_var.set("")
        self.refresh_patients()

    def on_patient_select(self, _event=None):
        selected = self.patient_tree.selection()
        if not selected:
            return
        values = self.patient_tree.item(selected[0], "values")
        self.selected_patient_id = int(values[0])
        self.selected_label.config(text=f"Selected patient: {values[2]} ({values[1]})")

    def save_reading(self):
        if self.selected_patient_id is None:
            messagebox.showwarning(
                "Select a patient", "Go to Patients and select a patient before recording readings."
            )
            return
        try:
            hr = float(self.hr_var.get().strip())
            spo2 = float(self.spo2_var.get().strip())
            temp = float(self.temp_var.get().strip())
            if not (0 < hr <= 300 and 0 <= spo2 <= 100 and 20 <= temp <= 50):
                raise ValueError
        except ValueError:
            messagebox.showerror(
                "Invalid measurements",
                "Enter numbers within these broad data-entry limits: HR 0–300, SpO₂ 0–100, temperature 20–50 °C.",
            )
            return

        with sqlite3.connect(DB_NAME) as conn:
            conn.execute(
                """INSERT INTO readings
                   (patient_id, heart_rate, spo2, temperature, notes, recorded_at)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    self.selected_patient_id, hr, spo2, temp,
                    self.notes_var.get().strip(),
                    datetime.now().strftime("%Y-%m-%d %H:%M"),
                ),
            )

        flags = self.get_flags(hr, spo2, temp)
        self.hr_var.set("")
        self.spo2_var.set("")
        self.temp_var.set("")
        self.notes_var.set("")
        self.refresh_history()
        if flags:
            messagebox.showwarning(
                "Example range flag",
                "This reading is outside one or more example ranges:\n\n"
                + "\n".join(f"• {flag}" for flag in flags)
                + "\n\nThis is not a diagnosis. Check measurement quality and consult a qualified clinician when appropriate.",
            )
        else:
            messagebox.showinfo(
                "Reading saved",
                "Measurement saved. No example range was flagged; this does not mean the person is medically well.",
            )

    @staticmethod
    def get_flags(hr, spo2, temp):
        flags = []
        if not HR_MIN <= hr <= HR_MAX:
            flags.append(f"Heart rate {hr:g} bpm is outside {HR_MIN}–{HR_MAX} bpm.")
        if spo2 < SPO2_MIN:
            flags.append(f"SpO₂ {spo2:g}% is below the example threshold of {SPO2_MIN}%.")
        if not TEMP_MIN <= temp <= TEMP_MAX:
            flags.append(f"Temperature {temp:g} °C is outside {TEMP_MIN}–{TEMP_MAX} °C.")
        return flags

    def refresh_history(self):
        if not hasattr(self, "history_tree"):
            return
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        with sqlite3.connect(DB_NAME) as conn:
            rows = conn.execute("""
                SELECT r.recorded_at, p.patient_code, p.name, r.heart_rate,
                       r.spo2, r.temperature, r.notes
                FROM readings r JOIN patients p ON p.id = r.patient_id
                ORDER BY r.id DESC
            """).fetchall()
        for date, code, name, hr, spo2, temp, notes in rows:
            flags = self.get_flags(float(hr), float(spo2), float(temp))
            status = "Review example flag" if flags else "No example flag"
            self.history_tree.insert(
                "", "end",
                values=(date, code, name, f"{hr:g}", f"{spo2:g}", f"{temp:g}", status, notes),
            )


def main():
    root = tk.Tk()
    MedTrackApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
