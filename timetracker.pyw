# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import messagebox
import datetime
import os
import csv
import time

LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "time_log.csv")

class TimeTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Time Tracker")
        self.root.geometry("340x320")
        self.root.resizable(False, False)
        self.root.configure(bg="#1a1a2e")
        self.root.attributes("-topmost", True)

        self.clocked_in = False
        self.clock_in_time = None
        self.elapsed_seconds = 0
        self.timer_job = None

        self._ensure_log_file()
        self._build_ui()
        self._update_clock()

    def _ensure_log_file(self):
        if not os.path.exists(LOG_FILE):
            with open(LOG_FILE, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Date", "Clock In", "Clock Out", "Hours", "Minutes"])

    def _build_ui(self):
        # Title
        tk.Label(self.root, text="TIME TRACKER", font=("Segoe UI", 16, "bold"),
                 bg="#1a1a2e", fg="#e94560").pack(pady=(18, 2))

        # Live clock
        self.live_clock_var = tk.StringVar()
        tk.Label(self.root, textvariable=self.live_clock_var, font=("Segoe UI", 11),
                 bg="#1a1a2e", fg="#a8a8b3").pack()

        # Status label
        self.status_var = tk.StringVar(value="Status: Clocked OUT")
        tk.Label(self.root, textvariable=self.status_var, font=("Segoe UI", 12, "bold"),
                 bg="#1a1a2e", fg="#f5a623").pack(pady=(14, 2))

        # Elapsed timer
        self.timer_var = tk.StringVar(value="00:00:00")
        tk.Label(self.root, textvariable=self.timer_var, font=("Courier New", 28, "bold"),
                 bg="#1a1a2e", fg="#00d4ff").pack(pady=4)

        # Clock In button
        self.in_btn = tk.Button(
            self.root, text="CLOCK IN", font=("Segoe UI", 13, "bold"),
            bg="#0f3460", fg="white", activebackground="#16213e",
            width=12, height=1, relief="flat", cursor="hand2",
            command=self.clock_in
        )
        self.in_btn.pack(pady=(12, 4))

        # Clock Out button
        self.out_btn = tk.Button(
            self.root, text="CLOCK OUT", font=("Segoe UI", 13, "bold"),
            bg="#e94560", fg="white", activebackground="#c73652",
            width=12, height=1, relief="flat", cursor="hand2",
            state="disabled", command=self.clock_out
        )
        self.out_btn.pack(pady=4)

        # View log button
        tk.Button(
            self.root, text="View Time Log", font=("Segoe UI", 9),
            bg="#16213e", fg="#a8a8b3", activebackground="#0f3460",
            relief="flat", cursor="hand2", command=self.view_log
        ).pack(pady=(10, 0))

    def _update_clock(self):
        now = datetime.datetime.now().strftime("%A  %I:%M:%S %p")
        self.live_clock_var.set(now)
        self.root.after(1000, self._update_clock)

    def _tick(self):
        if self.clocked_in and self.clock_in_time:
            delta = datetime.datetime.now() - self.clock_in_time
            total = int(delta.total_seconds())
            h = total // 3600
            m = (total % 3600) // 60
            s = total % 60
            self.timer_var.set(f"{h:02d}:{m:02d}:{s:02d}")
            self.timer_job = self.root.after(1000, self._tick)

    def clock_in(self):
        self.clock_in_time = datetime.datetime.now()
        self.clocked_in = True
        self.status_var.set("Status: CLOCKED IN  [ON]")
        self.in_btn.config(state="disabled", bg="#333366")
        self.out_btn.config(state="normal", bg="#e94560")
        self.timer_var.set("00:00:00")
        self._tick()

    def clock_out(self):
        if not self.clocked_in or not self.clock_in_time:
            return

        clock_out_time = datetime.datetime.now()
        delta = clock_out_time - self.clock_in_time
        total_minutes = int(delta.total_seconds() // 60)
        hours = total_minutes // 60
        minutes = total_minutes % 60

        if self.timer_job:
            self.root.after_cancel(self.timer_job)
            self.timer_job = None

        # Save to log
        with open(LOG_FILE, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                self.clock_in_time.strftime("%Y-%m-%d"),
                self.clock_in_time.strftime("%I:%M:%S %p"),
                clock_out_time.strftime("%I:%M:%S %p"),
                hours,
                minutes
            ])

        self.clocked_in = False
        self.status_var.set("Status: Clocked OUT")
        self.in_btn.config(state="normal", bg="#0f3460")
        self.out_btn.config(state="disabled", bg="#555555")

        messagebox.showinfo(
            "Session Saved",
            f"Session logged!\n\n"
            f"In:   {self.clock_in_time.strftime('%I:%M %p')}\n"
            f"Out:  {clock_out_time.strftime('%I:%M %p')}\n"
            f"Time: {hours}h {minutes}m"
        )

    def view_log(self):
        if not os.path.exists(LOG_FILE):
            messagebox.showinfo("No Log", "No time entries logged yet.\nClock in and out to create your first entry.")
            return
        import subprocess
        try:
            os.startfile(LOG_FILE)
        except Exception:
            # Fallback: open folder with file selected in Explorer
            subprocess.Popen(f'explorer /select,"{LOG_FILE}"')


if __name__ == "__main__":
    root = tk.Tk()
    app = TimeTrackerApp(root)
    root.mainloop()
