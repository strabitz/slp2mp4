"""
Build script for creating Windows executable of slp2mp4 GUI
This script uses PyInstaller to create a standalone executable
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

# Requirements for the GUI
REQUIREMENTS = [
    "pyinstaller",
    "py-slippi",
    "tomli",
    "tomli-w",  # For saving config files
]

def install_requirements():
    """Install required packages"""
    print("Installing requirements...")
    for req in REQUIREMENTS:
        subprocess.check_call([sys.executable, "-m", "pip", "install", req])

def create_spec_file():
    """Create PyInstaller spec file for the build"""
    spec_content = """
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['slp2mp4_gui.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src', 'src'),  # Include the src directory
        ('src/slp2mp4/defaults.toml', 'slp2mp4'),  # Include default config
    ],
    hiddenimports=[
        'slp2mp4',
        'slp2mp4.config',
        'slp2mp4.modes',
        'slp2mp4.modes.single',
        'slp2mp4.modes.directory',
        'slp2mp4.modes.replay_manager',
        'slp2mp4.orchestrator',
        'slp2mp4.video',
        'slp2mp4.replay',
        'slp2mp4.ffmpeg',
        'slp2mp4.dolphin',
        'slp2mp4.dolphin.runner',
        'slp2mp4.dolphin.comm',
        'slp2mp4.dolphin.ini',
        'slp2mp4.util',
        'slippi',
        'tomli',
        'tomli_w',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='slp2mp4-gui',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Don't show console window
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None
)
"""

    with open("slp2mp4-gui.spec", "w") as f:
        f.write(spec_content)

    print("Created slp2mp4-gui.spec")

def build_executable():
    """Build the executable using PyInstaller"""
    print("Building executable...")

    # Clean previous builds
    for dir_name in ["build", "dist"]:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)

    # Run PyInstaller
    subprocess.check_call([sys.executable, "-m", "PyInstaller", "slp2mp4-gui.spec"])

    print("\nBuild complete! Executable is in the 'dist' folder.")

def create_batch_file():
    """Create a batch file to run the GUI"""
    batch_content = """@echo off
cd /d "%~dp0"
start "" "dist\\slp2mp4-gui.exe"
"""

    with open("run-slp2mp4-gui.bat", "w") as f:
        f.write(batch_content)

    print("Created run-slp2mp4-gui.bat")

def main():
    print("slp2mp4 GUI Windows Build Script")
    print("=================================\n")

    # Check if we're in the right directory
    if not os.path.exists("src/slp2mp4"):
        print("ERROR: This script must be run from the slp2mp4 project root directory")
        print("(The directory containing the 'src' folder)")
        return 1

    # Save the GUI script if it doesn't exist
    if not os.path.exists("slp2mp4_gui.py"):
        print("ERROR: slp2mp4_gui.py not found!")
        print("Please save the GUI script as 'slp2mp4_gui.py' in the project root")
        return 1

    try:
        # Install requirements
        install_requirements()

        # Create spec file
        create_spec_file()

        # Build executable
        build_executable()

        # Create batch file
        create_batch_file()

        print("\n✅ Build successful!")
        print("\nTo run the GUI:")
        print("  - Double-click 'run-slp2mp4-gui.bat'")
        print("  - Or run 'dist\\slp2mp4-gui.exe' directly")

        print("\nTo distribute:")
        print("  - Copy the entire 'dist\\slp2mp4-gui' folder")
        print("  - Users only need to run slp2mp4-gui.exe")

    except Exception as e:
        print(f"\n❌ Build failed: {e}")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
