#!/usr/bin/env python3
"""
Build script to create standalone executable of LeRobot Installer
"""

import subprocess
import sys
import os
import shutil

def check_pyinstaller():
    """Check if PyInstaller is installed"""
    try:
        import PyInstaller
        return True
    except ImportError:
        return False

def install_pyinstaller():
    """Install PyInstaller"""
    print("Installing PyInstaller...")
    result = subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], 
                          capture_output=True, text=True)
    return result.returncode == 0

def build_executable():
    """Build the executable using PyInstaller"""
    print("Building executable...")
    
    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",           # Create a single executable
        "--windowed",          # No console window (GUI only)
        "--name=LeRobot_Installer",  # Name of the executable
        "--icon=NONE",         # No icon for now
        "robot_installer.py"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Executable built successfully!")
        
        # Show location of executable
        if os.name == 'nt':  # Windows
            exe_path = os.path.join("dist", "LeRobot_Installer.exe")
        else:  # Unix-like
            exe_path = os.path.join("dist", "LeRobot_Installer")
            
        if os.path.exists(exe_path):
            print(f"📦 Executable location: {os.path.abspath(exe_path)}")
            print("\nYou can now distribute this executable to users!")
            print("They won't need Python installed to run it.")
        else:
            print("⚠️ Executable was built but not found in expected location")
            
    else:
        print("❌ Failed to build executable")
        print("Error output:")
        print(result.stderr)
        return False
        
    return True

def main():
    print(" LeRobot Installer - Executable Builder")
    print("=" * 45)
    
    # Check if robot_installer.py exists
    if not os.path.exists("robot_installer.py"):
        print("❌ Error: robot_installer.py not found")
        print("Make sure you're running this from the correct directory")
        return
    
    # Check PyInstaller
    if not check_pyinstaller():
        print("PyInstaller not found. Installing...")
        if not install_pyinstaller():
            print("❌ Failed to install PyInstaller")
            print("Please install it manually: pip install pyinstaller")
            return
        print("✅ PyInstaller installed")
    else:
        print("✅ PyInstaller found")
    
    # Build executable
    if build_executable():
        print("\n🎉 Build completed successfully!")
        
        # Cleanup build files
        cleanup = input("\nClean up build files (spec, build directory)? [y/N]: ")
        if cleanup.lower() in ['y', 'yes']:
            if os.path.exists("build"):
                shutil.rmtree("build")
                print("🗑️ Removed build directory")
            
            spec_file = "LeRobot_Installer.spec"
            if os.path.exists(spec_file):
                os.remove(spec_file)
                print("🗑️ Removed spec file")
                
            print("✅ Cleanup completed")
    else:
        print("\n❌ Build failed")

if __name__ == "__main__":
    main() 