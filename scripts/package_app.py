"""
Portable Release Packaging Script for Windows.
Bundles the application into dist/SmartDocumentConverter-Portable.
"""

import os
import shutil
import zipfile


def package():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dist_dir = os.path.join(root_dir, "dist")
    package_dir = os.path.join(dist_dir, "SmartDocumentConverter-Portable")

    print("[*] Packaging Smart Document Converter Portable Edition...")

    if os.path.exists(package_dir):
        shutil.rmtree(package_dir)
    os.makedirs(package_dir, exist_ok=True)

    # 1. Copy engine
    shutil.copytree(os.path.join(root_dir, "engine"), os.path.join(package_dir, "engine"))

    # 2. Copy scripts
    shutil.copytree(os.path.join(root_dir, "scripts"), os.path.join(package_dir, "scripts"))

    # 3. Copy frontend/dist
    frontend_dist = os.path.join(root_dir, "frontend", "dist")
    if os.path.exists(frontend_dist):
        shutil.copytree(frontend_dist, os.path.join(package_dir, "frontend", "dist"))

    # 4. Copy docs and license
    for fname in ["requirements.txt", "README.md", "LICENSE"]:
        src = os.path.join(root_dir, fname)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(package_dir, fname))

    # 5. Create Windows Batch Launcher
    bat_content = (
        "@echo off\n"
        "title Smart Document Converter\n"
        "echo Launching Smart Document Converter...\n"
        "python -m pip install -r requirements.txt >nul 2>&1\n"
        "python scripts\\run_app.py\n"
        "pause\n"
    )
    with open(os.path.join(package_dir, "SmartDocumentConverter.bat"), "w") as f:
        f.write(bat_content)

    # 6. Create PowerShell Launcher
    ps1_content = (
        "# Smart Document Converter Launcher\n"
        "Write-Host 'Launching Smart Document Converter...' -ForegroundColor Cyan\n"
        "& python -m pip install -r requirements.txt\n"
        "& python scripts\\run_app.py\n"
    )
    with open(os.path.join(package_dir, "SmartDocumentConverter.ps1"), "w") as f:
        f.write(ps1_content)

    # 7. Zip package
    zip_path = os.path.join(dist_dir, "SmartDocumentConverter-v1.0.0-windows-portable.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(package_dir):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, dist_dir)
                zf.write(full_path, rel_path)

    size_mb = os.path.getsize(zip_path) / (1024 * 1024)
    print(f"[+] Portable package generated: {zip_path} ({size_mb:.2f} MB)")


if __name__ == "__main__":
    package()
