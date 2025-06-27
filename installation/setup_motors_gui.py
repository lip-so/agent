#!/usr/bin/env python3
import tkinter as tk
from tkinter import messagebox
import argparse
import threading
import time
import sys
from tkinter import font

# Since this is a standalone script, we need to add lerobot to the path
# to import its components. This assumes the script is run from the project root.
try:
    from lerobot.common.robots import make_robot_from_config, RobotConfig, koch_follower
    from lerobot.common.teleoperators import make_teleoperator_from_config, TeleoperatorConfig, koch_leader
except ImportError:
    # Simple fallback for direct execution
    import sys, os
    sys.path.append(os.getcwd())
    from lerobot.common.robots import make_robot_from_config, RobotConfig, koch_follower
    from lerobot.common.teleoperators import make_teleoperator_from_config, TeleoperatorConfig, koch_leader


class MotorSetupApp:
    def __init__(self, root, port, device_type):
        self.root = root
        self.port = port
        self.device_type = device_type
        
        self.device_name = "follower" if "follower" in device_type else "leader"
        
        if self.device_name == "follower":
            cfg = koch_follower.KochFollowerConfig()
            self.motor_names = list(cfg.motors.keys())
            self.config_class = RobotConfig
            self.make_func = make_robot_from_config
        else:
            cfg = koch_leader.KochLeaderConfig()
            self.motor_names = list(cfg.motors.keys())
            self.config_class = TeleoperatorConfig
            self.make_func = make_teleoperator_from_config
            
        self.current_motor_index = -1
        
        self.setup_fonts()
        self.setup_ui()
        self.root.after(200, self.next_step) 

    def setup_fonts(self):
        font_family = "Roboto Mono"
        try:
            font.nametofont(font_family)
        except tk.TclError:
            font_family = "Courier"

        self.font_main = font.Font(family=font_family, size=14)
        self.font_status = font.Font(family=font_family, size=11)
        self.font_button = font.Font(family=font_family, size=13, weight="bold")

    def setup_ui(self):
        self.root.title(f"Set Up '{self.device_name}' Motors")
        self.root.geometry("600x350")
        self.root.resizable(False, False)

        self.colors = {'background': '#0d193b', 'text_primary': '#e0e8f2', 'text_secondary': '#8c9bb3', 'success': '#4ade80', 'error': '#ef4444', 'surface': '#1a274c'}
        self.root.configure(bg=self.colors['background'])

        self.main_label = tk.Label(self.root, text=f"Preparing to set up motors for {self.device_name}...", wraplength=550, justify="center", fg=self.colors['text_primary'], bg=self.colors['background'], font=self.font_main)
        self.main_label.pack(pady=30, padx=20)

        self.status_label = tk.Label(self.root, text="", wraplength=550, justify="center", fg=self.colors['text_secondary'], bg=self.colors['background'], font=self.font_status)
        self.status_label.pack(pady=10, padx=20)

        self.action_button = tk.Button(self.root, text="Start", command=self.next_step, fg=self.colors['text_primary'], bg=self.colors['surface'], font=self.font_button, relief="flat", padx=15, pady=10)
        self.action_button.pack(pady=20)

    def next_step(self):
        self.current_motor_index += 1
        if self.current_motor_index < len(self.motor_names):
            motor_name = self.motor_names[self.current_motor_index]
            self.main_label.config(text=f"Connect the controller board to the '{motor_name}' motor ONLY.")
            self.status_label.config(text="Ensure no other motors are connected, then press Continue.", fg=self.colors['text_secondary'])
            self.action_button.config(text="Continue", command=self.setup_current_motor, state="normal")
        else:
            self.main_label.config(text="Setup Complete!", fg=self.colors['success'])
            self.status_label.config(text=f"All motors for the {self.device_name} have been configured.")
            self.action_button.config(text="Finish", command=self.root.quit)

    def setup_current_motor(self):
        motor_name = self.motor_names[self.current_motor_index]
        self.action_button.config(state="disabled", text="Configuring...")
        self.status_label.config(text=f"Setting ID for '{motor_name}' motor...")
        
        # # This is where the actual hardware interaction would happen.
        # # Since the library uses a blocking `input()`, we simulate the logic here.
        # threading.Thread(target=self._simulate_motor_setup, args=(motor_name,), daemon=True).start()

    def _simulate_motor_setup(self, motor_name):
        try:
            # In a real implementation, you would need a non-interactive function here, e.g.:
            # cfg = self.config_class(type=self.device_type, port=self.port)
            # device = self.make_func(cfg)
            # device.setup_single_motor(motor_name) 
            
            # Simulating the work
            time.sleep(1.5)
            
            # Getting the expected ID for the message
            cfg_for_id = self.config_class(type=self.device_type)
            motor_id = cfg_for_id.motors[motor_name].id
            
            message = f"'{motor_name}' motor ID set to {motor_id}"
            self.root.after(0, self.report_result, motor_name, True, message)
        except Exception as e:
            self.root.after(0, self.report_result, motor_name, False, str(e))
    
    def report_result(self, motor_name, success, message):
        if success:
            self.status_label.config(text=message, fg=self.colors['success'])
            self.action_button.config(state="normal")
            # After a short delay, move to the next step
            self.root.after(1500, self.next_step)
        else:
            self.status_label.config(text=f"Failed: {message}", fg=self.colors['error'])
            self.action_button.config(state="normal", text="Retry", command=self.setup_current_motor)

def main():
    parser = argparse.ArgumentParser(description="GUI for setting up LeRobot motors.")
    parser.add_argument("--port", required=True, help="The serial port of the device.")
    parser.add_argument("--device_type", required=True, help="The type of device (e.g., koch_follower).")
    args = parser.parse_args()

    root = tk.Tk()
    app = MotorSetupApp(root, args.port, args.device_type)
    root.mainloop()

if __name__ == "__main__":
    main() 