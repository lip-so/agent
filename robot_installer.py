#!/usr/bin/env python3
"""
LeRobot Installer - Tune Robotics
Beautiful, modern installer for LeRobot robotics platform.
"""

import tkinter as tk
from tkinter import ttk, messagebox, font, filedialog
import subprocess
import threading
import os
import sys
import platform
import time
import shutil
from pathlib import Path
import time
import math

class LeRobotInstaller:
    def __init__(self, root):
        self.root = root
        self.root.title("LeRobot Installer")
        self.root.geometry("1000x650")
        self.root.resizable(False, False)
        
        # Exact Tune Robotics Color Scheme from CSS
        self.colors = {
            'background': '#000b2a',
            'text_primary': '#e0e8f2',
            'text_secondary': '#8c9bb3',
            'accent': '#e0e8f2',
            'surface': '#0d193b',
            'border': '#1a274c',
            'success': '#4ade80',
            'warning': '#fbbf24',
            'error': '#ef4444',
            'hover': '#1a274c',
            'secondary_text': '#6a7891'
        }
        
        # Configure root window
        self.root.configure(bg=self.colors['background'])
        
        # Variables
        self.installation_complete = False
        self.motor_configuration_complete = False
        self.current_step = 0
        self.total_steps = 8
        self.animation_running = False
        self.show_details = False
        
        # Motor port storage
        self.leader_port = None
        self.follower_port = None
        
        # Installation directory - dynamically use current user's home
        self.install_dir = os.path.expanduser("~/lerobot")
        
        # Hidden terminal output
        self.terminal_output = []
        
        # Setup fonts and styles
        self.setup_fonts()
        self.setup_ui()
        
    def setup_fonts(self):
        """Setup Roboto Mono fonts matching Tune Robotics design"""
        try:
            # Logo font (1.2rem equivalent)
            self.font_logo = font.Font(family='Roboto Mono', size=15, weight='bold')
            # Super title (2.8rem equivalent) 
            self.font_super_title = font.Font(family='Roboto Mono', size=36, weight='bold')
            # Title (1.8rem equivalent)
            self.font_title = font.Font(family='Roboto Mono', size=22, weight='bold')
            # Subtitle (1rem equivalent)
            self.font_subtitle = font.Font(family='Roboto Mono', size=13)
            # Body text (0.95rem equivalent)
            self.font_body = font.Font(family='Roboto Mono', size=12)
            # Small text (0.8rem equivalent)
            self.font_small = font.Font(family='Roboto Mono', size=10)
            # Button text (1rem equivalent)
            self.font_button = font.Font(family='Roboto Mono', size=13, weight='bold')
        except:
            # Fallback fonts
            self.font_logo = font.Font(size=15, weight='bold')
            self.font_super_title = font.Font(size=36, weight='bold')
            self.font_title = font.Font(size=22, weight='bold')
            self.font_subtitle = font.Font(size=13)
            self.font_body = font.Font(size=12)
            self.font_small = font.Font(size=10)
            self.font_button = font.Font(size=13, weight='bold')
            

        
    def setup_ui(self):
        """Setup the modern, beautiful UI"""
        # Main canvas for custom drawing
        self.canvas = tk.Canvas(self.root, 
                               bg=self.colors['background'], 
                               highlightthickness=0,
                               width=1000, height=650)
        self.canvas.pack(fill='both', expand=True)
        
        # Create main sections
        self.create_header()
        self.create_hero_section()
        self.create_main_content()
        self.create_status_section()
        
        # Bind events
        self.canvas.bind('<Button-1>', self.on_canvas_click)
        self.canvas.bind('<Motion>', self.on_mouse_motion)
        
    def create_header(self):
        """Create the header with logo - fixed position like the website"""
        # Logo in fixed position (top-left)
        self.canvas.create_text(32, 32, 
                               text="TUNE ROBOTICS", 
                               font=self.font_logo,
                               fill=self.colors['text_primary'],
                               anchor='w')
                               
    def create_hero_section(self):
        """Create hero section matching Tune Robotics landing page style"""
        # Super title (like landing-super-title)
        self.canvas.create_text(500, 140, 
                               text="LeRobot", 
                               font=self.font_super_title,
                               fill=self.colors['text_primary'],
                               anchor='center')
                               
        # Main title (like landing-title) 
        self.canvas.create_text(500, 180, 
                               text="Installer", 
                               font=self.font_title,
                               fill=self.colors['text_secondary'],
                               anchor='center')
                               
        # Subtitle (like landing-subtitle)
        self.canvas.create_text(500, 220, 
                               text="Automated installation and configuration for LeRobot robotics platform", 
                               font=self.font_small,
                               fill=self.colors['secondary_text'],
                               anchor='center')
                               
                        # Installation directory in smaller text
        self.install_dir_text_id = self.canvas.create_text(500, 240, 
                               text=f"Installation directory: {self.install_dir}", 
                               font=self.font_small,
                               fill=self.colors['secondary_text'],
                               anchor='center')
                               
        # Change directory button (small, subtle)
        self.change_dir_btn_bg = self.canvas.create_rectangle(450, 255, 550, 275,
                                                            fill='', outline=self.colors['border'], width=1)
        self.change_dir_btn_text = self.canvas.create_text(500, 265,
                                                          text="Change Directory",
                                                          font=self.font_small,
                                                          fill=self.colors['text_secondary'],
                                                          anchor='center')
                               
    def create_main_content(self):
        """Create main content with clean card design like Tune Robotics features"""
        # Main card (like feature cards on the website)
        card_x, card_y = 200, 280
        card_w, card_h = 600, 300
        
        # Draw main card with border (like .feature styling)
        self.canvas.create_rectangle(card_x, card_y, card_x + card_w, card_y + card_h,
                                    fill='', 
                                    outline=self.colors['border'], width=2)
        
        # Card title (like .feature h3)
        self.canvas.create_text(card_x + 32, card_y + 32, 
                               text="Installation Progress", 
                               font=self.font_subtitle,
                               fill=self.colors['text_primary'],
                               anchor='w')
        
        # Clean progress bar without background
        bar_y = card_y + 70
        self.progress_bg = self.canvas.create_rectangle(card_x + 32, bar_y, 
                                                       card_x + card_w - 32, bar_y + 4,
                                                       fill=self.colors['border'], 
                                                       outline='')
        self.progress_fill = self.canvas.create_rectangle(card_x + 32, bar_y, 
                                                         card_x + 32, bar_y + 4,
                                                         fill=self.colors['accent'], 
                                                         outline='')
        
        # Progress text (like .feature p)
        self.progress_text_id = self.canvas.create_text(card_x + 32, card_y + 90, 
                                                       text="Ready to begin installation", 
                                                       font=self.font_body,
                                                       fill=self.colors['text_secondary'],
                                                       anchor='w')
        
        # Installation steps as a simple list (like .feature ul)
        steps_y = card_y + 120
        self.step_indicators = []
        step_names = [
            "• System prerequisites", "• Repository cloning", "• Environment setup", "• Dependencies",
            "• LeRobot installation", "• Dynamixel SDK", "• System packages", "• Verification"
        ]
        
        # Create step list in two columns
        col1_x = card_x + 32
        col2_x = card_x + card_w // 2 + 16
        
        for i, step_name in enumerate(step_names):
            if i < 4:
                x = col1_x
                y = steps_y + i * 20
            else:
                x = col2_x
                y = steps_y + (i - 4) * 20
            
            # Step text (no circles, just bullet points)
            text = self.canvas.create_text(x, y, 
                                         text=step_name, 
                                         font=self.font_small,
                                         fill=self.colors['text_secondary'],
                                         anchor='w')
            
            # Store dummy circle for compatibility
            self.step_indicators.append((None, text))
            
        # Action buttons
        self.create_buttons(card_x, card_y + card_h - 60)
        
        # Store change directory button coordinates for click detection
        if not hasattr(self, 'button_coords'):
            self.button_coords = {}
        self.button_coords['change_dir'] = (450, 255, 550, 275)
        
    def create_buttons(self, x, y):
        """Create buttons matching Tune Robotics CTA style"""
        # Center buttons horizontally
        total_width = 160 + 20 + 160 + 20 + 120  # button widths + gaps
        start_x = (1000 - total_width) // 2
        btn_h = 44  # Slightly taller like the website buttons
        
        # Start Installation button (like .cta-button)
        btn_w = 160
        self.install_btn_bg = self.canvas.create_rectangle(start_x, y, start_x + btn_w, y + btn_h,
                                                          fill='', 
                                                          outline=self.colors['border'], width=2)
        self.install_btn_text = self.canvas.create_text(start_x + btn_w//2, y + btn_h//2, 
                                                       text="Start Installation", 
                                                       font=self.font_button,
                                                       fill=self.colors['text_primary'],
                                                       anchor='center')
        
        # Configure Motors button (secondary CTA style)
        motor_x = start_x + btn_w + 20
        self.motor_btn_bg = self.canvas.create_rectangle(motor_x, y, motor_x + btn_w, y + btn_h,
                                                        fill='', 
                                                        outline=self.colors['border'], width=2)
        self.motor_btn_text = self.canvas.create_text(motor_x + btn_w//2, y + btn_h//2, 
                                                     text="Find Ports", 
                                                     font=self.font_button,
                                                     fill=self.colors['text_secondary'],
                                                     anchor='center')
        
        # Details toggle button (smaller)
        details_x = motor_x + btn_w + 20
        details_w = 120
        self.details_btn_bg = self.canvas.create_rectangle(details_x, y, details_x + details_w, y + btn_h,
                                                          fill='', 
                                                          outline=self.colors['border'], width=2)
        self.details_btn_text = self.canvas.create_text(details_x + details_w//2, y + btn_h//2, 
                                                       text="Show Details", 
                                                       font=self.font_button,
                                                       fill=self.colors['text_secondary'],
                                                       anchor='center')
        
        # Store button coordinates for click detection
        self.button_coords = {
            'install': (start_x, y, start_x + btn_w, y + btn_h),
            'motor': (motor_x, y, motor_x + btn_w, y + btn_h),
            'details': (details_x, y, details_x + details_w, y + btn_h)
        }
        
    def create_status_section(self):
        """Create clean status section like footer"""
        # Status text (like landing-subtitle)
        self.status_text_id = self.canvas.create_text(500, 600, 
                                                     text="Ready to transform your robotics setup", 
                                                     font=self.font_small,
                                                     fill=self.colors['secondary_text'],
                                                     anchor='center')
        
        # Simple info line
        self.canvas.create_text(500, 620, 
                               text="No dependencies required • One-click installation • Professional setup", 
                               font=self.font_small,
                               fill=self.colors['secondary_text'],
                               anchor='center')
        
    def create_details_overlay(self):
        """Create clean details overlay matching website style"""
        if hasattr(self, 'details_overlay'):
            return
            
        # Dark overlay background
        self.details_overlay = self.canvas.create_rectangle(0, 0, 1000, 650,
                                                           fill=self.colors['background'], 
                                                           stipple='gray75')
        
        # Details card (like feature card)
        card_x, card_y = 150, 100
        card_w, card_h = 700, 450
        
        self.details_card = self.canvas.create_rectangle(card_x, card_y, card_x + card_w, card_y + card_h,
                                                        fill=self.colors['background'], 
                                                        outline=self.colors['border'], width=2)
        
        # Title (like feature h3)
        self.canvas.create_text(card_x + 32, card_y + 32, 
                               text="Installation Details", 
                               font=self.font_subtitle,
                               fill=self.colors['text_primary'],
                               anchor='w')
        
        # Terminal output area (clean styling)
        self.details_text = tk.Text(self.root,
                                   bg=self.colors['background'],
                                   fg=self.colors['text_secondary'],
                                   font=('Roboto Mono', 10),
                                   height=20, width=80,
                                   relief='flat',
                                   borderwidth=0,
                                   insertbackground=self.colors['accent'])
        
        self.details_text_window = self.canvas.create_window(card_x + 32, card_y + 70, 
                                                            window=self.details_text, 
                                                            anchor='nw')
        
        # Close button (CTA style)
        close_x, close_y = card_x + card_w - 90, card_y + card_h - 60
        self.details_close_bg = self.canvas.create_rectangle(close_x, close_y, close_x + 70, close_y + 40,
                                                            fill='', 
                                                            outline=self.colors['border'], width=2)
        self.details_close_text = self.canvas.create_text(close_x + 35, close_y + 20, 
                                                         text="Close", 
                                                         font=self.font_button,
                                                         fill=self.colors['text_primary'],
                                                         anchor='center')
        
        # Add to terminal output
        for line in self.terminal_output:
            self.details_text.insert(tk.END, line + '\n')
        self.details_text.see(tk.END)
        
    def hide_details_overlay(self):
        """Hide the details overlay"""
        if hasattr(self, 'details_overlay'):
            self.canvas.delete(self.details_overlay)
            self.canvas.delete(self.details_card)
            self.canvas.delete(self.details_close_bg)
            self.canvas.delete(self.details_close_text)
            self.canvas.delete(self.details_text_window)
            self.details_text.destroy()
            delattr(self, 'details_overlay')
            
    def on_mouse_motion(self, event):
        """Handle mouse motion for button hover effects"""
        x, y = event.x, event.y
        
        # Check button hover states
        for btn_name, coords in self.button_coords.items():
            if coords[0] <= x <= coords[2] and coords[1] <= y <= coords[3]:
                # Hover effect (like .cta-button:hover)
                if btn_name == 'install':
                    self.canvas.itemconfig(self.install_btn_bg, fill=self.colors['surface'])
                elif btn_name == 'motor':
                    self.canvas.itemconfig(self.motor_btn_bg, fill=self.colors['surface'])
                elif btn_name == 'details':
                    self.canvas.itemconfig(self.details_btn_bg, fill=self.colors['surface'])
                elif btn_name == 'change_dir':
                    self.canvas.itemconfig(self.change_dir_btn_bg, fill=self.colors['surface'])
            else:
                # Reset hover
                if btn_name == 'install':
                    self.canvas.itemconfig(self.install_btn_bg, fill='')
                elif btn_name == 'motor':
                    self.canvas.itemconfig(self.motor_btn_bg, fill='')
                elif btn_name == 'details':
                    self.canvas.itemconfig(self.details_btn_bg, fill='')
                elif btn_name == 'change_dir':
                    self.canvas.itemconfig(self.change_dir_btn_bg, fill='')
    
    def on_canvas_click(self, event):
        """Handle canvas clicks for buttons"""
        x, y = event.x, event.y
        
        # Check button clicks
        for btn_name, coords in self.button_coords.items():
            if coords[0] <= x <= coords[2] and coords[1] <= y <= coords[3]:
                if btn_name == 'install':
                    self.start_installation()
                elif btn_name == 'motor':
                    self.start_motor_configuration()
                elif btn_name == 'details':
                    self.toggle_details()
                elif btn_name == 'change_dir':
                    self.change_installation_directory()
                break
                
        # Check details overlay close button
        if hasattr(self, 'details_overlay'):
            close_coords = self.canvas.coords(self.details_close_bg)
            if len(close_coords) >= 4:
                if close_coords[0] <= x <= close_coords[2] and close_coords[1] <= y <= close_coords[3]:
                    self.toggle_details()
                    
    def toggle_details(self):
        """Toggle the details overlay"""
        if hasattr(self, 'details_overlay'):
            self.hide_details_overlay()
            self.canvas.itemconfig(self.details_btn_text, text="Show Details")
        else:
            self.create_details_overlay()
            self.canvas.itemconfig(self.details_btn_text, text="Hide Details")
            
    def change_installation_directory(self):
        """Allow user to change the installation directory"""
        # Don't allow change during installation
        if self.installation_complete or hasattr(self, 'installation_thread_running'):
            messagebox.showwarning("Installation In Progress", 
                                 "Cannot change directory while installation is in progress.")
            return
            
        # Get current parent directory
        current_parent = os.path.dirname(self.install_dir)
        
        # Open directory chooser
        new_parent = filedialog.askdirectory(
            title="Choose Installation Directory",
            initialdir=current_parent,
            mustexist=True
        )
        
        if new_parent:
            # Update installation directory
            self.install_dir = os.path.join(new_parent, "lerobot")
            
            # Update the display
            self.canvas.itemconfig(self.install_dir_text_id, 
                                 text=f"Installation directory: {self.install_dir}")
            
            self.log(f"Installation directory changed to: {self.install_dir}")
            
            # Show confirmation message
            messagebox.showinfo("Directory Changed", 
                              f"Installation directory updated to:\n{self.install_dir}")
        else:
            self.log("Directory change cancelled by user")
        
    def log(self, message, log_type='info'):
        """Add a message to the hidden log (shown only in details overlay)"""
        timestamp = time.strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        
        # Store in terminal output
        self.terminal_output.append(formatted_message)
        
        # Update details text if overlay is open
        if hasattr(self, 'details_text'):
            self.details_text.insert(tk.END, formatted_message + "\n")
            self.details_text.see(tk.END)
        
        # Keep only last 1000 lines to prevent memory issues
        if len(self.terminal_output) > 1000:
            self.terminal_output = self.terminal_output[-1000:]
        
    def update_progress(self, step, message):
        """Update beautiful progress bar and step indicators"""
        self.current_step = step
        
        # Update progress bar fill
        progress_percent = (step / self.total_steps)
        bar_coords = self.canvas.coords(self.progress_bg)
        if len(bar_coords) >= 4:
            bar_width = bar_coords[2] - bar_coords[0]
            fill_width = bar_width * progress_percent
            self.canvas.coords(self.progress_fill, 
                             bar_coords[0], bar_coords[1], 
                             bar_coords[0] + fill_width, bar_coords[3])
        
        # Update progress text
        self.canvas.itemconfig(self.progress_text_id, text=f"Step {step}/{self.total_steps}: {message}")
        
        # Update step indicators (text color changes)
        for i, (circle, text) in enumerate(self.step_indicators):
            if i < step - 1:
                # Completed step - accent color
                self.canvas.itemconfig(text, fill=self.colors['accent'])
            elif i == step - 1:
                # Current step - bright
                self.canvas.itemconfig(text, fill=self.colors['text_primary'])
            else:
                # Pending step - secondary
                self.canvas.itemconfig(text, fill=self.colors['text_secondary'])
                
        
        if step == self.total_steps:
            self.canvas.itemconfig(self.status_text_id, text="Installation completed successfully")
        else:
            self.canvas.itemconfig(self.status_text_id, text=f"{message}...")
            
        self.root.update_idletasks()
        
    def run_command(self, command, cwd=None, shell=True):
        """Run command and capture output"""
        try:
            self.log(f"Running: {command}")
            
            process = subprocess.Popen(
                command,
                shell=shell,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                cwd=cwd
            )
            
            output_lines = []
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    output_lines.append(output.strip())
                    self.log(output.strip())
                    
            rc = process.poll()
            return rc == 0, '\n'.join(output_lines)
            
        except Exception as e:
            self.log(f"Error running command: {str(e)}")
            return False, str(e)
            
    def check_prerequisites(self):
        """Check if git and conda are installed"""
        self.update_progress(1, "Checking prerequisites...")
        
        # Check git
        if not shutil.which('git'):
            self.log("❌ Git not found. Please install Git first.")
            messagebox.showerror("Prerequisites Missing", 
                               "Git is not installed. Please install Git and try again.")
            return False
        else:
            self.log("✅ Git found")
            
        # Check conda
        if not shutil.which('conda'):
            self.log("❌ Conda not found. Please install Miniconda or Anaconda first.")
            messagebox.showerror("Prerequisites Missing", 
                               "Conda is not installed. Please install Miniconda or Anaconda and try again.")
            return False
        else:
            self.log("✅ Conda found")
            
        return True
        
    def clone_repository(self):
        """Clone LeRobot repository"""
        self.update_progress(2, "Cloning LeRobot repository...")
        
        # Remove existing directory if it exists
        if os.path.exists(self.install_dir):
            self.log(f"Removing existing directory: {self.install_dir}")
            shutil.rmtree(self.install_dir)
            
        # Clone repository
        parent_dir = os.path.dirname(self.install_dir)
        success, output = self.run_command(
            "git clone https://github.com/huggingface/lerobot.git lerobot",
            cwd=parent_dir
        )
        
        if not success:
            self.log("❌ Failed to clone repository")
            return False
            
        self.log("✅ Repository cloned successfully")
        return True
        
    def create_conda_environment(self):
        """Create conda environment with Python 3.10"""
        self.update_progress(3, "Creating conda environment...")
        
        # Remove existing environment if it exists
        self.log("Checking for existing lerobot environment...")
        success, output = self.run_command("conda env list")
        if "lerobot" in output:
            self.log("Removing existing lerobot environment...")
            success, output = self.run_command("conda env remove -n lerobot -y")
            
        # Create new environment
        success, output = self.run_command("conda create -y -n lerobot python=3.10")
        
        if not success:
            self.log("❌ Failed to create conda environment")
            return False
            
        self.log("✅ Conda environment created successfully")
        return True
        
    def install_ffmpeg(self):
        """Install ffmpeg in conda environment"""
        self.update_progress(4, "Installing ffmpeg...")
        
        success, output = self.run_command("conda install -n lerobot ffmpeg -c conda-forge -y")
        
        if not success:
            self.log("❌ Failed to install ffmpeg")
            return False
            
        self.log("✅ ffmpeg installed successfully")
        return True
        
    def install_lerobot(self):
        """Install LeRobot package"""
        self.update_progress(5, "Installing LeRobot package...")
        
        # Get conda environment python path
        if platform.system() == "Windows":
            python_path = f"conda run -n lerobot python"
            pip_path = f"conda run -n lerobot pip"
        else:
            python_path = f"conda run -n lerobot python"
            pip_path = f"conda run -n lerobot pip"
            
        success, output = self.run_command(f"{pip_path} install -e .", cwd=self.install_dir)
        
        if not success:
            self.log("❌ Failed to install LeRobot")
            return False
            
        self.log("✅ LeRobot installed successfully")
        return True
        
    def install_dynamixel(self):
        """Install Dynamixel SDK"""
        self.update_progress(6, "Installing Dynamixel SDK...")
        
        pip_path = f"conda run -n lerobot pip"
        success, output = self.run_command(f'{pip_path} install -e ".[dynamixel]"', cwd=self.install_dir)
        
        if not success:
            self.log("❌ Failed to install Dynamixel SDK")
            return False
            
        self.log("✅ Dynamixel SDK installed successfully")
        return True
        
    def install_additional_dependencies(self):
        """Install additional system dependencies if needed"""
        self.update_progress(7, "Installing additional dependencies...")
        
        system = platform.system()
        if system == "Linux":
            self.log("Installing Linux dependencies...")
            commands = [
                "sudo apt-get update",
                "sudo apt-get install -y cmake build-essential python3-dev pkg-config",
                "sudo apt-get install -y libavformat-dev libavcodec-dev libavdevice-dev",
                "sudo apt-get install -y libavutil-dev libswscale-dev libswresample-dev libavfilter-dev"
            ]
            
            for cmd in commands:
                success, output = self.run_command(cmd)
                if not success:
                    self.log(f"⚠️ Warning: Could not install some dependencies: {cmd}")
                    
        elif system == "Darwin":  # macOS
            self.log("Checking for Homebrew dependencies...")
            if shutil.which('brew'):
                success, output = self.run_command("brew install cmake pkg-config")
                if not success:
                    self.log("⚠️ Warning: Could not install some dependencies via Homebrew")
            else:
                self.log("⚠️ Homebrew not found. Some dependencies may need manual installation.")
                
        else:  # Windows
            self.log("Windows detected. Additional dependencies may need manual installation.")
            
        self.log("✅ Additional dependencies check completed")
        return True
        
    def verify_installation(self):
        """Verify the installation"""
        self.update_progress(8, "Verifying installation...")
        
        python_path = f"conda run -n lerobot python"
        
        # Test import
        success, output = self.run_command(f'{python_path} -c "import lerobot; print(f\'LeRobot version: {{lerobot.__version__}}\')"')
        
        if not success:
            self.log("❌ Installation verification failed")
            return False
            
        self.log("✅ Installation verified successfully")
        return True
        
    def find_ports_interactive(self, arm_type="follower"):
        """Find and store robot arm USB ports - simple workflow"""
        self.log(f"\n🔍 Finding {arm_type} arm USB port...")
        
        if arm_type == "follower":
            self.log("🤖 FOLLOWER ARM PORT DISCOVERY")
            self.log("=" * 35)
            self.log("Instructions:")
            self.log("1. The script will ask you to unplug the FOLLOWER arm")
            self.log("2. Unplug the follower arm when prompted")
            self.log("3. Press Enter")
            self.log("4. Script will output the port name")
        else:  # leader
            self.log("🤖 LEADER ARM PORT DISCOVERY") 
            self.log("=" * 33)
            self.log("Instructions:")
            self.log("1. The script will ask you to unplug the LEADER arm")
            self.log("2. Unplug the leader arm when prompted")
            self.log("3. Press Enter")
            self.log("4. Script will output the port name")
        
        # Try to run the actual find_port.py script
        if self.installation_complete:
            # Check if script exists
            script_path = os.path.join(self.install_dir, "lerobot", "lerobot", "find_port.py")
            if not os.path.exists(script_path):
                self.log(f"❌ Script not found: {script_path}")
                self.log("⚠️ LeRobot installation may be incomplete")
                return False
                
            python_cmd = "conda run -n lerobot python lerobot/find_port.py"
            self.log(f"\nRunning: {python_cmd}")
            self.log("Follow the instructions in the terminal window...")
            
            success, output = self.run_command(python_cmd, cwd=self.install_dir)
            
            if not success:
                self.log(f"❌ Command failed for {arm_type} arm")
                self.log("Error details:")
                self.log(output)
                return False
                
            # Extract port from output
            port = self.extract_port_from_output(output)
            
            if port:
                # Store the port
                if arm_type == "follower":
                    self.follower_port = port
                else:
                    self.leader_port = port
                    
                self.log(f"✅ Found {arm_type} arm port: {port}")
                self.log(f"📍 Remembered {arm_type} port: {port}")
                return True
            else:
                self.log(f"❌ Could not find port name in output for {arm_type} arm")
                self.log("Script output:")
                self.log(output)
                return False
                    
        else:
            # Demo mode - simulate the process
            demo_port = f"/dev/ttyUSB{0 if arm_type == 'follower' else 1}" if platform.system() != "Windows" else f"COM{3 if arm_type == 'follower' else 4}"
            
            if arm_type == "follower":
                self.follower_port = demo_port
            else:
                self.leader_port = demo_port
                
            self.log("⚠️ Demo mode - simulating port discovery")
            self.log(f"📍 Demo {arm_type} port: {demo_port}")
            return True
            
    def extract_port_from_output(self, output):
        """Extract port name from find_port.py script output"""
        import re
        
        # Look for the main output line from find_port.py
        for line in output.split('\n'):
            line = line.strip()
            
            # Look for "The port of this MotorsBus is" pattern
            if "The port of this MotorsBus is" in line:
                # Extract everything after this phrase
                parts = line.split("The port of this MotorsBus is")
                if len(parts) > 1:
                    port = parts[1].strip()
                    # Remove any trailing punctuation or quotes
                    port = port.strip('.,!"\' ')
                    if port and (port.startswith('/dev/') or port.startswith('COM')):
                        return port
        
        # Fallback: Look for any port patterns in the output
        # Unix-style ports (like /dev/ttyUSB0, /dev/ttyACM0)
        unix_ports = re.findall(r'/dev/tty[A-Z]+\d+', output)
        if unix_ports:
            return unix_ports[-1]  # Return the last found port
            
        # Windows-style ports (like COM3, COM4)
        windows_ports = re.findall(r'COM\d+', output)
        if windows_ports:
            return windows_ports[-1]  # Return the last found port
            
        return None
        
    def show_motor_step(self, step_title, step_description, step_action):
        """Show motor configuration step in the main UI"""
        # Update the main UI to show motor configuration steps
        self.canvas.itemconfig(self.progress_text_id, text=step_title)
        
        # Update status text
        self.canvas.itemconfig(self.status_text_id, text=step_description)
        
        # Log the step
        self.log(f"\n{step_title}")
        self.log("=" * len(step_title))
        self.log(step_description)
        self.log(f"\nNext: {step_action}")
        
        return True
        
    def configure_follower_arm(self):
        """Find and store follower arm USB port"""
        # Step 1: Setup
        self.show_motor_step(
            "Finding Follower Arm", 
            "Connect both arms via USB and power them on",
            "Running port discovery script"
        )
        
        time.sleep(1)  # Brief pause for user to read
        
        # Step 2: Run port discovery
        self.show_motor_step(
            "Scanning Follower Port",
            "Running: python lerobot/find_port.py",
            "Follow terminal instructions to unplug follower arm"
        )
        
        if not self.find_ports_interactive("follower"):
            self.show_motor_step(
                "Follower Port Failed",
                "Could not identify follower arm port",
                "Check terminal output and ensure arm is connected"
            )
            return False
            
        # Step 3: Completion
        self.show_motor_step(
            "Follower Port Found",
            f"Follower arm port: {self.follower_port}",
            "Proceeding to find leader arm port"
        )
        
        time.sleep(1)  # Brief pause
        return True
        
    def configure_leader_arm(self):
        """Find and store leader arm USB port"""
        # Step 1: Setup
        self.show_motor_step(
            "Finding Leader Arm",
            "Both arms should still be connected and powered",
            "Running port discovery for leader arm"
        )
        
        time.sleep(1)  # Brief pause
        
        # Step 2: Run port discovery
        self.show_motor_step(
            "Scanning Leader Port",
            "Running: python lerobot/find_port.py",
            "Follow terminal instructions to unplug leader arm"
        )
        
        if not self.find_ports_interactive("leader"):
            self.show_motor_step(
                "Leader Port Failed",
                "Could not identify leader arm port", 
                "Check terminal output and ensure arm is connected"
            )
            return False
            
        # Step 3: Final completion
        self.show_motor_step(
            "Ports Discovery Complete",
            f"Leader: {self.leader_port} | Follower: {self.follower_port}",
            "Port information saved - Ready to use LeRobot"
        )
        
        time.sleep(1)  # Brief pause
        return True
        
    def motor_configuration_thread(self):
        """Main port discovery thread integrated into UI"""
        try:
            # Update motor button visual state (disabled style)
            self.canvas.itemconfig(self.motor_btn_bg, fill=self.colors['border'])
            self.canvas.itemconfig(self.motor_btn_text, text="Finding Ports...", fill=self.colors['text_secondary'])
            
            # Initial setup screen
            self.show_motor_step(
                "Port Discovery Starting",
                "Finding USB ports for leader and follower arms",
                "Beginning port discovery process"
            )
            
            time.sleep(1)
            
            # Check if installation was completed
            if not self.installation_complete:
                self.log("⚠️ Installation not completed - running in demo mode")
                self.log("📍 In real usage, complete installation first before finding ports")
                
            # Check if LeRobot is properly installed for port discovery
            if self.installation_complete:
                script_path = os.path.join(self.install_dir, "lerobot", "lerobot", "find_port.py")
                if os.path.exists(script_path):
                    self.log("✅ LeRobot installation found - using real port discovery")
                else:
                    self.log("⚠️ find_port.py script not found - using demo mode")
            else:
                self.log("⚠️ Running port discovery in demo mode")
                
            # Step 1: Find follower arm port
            if not self.configure_follower_arm():
                self.show_motor_step(
                    "Port Discovery Failed",
                    "Follower arm port discovery failed",
                    "Check terminal output for details"
                )
                return
                
            # Step 2: Find leader arm port
            if not self.configure_leader_arm():
                self.show_motor_step(
                    "Port Discovery Failed", 
                    "Leader arm port discovery failed",
                    "Check terminal output for details"
                )
                return
                
            # Port discovery successful
            self.motor_configuration_complete = True
            
            # Log completion with port summary
            self.log("\n🎉 PORT DISCOVERY COMPLETED SUCCESSFULLY!")
            self.log("=" * 60)
            self.log("Robot arm USB ports have been identified:")
            self.log(f"📍 Leader arm port:   {self.leader_port}")
            self.log(f"📍 Follower arm port: {self.follower_port}")
            self.log("")
            self.log("You can now use these ports in your LeRobot configuration.")
            
        except Exception as e:
            self.show_motor_step(
                "Port Discovery Error",
                f"Port discovery failed: {str(e)}",
                "Check terminal output for details"
            )
            
        finally:
            # Reset motor button visual state
            self.canvas.itemconfig(self.motor_btn_bg, fill='')
            self.canvas.itemconfig(self.motor_btn_text, text="Find Ports", fill=self.colors['text_secondary'])
            
    def start_motor_configuration(self):
        """Start the port discovery process in a separate thread"""
        if self.motor_configuration_complete:
            response = messagebox.askyesno("Find Ports Again", 
                                         f"Ports already found:\nLeader: {self.leader_port}\nFollower: {self.follower_port}\n\nDo you want to find them again?")
            if not response:
                return
                
        # Clear terminal output for port discovery
        self.terminal_output = []
        if hasattr(self, 'details_text'):
            self.details_text.delete(1.0, tk.END)
        self.motor_configuration_complete = False
        
        # Reset stored ports
        self.leader_port = None
        self.follower_port = None
        
        # Start port discovery in separate thread to keep UI responsive
        threading.Thread(target=self.motor_configuration_thread, daemon=True).start()
        
    def installation_thread(self):
        """Main installation thread"""
        try:
            # Mark installation as running
            self.installation_thread_running = True
            
            # Update install button visual state (disabled style)
            self.canvas.itemconfig(self.install_btn_bg, fill=self.colors['border'])
            self.canvas.itemconfig(self.install_btn_text, text="Installing...", fill=self.colors['text_secondary'])
            
            steps = [
                self.check_prerequisites,
                self.clone_repository, 
                self.create_conda_environment,
                self.install_ffmpeg,
                self.install_lerobot,
                self.install_dynamixel,
                self.install_additional_dependencies,
                self.verify_installation
            ]
            
            for step_func in steps:
                if not step_func():
                    self.log("\n❌ Installation failed!")
                    messagebox.showerror("Installation Failed", 
                                       "Installation failed. Please check the log for details.")
                    return
                    
            # Installation successful
            self.installation_complete = True
            self.update_progress(self.total_steps, "Installation completed!")
            
            # Enable motor configuration button (make it primary)
            self.canvas.itemconfig(self.motor_btn_text, fill=self.colors['text_primary'])
            
            self.log("\n🎉 Installation completed successfully!")
            
            success_message = f"""LeRobot has been installed successfully!

Installation directory: {self.install_dir}

To use LeRobot:
1. Open a terminal
2. Run: conda activate lerobot
3. Navigate to: cd {self.install_dir}
4. Start using LeRobot!

Next step: Click "Find Ports" to identify your robot arm USB connections.

You can now find robot arm ports or close this installer."""

            messagebox.showinfo("🎉 Installation Complete", success_message)
            
        except Exception as e:
            self.log(f"\n❌ Unexpected error: {str(e)}")
            messagebox.showerror("Installation Error", f"An unexpected error occurred: {str(e)}")
            
        finally:
            # Mark installation as no longer running
            self.installation_thread_running = False
            
            if self.installation_complete:
                # Reset install button (secondary style)
                self.canvas.itemconfig(self.install_btn_bg, fill='')
                self.canvas.itemconfig(self.install_btn_text, text="Reinstall", fill=self.colors['text_secondary'])
            else:
                # Reset install button (primary style)
                self.canvas.itemconfig(self.install_btn_bg, fill='')
                self.canvas.itemconfig(self.install_btn_text, text="Start Installation", fill=self.colors['text_primary'])
            
    def start_installation(self):
        """Start the installation process in a separate thread"""
        if self.installation_complete:
            response = messagebox.askyesno("Reinstall", 
                                         "LeRobot is already installed. Do you want to reinstall?")
            if not response:
                return
                
        # Clear terminal output
        self.terminal_output = []
        if hasattr(self, 'details_text'):
            self.details_text.delete(1.0, tk.END)
        self.installation_complete = False
        
        # Reset UI state
        self.canvas.itemconfig(self.status_text_id, text="Starting installation process...")
        
        # Reset step indicators
        for circle, text in self.step_indicators:
            self.canvas.itemconfig(text, fill=self.colors['text_secondary'])
        
        # Start installation in separate thread to keep UI responsive
        threading.Thread(target=self.installation_thread, daemon=True).start()

def main():
    # Create the beautiful main window
    root = tk.Tk()
    root.title("LeRobot Installer - Tune Robotics")
    
    # Create installer app
    app = LeRobotInstaller(root)
    
    # Center window on screen
    root.update_idletasks()
    width = 1000
    height = 650
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    # Start the modern GUI
    root.mainloop()

if __name__ == "__main__":
    main() 
    