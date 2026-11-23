"""
Smart Document Converter - Desktop Local Launcher.
Launches the background Python IPC engine and opens the UI in desktop window or browser.
"""

import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import threading
import time
import webbrowser
import uvicorn
from fastapi.staticfiles import StaticFiles
from engine.cli import create_fastapi_app


def launch():
    print("=" * 65)
    print("  Smart Document Converter — Desktop Local Launcher")
    print("=" * 65)

    app = create_fastapi_app()

    # Mount static frontend build if it exists
    frontend_dist = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend", "dist")
    if os.path.exists(frontend_dist):
        app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="static")
        print(f"[+] Loaded production frontend from: {frontend_dist}")
    else:
        print("[!] Note: frontend/dist not found. Run 'npm run build' inside frontend/ to bundle UI.")

    port = 8000
    url = f"http://localhost:{port}"

    def open_browser():
        time.sleep(1.2)
        print(f"[+] Opening application interface at: {url}")
        webbrowser.open(url)

    threading.Thread(target=open_browser, daemon=True).start()

    print(f"[+] Starting Smart Document Converter server on {url}")
    print("[+] Press Ctrl+C to stop the application.")
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning")


if __name__ == "__main__":
    launch()
