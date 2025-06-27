#!/usr/bin/env python3
"""
LeRobot Installer Launcher
Simple launcher script that handles the application flow from the welcome
screen to the main installer.
"""

import tkinter as tk
from tkinter import messagebox
import sys
import os

# Adjust path to import from the root directory and subdirectories
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

try:
    from ui.welcome_ui import WelcomeScreen
    from robot_installer import LeRobotInstaller
    from PIL import ImageTk, Image
except ImportError as e:
    messagebox.showerror("Import Error", f"A required module is missing: {e}\n\nPlease ensure all files are in their correct locations and required libraries are installed.")
    sys.exit(1)


class MainApplication:
    """Orchestrates the application flow from welcome screen to installer."""
    def __init__(self, root):
        self.root = root
        self.root.withdraw() # Hide the main root window initially
        self.show_welcome_screen()

    def show_welcome_screen(self):
        self.welcome_window = tk.Toplevel(self.root)
        self.welcome_window.title("Tune Robotics")
        self.welcome_window.geometry("1200x750")
        self.welcome_window.resizable(True, True)
        self.welcome_app = WelcomeScreen(self.welcome_window, self.robot_selected_callback)
        self.welcome_window.protocol("WM_DELETE_WINDOW", self.root.destroy)

    def robot_selected_callback(self, robot_type):
        """Called when a robot is chosen on the welcome screen."""
        if robot_type == 'koch':
            # Destroy the welcome screen and show the main installer
            self.welcome_window.destroy()
            self.show_installer()
        else:
            messagebox.showinfo("Coming Soon", f"Configuration for '{robot_type}' is not yet implemented.", parent=self.welcome_window)
    
    def show_installer(self):
        """Creates and shows the main installer window."""
        self.root.deiconify()
        self.root.title("Tune Robotics Installer")
        self.root.geometry("1200x750")
        self.root.resizable(True, True)
        self.installer_app = LeRobotInstaller(self.root)


def main():
    """Main entry point for the entire application."""
    # Basic prerequisite checks
    if sys.version_info < (3, 6):
        messagebox.showerror("Error", "Python 3.6 or higher is required.")
        return
    
    # Pillow is checked here implicitly by the import at the top

    root = tk.Tk()
    app = MainApplication(root)
    root.mainloop()

if __name__ == "__main__":
    main() 