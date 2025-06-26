#!/usr/bin/env python3
"""
LeRobot Installer
A clean, modern installer for the LeRobot robotics platform.
"""

import tkinter as tk
from tkinter import messagebox, filedialog
import subprocess
import threading
import os
import sys
import shutil
from pathlib import Path
import platform
import time

from installer_ui import InstallerUI

class LeRobotInstaller:
    def __init__(self, root):
        self.root = root
        self.root.title("LeRobot Installer")
        self.root.geometry("1000x650")
        self.root.resizable(False, False)
        
        # --- State Variables ---
        self.installation_complete = False
        self.installation_thread_running = False
        self.port_discovery_running = False
        self.total_steps = 8
        self.current_step = 0
        self.ports_before_unplug = []
        self.current_device_for_port_finding = ""
        
        # --- Paths ---
        self.install_dir = os.path.expanduser("~/lerobot")
        
        # --- Port Discovery ---
        self.follower_port = None
        self.leader_port = None

        # --- Logging ---
        self.terminal_output = []
        
        # --- UI ---
        self.ui = InstallerUI(self.root, self)

        # Check for existing install on startup
        self.root.after(200, self._check_on_startup)

    def handle_install_click(self):
        self.start_installation()

    def handle_motor_click(self):
        if self.installation_complete and not self.port_discovery_running:
            self.start_port_discovery()

    def handle_change_dir_click(self):
        self.change_installation_directory()
        
    def handle_port_finder_action_click(self):
        """Handles the main action button click during the port finding process."""
        # This function is called by the UI's action button.
        # It relies on the self.port_discovery_running state to know what to do.
        if self.port_discovery_running:
            self._after_unplug()

    def change_installation_directory(self):
        """Allows the user to select a new installation directory."""
        if self.installation_thread_running:
            messagebox.showwarning("Installation In Progress", "Cannot change directory while an installation is running.")
            return

        new_parent = filedialog.askdirectory(title="Choose a Parent Directory for LeRobot", initialdir=os.path.dirname(self.install_dir))
        if new_parent:
            self.install_dir = os.path.join(new_parent, "lerobot")
            self.ui.update_install_dir_text(self.install_dir)
            self.log(f"Installation directory changed to: {self.install_dir}")

    def _check_on_startup(self):
        """Checks for an existing installation when the app starts."""
        if self._installation_exists():
            self.log("Existing LeRobot installation detected.")
            self._update_ui_for_existing_install(silent=True)

    def start_installation(self):
        """Starts the installation process if not already installed."""
        if self.installation_thread_running:
            self.log("Installation is already in progress.")
            return

        if self.installation_complete:
            messagebox.showinfo("Already Installed",
                "LeRobot is already installed. You can proceed to find ports.")
            return
        
        self._reset_ui_for_install()
        threading.Thread(target=self._installation_thread, daemon=True).start()
    
    def _installation_exists(self):
        """Checks if a LeRobot directory or conda environment already exists."""
        dir_exists = os.path.exists(self.install_dir)
        conda_path = shutil.which('conda')
        if not conda_path:
            return dir_exists
        try:
            process = subprocess.run([conda_path, "env", "list"], capture_output=True, text=True, timeout=10)
            env_exists = any(line.strip().startswith('lerobot ') for line in process.stdout.splitlines())
            return dir_exists or env_exists
        except Exception:
            return dir_exists

    def _update_ui_for_existing_install(self, silent=False):
        """Updates the UI to show that an installation already exists."""
        self.installation_complete = True
        self.update_progress(self.total_steps, "Existing installation detected.")
        self.ui.set_button_state('motor', 'Find Ports', 'text_primary')
        self.ui.set_button_state('install', 'Installed', 'text_secondary')
        if not silent:
            messagebox.showinfo("Success", "LeRobot has been installed successfully!")

    def _reset_ui_for_install(self):
        """Clears logs and resets the UI for a new installation."""
        self.terminal_output.clear()
        self.update_progress(0, "Ready to begin installation")

    def _installation_thread(self):
        """The main installation logic running in a separate thread."""
        self.installation_thread_running = True
        self.ui.set_button_state('install', 'Installing...', 'text_secondary')
        
        try:
            steps = [
                (self._check_prerequisites, "Checking prerequisites..."),
                (self._clone_repository, f"Cloning repository into {self.install_dir}..."),
                (self._create_conda_environment, "Creating conda environment 'lerobot'..."),
                (self._install_ffmpeg, "Installing ffmpeg..."),
                (self._install_lerobot, "Installing LeRobot package..."),
                (self._install_dynamixel, "Installing Dynamixel SDK..."),
                (self._install_additional_dependencies, "Installing additional dependencies..."),
                (self._verify_installation, "Verifying installation..."),
            ]

            for i, (func, msg) in enumerate(steps):
                self.update_progress(i, msg)
                if not func():
                    raise RuntimeError(f"Step '{msg}' failed. Check logs for details.")
            
            self._finalize_installation()

        except Exception as e:
            self.log(f"Error during installation: {e}")
            messagebox.showerror("Installation Failed", f"An error occurred: {e}")
            self.ui.set_button_state('install', 'Retry Install', 'error')

        finally:
            self.installation_thread_running = False

    def _finalize_installation(self):
        """Finalizes the installation, updating the UI."""
        self._update_ui_for_existing_install()

    def _check_prerequisites(self):
        """Checks for Git and Conda."""
        return shutil.which("git") and shutil.which("conda")

    def _clone_repository(self):
        if os.path.exists(self.install_dir):
            return True
        return self._run_command(f"git clone https://github.com/huggingface/lerobot.git {self.install_dir}")

    def _create_conda_environment(self):
        return self._run_command(f"{shutil.which('conda')} create -n lerobot python=3.10 -y")

    def _install_ffmpeg(self):
        return self._run_command(f"{self._get_conda_executable('conda')} install conda-forge::ffmpeg -y")

    def _install_lerobot(self):
        return self._run_command(f"{self._get_conda_executable('pip')} install -e .", cwd=self.install_dir)

    def _install_dynamixel(self):
        return self._run_command(f"{self._get_conda_executable('pip')} install dynamixel-sdk", cwd=self.install_dir)

    def _install_additional_dependencies(self):
        req_path = os.path.join(self.install_dir, "requirements.txt")
        if not os.path.exists(req_path):
            return True
        return self._run_command(f"{self._get_conda_executable('pip')} install -r {req_path}", cwd=self.install_dir)

    def _verify_installation(self):
        return self._run_command(f"{self._get_conda_executable('python')} -c 'import lerobot; print(lerobot.__version__)'")

    def _get_conda_executable(self, name):
        conda_path = shutil.which('conda')
        if not conda_path: return name
        conda_base_dir = os.path.dirname(os.path.dirname(conda_path))
        env_bin_path = os.path.join(conda_base_dir, "envs", "lerobot", "bin", name)
        return env_bin_path if os.path.exists(env_bin_path) else f"{shutil.which('conda')} run -n lerobot --no-capture-output {name}"

    def start_port_discovery(self):
        """Starts the step-by-step port discovery process in the main UI."""
        self.log("Starting guided port discovery...")
        self.port_discovery_running = True
        self.ui.show_port_finding_view()
        # Start with the follower device
        threading.Thread(target=self._find_next_port, daemon=True).start()

    def _find_next_port(self):
        """Determines which device to find next and starts the process."""
        if not self.follower_port:
            self.current_device_for_port_finding = "follower"
        elif not self.leader_port:
            self.current_device_for_port_finding = "leader"
        else:
            # Both are found, process is complete.
            self.port_discovery_running = False
            self.ui.show_installation_view() # Switch back to main view
            messagebox.showinfo("Success", f"Both ports found!\n\nFollower: {self.follower_port}\nLeader: {self.leader_port}")
            return
        
        self._prepare_for_unplug()

    def _find_available_ports(self):
        try:
            from serial.tools import list_ports
            if platform.system() == "Windows":
                return {port.device for port in list_ports.comports()}
            else:
                return {str(path) for path in Path("/dev").glob("tty*")}
        except ImportError:
            messagebox.showerror("Error", "The 'pyserial' library is required. Please install it.")
            return None
        except Exception as e:
            messagebox.showerror("Error", f"Could not list ports: {e}")
            return None

    def _prepare_for_unplug(self):
        """First stage of finding a single port."""
        self.ui.update_port_finder_instructions(f"Scanning for connected devices...")
        self.ports_before_unplug = self._find_available_ports()
        if self.ports_before_unplug is None:
            self.ui.update_port_finder_instructions("Error: Could not scan for ports. Please try again.")
            self.ui.set_port_finder_button("Retry", self._find_next_port)
            return

        instruction = f"Please UNPLUG the USB cable from the '{self.current_device_for_port_finding}' robot now."
        self.ui.update_port_finder_instructions(instruction)
        self.ui.set_port_finder_button("Unplugged")

    def _after_unplug(self):
        """Second stage, after user has unplugged the device."""
        self.ui.update_port_finder_instructions("Scanning again...")
        self.ui.set_port_finder_button("", state="disabled") 
        
        time.sleep(1.0)
        ports_after = self._find_available_ports()
        
        if ports_after is None:
            self.ui.update_port_finder_instructions("Error: Could not scan for ports. Please try again.")
            self.ui.set_port_finder_button("Retry", self._find_next_port)
            return
            
        diff = self.ports_before_unplug - ports_after
        
        if len(diff) == 1:
            port = diff.pop()
            if self.current_device_for_port_finding == "follower":
                self.follower_port = port
                self.ui.update_follower_port_display(port)
            else:
                self.leader_port = port
                self.ui.update_leader_port_display(port)
            
            self.log(f"Found {self.current_device_for_port_finding} port: {port}")
            # Move to the next device
            self._find_next_port()
            
        elif len(diff) == 0:
            self.ui.update_port_finder_instructions("No device change was detected. Please try again.")
            self.ui.set_port_finder_button("Retry", self._find_next_port)
        else:
            self.ui.update_port_finder_instructions(f"Multiple devices changed. Please only unplug one device at a time.")
            self.ui.set_port_finder_button("Retry", self._find_next_port)

    def log(self, message):
        """Logs a message to the console and internal log list."""
        print(message)
        self.terminal_output.append(message)
        self.update_status_text(message.splitlines()[-1])

    def update_progress(self, step, message):
        """Updates the progress bar and text."""
        self.current_step = step
        self.log(f"Progress: Step {step}/{self.total_steps} - {message}")
        self.ui.update_progress(step, self.total_steps, message)

    def update_status_text(self, message):
        """Updates the status text in the UI footer."""
        self.ui.update_status_text(message)

    def _run_command(self, command, cwd=None):
        """Runs a shell command, logs its output, and returns success."""
        self.log(f"Running command: {command}")
        try:
            process = subprocess.run(command, shell=True, check=True, capture_output=True, text=True, cwd=cwd)
            self.log(process.stdout)
            if process.stderr:
                self.log(f"Stderr: {process.stderr}")
            return True
        except subprocess.CalledProcessError as e:
            self.log(f"Error running command: {command}")
            self.log(e.stdout)
            self.log(e.stderr)
            return False

def main():
    """Main function to create and run the installer application."""
    root = tk.Tk()
    app = LeRobotInstaller(root)
    root.mainloop()

if __name__ == "__main__":
    main() 
    