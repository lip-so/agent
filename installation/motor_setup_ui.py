import tkinter as tk
from tkinter import messagebox, font

class MotorSetupUI(tk.Toplevel):
    """A UI window to guide the user through setting up motors one by one."""

    def __init__(self, parent, device_name, motor_names):
        super().__init__(parent)
        self.title(f"Set Up '{device_name}' Motors")
        self.geometry("600x350")
        self.resizable(False, False)
        
        self.device_name = device_name
        self.motor_names = motor_names
        self.current_motor_index = -1
        self.parent = parent
        self.callback = None
        
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.setup_fonts()
        self.setup_ui()

    def setup_fonts(self):
        font_family = "Roboto Mono"
        try:
            # Check if font is available
            font.nametofont(font_family)
        except tk.TclError:
            font_family = "Courier"

        self.font_main = font.Font(family=font_family, size=14)
        self.font_status = font.Font(family=font_family, size=11)
        self.font_button = font.Font(family=font_family, size=13, weight="bold")

    def setup_ui(self):
        self.colors = {
            'background': '#0d193b',
            'text_primary': '#e0e8f2',
            'text_secondary': '#8c9bb3',
            'success': '#4ade80',
            'surface': '#1a274c',
            'hover': '#2a3f6b'
        }
        self.configure(bg=self.colors['background'])

        self.main_label = tk.Label(self, text=f"Preparing to set up motors for {self.device_name}...",
                                   wraplength=550, justify="center",
                                   fg=self.colors['text_primary'], bg=self.colors['background'], font=self.font_main)
        self.main_label.pack(pady=30, padx=20)

        self.status_label = tk.Label(self, text="", wraplength=550, justify="center",
                                     fg=self.colors['text_secondary'], bg=self.colors['background'], font=self.font_status)
        self.status_label.pack(pady=10, padx=20)

        self.action_button = tk.Button(self, text="Start", command=self.next_step,
                                       fg=self.colors['text_primary'], bg=self.colors['surface'], font=self.font_button,
                                       relief="flat", padx=15, pady=10)
        self.action_button.pack(pady=20)
        
        # Center the window and make it modal
        self.center_window()
        self.transient(parent)
        self.grab_set()

    def center_window(self):
        self.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - (self.winfo_width() // 2)
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")

    def _on_close(self):
        if messagebox.askokcancel("Quit", "Do you want to cancel motor setup?"):
            self.destroy()

    def next_step(self):
        """Processes the next motor in the list."""
        self.current_motor_index += 1
        if self.current_motor_index < len(self.motor_names):
            motor_name = self.motor_names[self.current_motor_index]
            self.main_label.config(text=f"Connect the controller board to the '{motor_name}' motor ONLY.")
            self.status_label.config(text="Ensure no other motors are connected, then press Continue.", fg=self.colors['text_secondary'])
            self.action_button.config(text="Continue", command=self._trigger_callback)
        else:
            self.main_label.config(text="Setup Complete!", fg=self.colors['success'])
            self.status_label.config(text=f"All motors for the {self.device_name} have been configured.")
            self.action_button.config(text="Finish", command=self.destroy)

    def _trigger_callback(self):
        """Disables the button and calls the main logic to set up the motor."""
        if self.callback:
            motor_name = self.motor_names[self.current_motor_index]
            self.action_button.config(state="disabled", text="Configuring...")
            self.status_label.config(text=f"Setting ID for '{motor_name}' motor...")
            
            # The callback in the controller will do the work and then call `report_result`
            self.callback(motor_name)

    def report_result(self, motor_name, success, message):
        """Called by the controller to report the outcome of a motor setup."""
        if success:
            self.status_label.config(text=message, fg=self.colors['success'])
            # After a brief pause, move to the next step automatically
            self.action_button.config(state="normal") # Re-enable for next step
            self.after(1500, self.next_step)
        else:
            self.status_label.config(text=f"Failed: {message}", fg=self.colors['error'])
            self.action_button.config(state="normal", text="Retry")
            # Reset index so "Retry" re-runs the current motor
            self.current_motor_index -= 1 