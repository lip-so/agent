#!/usr/bin/env python3
"""
LeRobot Installer Launcher
Simple launcher script with version checks and error handling.
"""

import sys
import os

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 6):
        print("Error: Python 3.6 or higher is required")
        print(f"Current version: {sys.version}")
        print("Please install a newer version of Python and try again.")
        return False
    return True

def check_tkinter():
    """Check if tkinter is available"""
    try:
        import tkinter
        return True
    except ImportError:
        print("Error: tkinter is not available")
        print("Please install tkinter (usually comes with Python)")
        print("On Ubuntu/Debian: sudo apt-get install python3-tk")
        return False

def main():
    print("LeRobot Installer Launcher")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        input("Press Enter to exit...")
        return
    
    # Check tkinter
    if not check_tkinter():
        input("Press Enter to exit...")
        return
    
    # Check if main installer exists
    installer_path = "robot_installer.py"
    if not os.path.exists(installer_path):
        print(f"Error: {installer_path} not found")
        print("Make sure robot_installer.py is in the same directory as this launcher.")
        input("Press Enter to exit...")
        return
    
    print("All checks passed. Launching installer...")
    print()
    
    # Import and run the main installer
    try:
        import robot_installer
        robot_installer.main()
    except Exception as e:
        print(f"Error launching installer: {e}")
        print("Please check the error message above and try again.")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main() 