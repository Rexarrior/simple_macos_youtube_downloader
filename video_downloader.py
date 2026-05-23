#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, scrolledtext
import subprocess
import os
import sys
import threading

class VideoDownloader(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Video Downloader")
        self.geometry("700x450")

        frame = ttk.Frame(self, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="URL:").pack(anchor=tk.W)
        self.url_entry = ttk.Entry(frame, width=80)
        self.url_entry.pack(fill=tk.X, pady=(0, 10))

        self.download_btn = ttk.Button(frame, text="Download", command=self.download)
        self.download_btn.pack()

        self.log_area = scrolledtext.ScrolledText(frame, width=80, height=20, state=tk.DISABLED, font=("Courier", 9))
        self.log_area.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

    def log(self, text):
        self.log_area.config(state=tk.NORMAL)
        self.log_area.insert(tk.END, text + "\n")
        self.log_area.see(tk.END)
        self.log_area.config(state=tk.DISABLED)

    def getDownloadsDir(self):
        if sys.platform == "darwin":
            return os.path.expanduser("~/Downloads")
        elif sys.platform == "win32":
            return os.path.join(os.environ["USERPROFILE"], "Downloads")
        else:
            return os.path.expanduser("~/Downloads")

    def run_process(self, cmd):
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in process.stdout:
            self.log(line.rstrip())
        return process.wait()

    def download(self):
        url = self.url_entry.get().strip()
        if not url:
            self.log("[ERROR] Enter URL")
            return

        self.download_btn.config(state=tk.DISABLED)
        self.log_area.config(state=tk.NORMAL)
        self.log_area.delete("1.0", tk.END)
        self.log_area.config(state=tk.DISABLED)

        threading.Thread(target=self._download_task, args=(url,), daemon=True).start()

    def _download_task(self, url):
        output_template = os.path.join(self.getDownloadsDir(), "%(title)s.%(ext)s")
        self.log(f"[DOWNLOAD] Starting...")
        self.log(f"[INFO] Saving to: {self.getDownloadsDir()}")

        ret = self.run_process(["yt-dlp", "-o", output_template, "--merge-output-format", "mp4", url])

        if ret != 0:
            self.log(f"[ERROR] Download failed with code {ret}")
            self.download_btn.config(state=tk.NORMAL)
            return

        mp4_files = [f for f in os.listdir(self.getDownloadsDir()) if f.endswith(".mp4") and not f.startswith("fixed")]
        if mp4_files:
            latest = max([os.path.join(self.getDownloadsDir(), f) for f in mp4_files], key=os.path.getmtime)
            fixed_path = os.path.join(self.getDownloadsDir(), "fixed.mp4")
            self.log(f"[REMUX] Converting to MP4...")
            ret = self.run_process(["ffmpeg", "-i", latest, "-c", "copy", "-y", fixed_path])
            if ret == 0:
                self.log(f"[DONE] Saved: {fixed_path}")
            else:
                self.log(f"[ERROR] Remux failed")
        else:
            self.log("[WARNING] No MP4 file found")

        self.download_btn.config(state=tk.NORMAL)

if __name__ == "__main__":
    app = VideoDownloader()
    app.mainloop()
