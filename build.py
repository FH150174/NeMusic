"""PyInstaller build script for NeMusic.

Run: python build.py
Output: dist/NeMusic.exe
"""
import PyInstaller.__main__
import os
import sys
import shutil


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def find_vlc_path():
    """Find the VLC installation directory."""
    paths = [
        r"C:\Program Files\VideoLAN\VLC",
        r"C:\Program Files (x86)\VideoLAN\VLC",
    ]
    for p in paths:
        if os.path.exists(p):
            return p
    return None


def find_node_path():
    """Find Node.js installation."""
    import subprocess
    try:
        result = subprocess.run(["where", "node"], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip().split("\n")[0]
    except Exception:
        pass
    paths = [
        r"C:\Program Files\nodejs\node.exe",
        r"D:\Node.js\node.exe",
    ]
    for p in paths:
        if os.path.exists(p):
            return p
    return None


def clean():
    """Clean previous build artifacts."""
    for d in ["build", "dist", "__pycache__"]:
        p = os.path.join(BASE_DIR, d)
        if os.path.exists(p):
            shutil.rmtree(p)
    for f in os.listdir(BASE_DIR):
        if f.endswith(".spec"):
            os.remove(os.path.join(BASE_DIR, f))


def build():
    frontend_dir = os.path.join(BASE_DIR, "frontend")
    icon_path = os.path.join(BASE_DIR, "icon.ico")

    args = [
        os.path.join(BASE_DIR, "main.py"),
        "--name=NeMusic",
        "--onefile",
        "--windowed",
        "--clean",
        f"--add-data={frontend_dir}{os.pathsep}frontend",
        # Include Node.js API server script
        f"--add-data={os.path.join(BASE_DIR, 'api_server.js')}{os.pathsep}.",
        f"--add-data={os.path.join(BASE_DIR, 'crypto_helper.js')}{os.pathsep}.",
        "--hidden-import=vlc",
        "--hidden-import=pywebview",
        "--hidden-import=requests",
        "--hidden-import=json",
        "--hidden-import=hashlib",
        "--hidden-import=sqlite3",
        "--hidden-import=subprocess",
        "--collect-all=pywebview",
    ]

    # Icon
    if os.path.exists(icon_path):
        args.append(f"--icon={icon_path}")
    else:
        print("Warning: icon.ico not found, skipping icon embedding.")

    # VLC libraries
    vlc_path = find_vlc_path()
    if vlc_path:
        libvlc_dll = os.path.join(vlc_path, "libvlc.dll")
        libvlccore_dll = os.path.join(vlc_path, "libvlccore.dll")
        vlc_plugins = os.path.join(vlc_path, "plugins")
        if os.path.exists(libvlc_dll):
            args.append(f"--add-binary={libvlc_dll}{os.pathsep}.")
        if os.path.exists(libvlccore_dll):
            args.append(f"--add-binary={libvlccore_dll}{os.pathsep}.")
        if os.path.exists(vlc_plugins):
            args.append(f"--add-binary={vlc_plugins}{os.pathsep}plugins")
        print(f"VLC found at: {vlc_path}")
    else:
        print("Warning: VLC not found.")

    # Node.js binary (for running the API server)
    node_path = find_node_path()
    if node_path:
        args.append(f"--add-binary={node_path}{os.pathsep}.")
        print(f"Node.js found at: {node_path}")
    else:
        print("Warning: Node.js not found at C:\\Program Files\\nodejs\\")

    print("Building NeMusic.exe (this may take a few minutes)...")
    PyInstaller.__main__.run(args)
    print("Build complete!")
    print("Output: dist/NeMusic.exe")


if __name__ == "__main__":
    if "--clean" in sys.argv:
        clean()
    build()
