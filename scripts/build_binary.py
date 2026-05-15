import subprocess
import sys
import os

def build():
    """
    Build a standalone binary using PyInstaller.
    """
    print("🚀 Starting PyInstaller build...")
    
    # Ensure pyinstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("❌ PyInstaller not found. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # Define the entry point
    entry_point = "src/nodeway/__main__.py"
    
    # Run PyInstaller
    cmd = [
        "pyinstaller",
        "--onefile",
        "--name", "nodeway",
        "--clean",
        "--add-data", "src/nodeway;nodeway",  # Include package data if needed
        entry_point
    ]
    
    print(f"Executing: {' '.join(cmd)}")
    subprocess.run(cmd)
    
    print("\n✅ Build complete. Check the 'dist/' folder.")

if __name__ == "__main__":
    build()
