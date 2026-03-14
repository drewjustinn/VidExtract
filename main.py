"""
main.py
───────
Entry point — just run:  python main.py
"""

import sys
import threading
import subprocess
import multiprocessing

# CRITICAL — must be first line in if __name__ block for PyInstaller on Windows
if sys.platform == "win32":
    multiprocessing.freeze_support()

from ui.main_window import MainWindow


def auto_update_ytdlp(callback):
    try:
        import urllib.request
        import json
        import os

        # Get latest yt-dlp release info from GitHub
        req = urllib.request.Request(
            "https://api.github.com/repos/yt-dlp/yt-dlp/releases/latest",
            headers={"User-Agent": "VidExtract"}
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            release = json.loads(r.read())

        latest_version = release["tag_name"]

        # Find yt-dlp.exe path
        if getattr(sys, 'frozen', False):
            ytdlp_path = os.path.join(os.path.dirname(sys.executable), "yt-dlp.exe")
        else:
            ytdlp_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "yt-dlp.exe")

        # Check current version
        import subprocess
        kwargs = {}
        if sys.platform == "win32":
            kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
        result = subprocess.run(
            [ytdlp_path, "--version"],
            capture_output=True, text=True, **kwargs
        )
        current_version = result.stdout.strip()

        if current_version == latest_version:
            callback(f"✅ yt-dlp is up to date ({current_version})")
            return

        # Download new yt-dlp.exe
        callback(f"🔄 Updating yt-dlp {current_version} → {latest_version}...")

        download_url = next(
            a["browser_download_url"]
            for a in release["assets"]
            if a["name"] == "yt-dlp.exe"
        )

        tmp_path = ytdlp_path + ".tmp"
        urllib.request.urlretrieve(download_url, tmp_path)

        # Replace old with new
        if os.path.exists(ytdlp_path):
            os.remove(ytdlp_path)
        os.rename(tmp_path, ytdlp_path)

        callback(f"✅ yt-dlp updated to {latest_version}")

    except Exception as e:
        callback(f"⚠️ yt-dlp update check failed: {e}")


if __name__ == "__main__":
    app = MainWindow()

    def on_update(msg):
        app.after(0, app._append_log, msg)

    threading.Thread(
        target=auto_update_ytdlp,
        args=(on_update,),
        daemon=True
    ).start()

    app.mainloop()