#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import os
import sys

class VideoDownloader(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Video Downloader")
        self.geometry("600x150")
        self.resizable(False, False)

        frame = ttk.Frame(self, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="URL:").pack(anchor=tk.W)
        self.url_entry = ttk.Entry(frame, width=70)
        self.url_entry.pack(fill=tk.X, pady=(0, 10))

        self.download_btn = ttk.Button(frame, text="Download", command=self.download)
        self.download_btn.pack()

        self.progress = ttk.Label(frame, text="")
        self.progress.pack(pady=(10, 0))

        self.progress_bar = ttk.Progressbar(frame, mode="indeterminate", length=400)

    def getDownloadsDir(self):
        if sys.platform == "darwin":
            return os.path.expanduser("~/Downloads")
        elif sys.platform == "win32":
            return os.path.join(os.environ["USERPROFILE"], "Downloads")
        else:
            return os.path.expanduser("~/Downloads")

    def download(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Warning", "Enter URL")
            return

        self.download_btn.config(state=tk.DISABLED)
        self.progress.config(text="Downloading...")
        self.progress_bar.pack(pady=(5, 0))
        self.progress_bar.start()
        self.update()

        output_template = os.path.join(self.getDownloadsDir(), "%(title)s.%(ext)s")

        try:
            result = subprocess.run(
                ["yt-dlp", "-o", output_template, "--merge-output-format", "mp4", url],
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                messagebox.showerror("Error", result.stderr[-500:])
                return

            self.progress.config(text="Remuxing with ffmpeg...")
            self.update()

            mp4_files = [f for f in os.listdir(self.getDownloadsDir()) if f.endswith(".mp4") and not f.startswith("fixed")]
            if mp4_files:
                latest = max([os.path.join(self.getDownloadsDir(), f) for f in mp4_files], key=os.path.getmtime)
                fixed_path = os.path.join(self.getDownloadsDir(), "fixed.mp4")
                subprocess.run(["ffmpeg", "-i", latest, "-c", "copy", "-y", fixed_path], capture_output=True)

            self.progress_bar.stop()
            self.progress_bar.pack_forget()
            self.progress.config(text="Done!")
            messagebox.showinfo("Success", f"Saved to {self.getDownloadsDir()}")

        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            self.download_btn.config(state=tk.NORMAL)
            self.progress_bar.stop()
            self.progress_bar.pack_forget()

if __name__ == "__main__":
    app = VideoDownloader()
    app.mainloop()
