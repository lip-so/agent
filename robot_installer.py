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
import webbrowser
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

from ui.installer_ui import InstallerUI
from installation.motor_setup_ui import MotorSetupUI
from lerobot.common.robots import make_robot_from_config, RobotConfig, koch_follower
from lerobot.common.teleoperators import make_teleoperator_from_config, TeleoperatorConfig, koch_leader
from installation.setup_motors_gui import MotorSetupApp # Assuming this will be used

class LeRobotInstaller:
    def __init__(self, root):
        self.root = root
        self.root.title("LeRobot Installer")
        self.root.geometry("1000x650")
        self.root.resizable(False, False)
        
        self.installation_complete = False
        self.installation_thread_running = False
        self.port_discovery_running = False
        self.total_steps = 8
        self.current_step = 0
        self.ports_before_unplug = []
        self.current_device_for_port_finding = ""
        
       
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

    def _check_on_startup(self):
        """Checks for an existing installation when the app starts."""
        if self._installation_exists():
            self.installation_complete = True
            self.ui.set_button_state('install', 'Installed', 'text_secondary')
            self.ui.set_button_state('motor', 'Find Ports', 'text_primary')
            self.ui.update_progress(8, 8, "Existing installation detected.")

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

    def handle_install_click(self):
        self.start_installation()

    def handle_motor_click(self):
        if self.installation_complete and not self.port_discovery_running:
            self.start_port_discovery()
        else:
            messagebox.showwarning("Prerequisites Not Met", "Please complete the installation first.")

    def handle_setup_click(self):
        if self.installation_complete and self.follower_port and self.leader_port:
            self.start_motor_setup()
        else:
            messagebox.showwarning("Prerequisites Not Met", "Please complete installation and port discovery first.")

    def handle_test_click(self):
        if self.installation_complete and self.follower_port and self.leader_port:
            self.start_web_server()
        else:
            messagebox.showwarning("Prerequisites Not Met", "The full setup must be complete before testing the robot.")

    def handle_change_dir_click(self):
        if self.installation_thread_running:
            messagebox.showwarning("Busy", "Cannot change directory during installation.")
            return
        new_parent = filedialog.askdirectory(title="Choose Parent Directory", initialdir=os.path.dirname(self.install_dir))
        if new_parent:
            self.install_dir = os.path.join(new_parent, "lerobot")
            self.ui.update_install_dir_text(self.install_dir)

    def handle_port_finder_action_click(self):
        """Handles the main action button click during the port finding process."""
        # This function is called by the UI's action button.
        # It relies on the self.port_discovery_running state to know what to do.
        if self.port_discovery_running:
            self._after_unplug()

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
    
    def _update_ui_for_existing_install(self, silent=False):
        """Updates the UI to show that an installation already exists."""
        self.installation_complete = True
        self.update_progress(self.total_steps, "Existing installation detected.")
        self.ui.set_button_state('motor', '🎯 Find Ports', 'text_primary')
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
            if self.follower_port and self.leader_port:
                messagebox.showinfo("Success", f"Both ports found!\n\nFollower: {self.follower_port}\nLeader: {self.leader_port}", parent=self.root)
                self.ui.set_button_state('setup', '⚙️ Set Up Motors', 'text_primary') # Enable setup button
            else:
                messagebox.showwarning("Incomplete", "One or more ports were not identified.", parent=self.root)
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

    def start_motor_setup(self):
        self.log("Starting guided motor setup...")
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "setup_motors_gui.py")

        if not os.path.exists(script_path):
            messagebox.showerror("Error", f"Motor setup script not found at:\n{script_path}")
            return

        # Run for follower
        self.log("Starting setup for FOLLOWER arm...")
        if not self._run_motor_setup_for_device("follower", self.follower_port, script_path):
            return # Stop if follower setup fails or is canceled

        # Run for leader
        self.log("Starting setup for LEADER arm...")
        if not self._run_motor_setup_for_device("leader", self.leader_port, script_path):
            return

        messagebox.showinfo("Success", "Motor setup process completed for both devices.")
        self.ui.set_button_state('test', '🚀 Test Robot', 'text_primary')

    def _run_motor_setup_for_device(self, device_name, port, script_path):
        """Executes the motor setup script for a single device and waits for it."""
        device_type = f"koch_{device_name}"
        self.log(f"Launching setup for {device_name} on port {port}...")
        
        command = [sys.executable, script_path, "--port", port, "--device_type", device_type]
        
        try:
            # Using Popen to not block the main UI thread entirely, but this is a simplified example.
            # For a truly non-blocking approach with real-time feedback, a different architecture would be needed.
            process = subprocess.run(command, check=True, capture_output=True, text=True, cwd=os.path.dirname(os.path.abspath(__file__)))
            self.log(f"{device_name.capitalize()} setup output:\n{process.stdout}")
            self.save_configuration(device_name, {'port': port}) # Save after successful setup
            return True
        except subprocess.CalledProcessError as e:
            self.log(f"Error during {device_name} setup: {e.stderr}")
            messagebox.showerror(f"{device_name.capitalize()} Setup Failed", f"The motor setup script failed.\n\nError:\n{e.stderr}")
            return False
        except FileNotFoundError:
            messagebox.showerror("Error", "Could not find 'python' executable. Please ensure Python is in your system's PATH.")
            return False

    def save_configuration(self, device_name, updates):
        """Programmatically updates and saves the Python config file for a device."""
        is_robot = "follower" in device_name
        
        if is_robot:
            config_path = os.path.join(self.install_dir, "lerobot", "common", "robots", "koch_follower", "config_koch_follower.py")
        else:
            config_path = os.path.join(self.install_dir, "lerobot", "common", "teleoperators", "koch_leader", "config_koch_leader.py")

        if not os.path.exists(config_path):
            self.log(f"Warning: Config file not found at {config_path}. Cannot save settings.")
            return

        try:
            with open(config_path, 'r') as f:
                lines = f.readlines()

            with open(config_path, 'w') as f:
                for line in lines:
                    # This is a simple but effective way to update the port
                    if 'port: str | None = ' in line and 'port' in updates:
                        f.write(f"    port: str | None = '{updates['port']}'\n")
                    # In a real implementation, you'd add logic here to update motor IDs
                    # elif 'motors: dict[str, MotorConfig] = ' in line and 'motors' in updates:
                    #    f.write(f"    motors: dict[str, MotorConfig] = {updates['motors']}\n")
                    else:
                        f.write(line)
            
            self.log(f"Successfully saved configuration for {device_name} to {config_path}")
        except Exception as e:
            self.log(f"Error saving configuration for {device_name}: {e}")
            messagebox.showerror("Save Failed", f"Could not save settings to {config_path}.")

    def _start_full_port_discovery(self):
        """Runs the discovery process for both follower and leader ports."""
        # Find follower port
        self.follower_port = self._find_single_port("follower")
        if self.follower_port:
            self.log(f"Follower port found: {self.follower_port}")
            self.ui.update_follower_port_display(self.follower_port)
            self.save_configuration("follower", {"port": self.follower_port})
        else:
            self.log("Follower port detection was canceled or failed.")
            messagebox.showwarning("Incomplete", "Port for follower not identified. Aborting.", parent=self.root)
            return

        self.leader_port = self._find_single_port("leader")
        if self.leader_port:
            self.log(f"Leader port found: {self.leader_port}")
            self.ui.update_leader_port_display(self.leader_port)
            self.save_configuration("leader", {"port": self.leader_port})
        else:
            self.log("Leader port detection was canceled or failed.")

        if self.follower_port and self.leader_port:
            messagebox.showinfo("Success", f"Both ports found and saved!\n\nFollower: {self.follower_port}\nLeader: {self.leader_port}", parent=self.root)
            self.ui.set_button_state('setup', 'Set Up Motors', 'text_primary') # Enable setup button
        else:
            messagebox.showwarning("Incomplete", "One or more ports were not identified.", parent=self.root)

    def start_web_server(self):
        """Initializes and runs the Flask web server in a new thread."""
        self.log("Starting web server for robot testing...")
        
        # Check if server is already running
        if hasattr(self, 'server_thread') and self.server_thread.is_alive():
            self.log("Server is already running.")
            webbrowser.open("http://127.0.0.1:7860")
            return

        app = Flask(__name__, static_folder='web_interface')
        CORS(app)

        @app.route('/')
        def index():
            return send_from_directory(app.static_folder, 'index.html')

        @app.route('/api/chat', methods=['POST'])
        def chat():
            # In a real implementation, this would connect to the robot
            user_message = request.json.get('message', '')
            self.log(f"Received message from web UI: {user_message}")
            
            # Simulate a response
            response_text = f"Simulated response to: '{user_message}'"
            return jsonify({'response': response_text})
        
        def run_app():
            self.log("Web server is running on http://127.0.0.1:7860")
            app.run(port=7860)

        self.server_thread = threading.Thread(target=run_app, daemon=True)
        self.server_thread.start()
        
        # Give the server a moment to start up before opening the browser
        time.sleep(1)
        webbrowser.open("http://127.0.0.1:7860")

def main():
    """Application entry point."""
    # This main function is now for the installer part only.
    # The actual app launch is handled by launch_installer.py
    root = tk.Tk()
    app = LeRobotInstaller(root)
    root.mainloop()

if __name__ == "__main__":
    main() 
    