import tkinter as tk
from tkinter import font, ttk
from PIL import ImageTk, Image
import os

class InstallerUI:

    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        
        self.colors = {
            'background': '#000b2a', 'text_primary': '#e0e8f2',
            'text_secondary': '#8c9bb3', 'accent': '#e0e8f2',
            'surface': '#0d193b', 'border': '#1a274c',
            'success': '#4ade80', 'warning': '#fbbf24',
            'error': '#ef4444', 'hover': '#2a3f6b'
        }
        
        self.root.configure(bg=self.colors['background'])
        
        self.setup_fonts()
        self.setup_ui()

    def setup_fonts(self):
        """Setup fonts using Roboto Mono (Google Fonts) with fallbacks"""
        # Check for available monospace fonts with preference for Roboto Mono
        font_families = ["Roboto Mono", "Source Code Pro", "Monaco", "Menlo", "Consolas", "Courier New", "monospace"]
        selected_family = "Courier"  # Default fallback
        
        # Test each font family to see if it's available
        for font_family in font_families:
            try:
                test_font = font.Font(family=font_family, size=12)
                # If we can create the font successfully, use this family
                selected_family = font_family
                break
            except tk.TclError:
                continue
        
        try:
            self.font_logo = font.Font(family=selected_family, size=15, weight='bold')
            self.font_super_title = font.Font(family=selected_family, size=36, weight='bold')
            self.font_title = font.Font(family=selected_family, size=22, weight='bold')
            self.font_subtitle = font.Font(family=selected_family, size=13, weight='normal')
            self.font_body = font.Font(family=selected_family, size=12, weight='normal')
            self.font_small = font.Font(family=selected_family, size=10, weight='normal')
            self.font_button = font.Font(family=selected_family, size=13, weight='bold')
            
            print(f"Using font family: {selected_family}")
        except tk.TclError as e:
            print(f"Font setup error: {e}, falling back to system defaults")
            # Ultimate fallback to system defaults
            self.font_logo = font.Font(size=15, weight='bold')
            self.font_super_title = font.Font(size=36, weight='bold')
            self.font_title = font.Font(size=22, weight='bold')
            self.font_subtitle = font.Font(size=13, weight='normal')
            self.font_body = font.Font(size=12, weight='normal')
            self.font_small = font.Font(size=10, weight='normal')
            self.font_button = font.Font(size=13, weight='bold')

    def setup_ui(self):
        """Sets up the main UI layout and widgets."""
        self.canvas = tk.Canvas(self.root, bg=self.colors['background'], highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)

        self._create_header()
        self._create_hero_section()
        
        self.main_card = tk.Frame(self.canvas, bg=self.colors['background'], highlightbackground=self.colors['border'], highlightthickness=2)
        
        self._create_installation_view()
        self._create_port_finding_view()
        
        self.canvas.create_window(500, 430, window=self.main_card, anchor='center')
        
        self._create_main_buttons()
        self._create_status_section()

        self.canvas.bind('<Button-1>', self._on_canvas_click)
        self.canvas.bind('<Motion>', self._on_mouse_motion)
        
        # Start in installation view
        self.show_installation_view()

    def _create_header(self):
        # Display Logo
        logo_path = os.path.join("photos", "logo.png")
        if os.path.exists(logo_path):
            self.logo_img = Image.open(logo_path)
            self.logo_img.thumbnail((150, 50))
            self.logo_photo = ImageTk.PhotoImage(self.logo_img)
            self.canvas.create_image(32, 32, image=self.logo_photo, anchor='nw')
        else:
            self.canvas.create_text(32, 32, text="LeRobot Installer", font=self.font_logo, fill=self.colors['text_primary'], anchor='w')

    def _create_hero_section(self):
        self.canvas.create_text(500, 140, text="LeRobot", font=self.font_super_title, fill=self.colors['text_primary'], anchor='center')
        self.canvas.create_text(500, 180, text="Automated Installer", font=self.font_title, fill=self.colors['text_secondary'], anchor='center')
        self.install_dir_text_id = self.canvas.create_text(500, 220, text=f"Directory: {self.controller.install_dir}", font=self.font_small, fill=self.colors['text_secondary'], anchor='center')
        self.change_dir_btn_bg = self.canvas.create_rectangle(450, 235, 550, 255, fill='', outline=self.colors['border'], width=1)
        self.change_dir_btn_text = self.canvas.create_text(500, 245, text="Change", font=self.font_small, fill=self.colors['text_secondary'], anchor='center')

    def _create_installation_view(self):
        self.install_view_frame = tk.Frame(self.main_card, bg=self.colors['background'])
        
        tk.Label(self.install_view_frame, text="Installation Progress", font=self.font_subtitle, fg=self.colors['text_primary'], bg=self.colors['background']).pack(pady=(10, 20))

        progress_frame = tk.Frame(self.install_view_frame, bg=self.colors['background'])
        self.progress_bar = ttk.Progressbar(progress_frame, orient='horizontal', length=400, mode='determinate')
        self.progress_bar.pack(pady=5)
        self.progress_label = tk.Label(progress_frame, text="Ready to begin.", font=self.font_body, fg=self.colors['text_secondary'], bg=self.colors['background'])
        self.progress_label.pack()
        progress_frame.pack(pady=20, padx=30)

    def _create_port_finding_view(self):
        self.port_view_frame = tk.Frame(self.main_card, bg=self.colors['background'])

        self.port_instructions_label = tk.Label(self.port_view_frame, text="Port detection", font=self.font_subtitle, wraplength=500, justify='center', fg=self.colors['text_primary'], bg=self.colors['background'])
        self.port_instructions_label.pack(pady=20, padx=20)

        self.port_finder_canvas = tk.Canvas(self.port_view_frame, width=220, height=44, bg=self.colors['background'], highlightthickness=0)
        button_pos = (0, 0, 220, 44)
        bg = self.port_finder_canvas.create_rectangle(button_pos, fill=self.colors['surface'], outline='')
        text = self.port_finder_canvas.create_text(110, 22, text="", font=self.font_button, fill=self.colors['text_primary'], anchor='center')
        self.port_finder_button_widget = {'canvas': self.port_finder_canvas, 'bg': bg, 'text': text}
        self.port_finder_canvas.pack(pady=20)
        self.port_finder_canvas.bind('<Enter>', self._on_port_finder_button_enter)
        self.port_finder_canvas.bind('<Leave>', self._on_port_finder_button_leave)
        
        ports_frame = tk.Frame(self.port_view_frame, bg=self.colors['background'])
        self.follower_port_label = tk.Label(ports_frame, text="Follower Port: Not Found", font=self.font_small, fg=self.colors['text_secondary'], bg=self.colors['background'])
        self.follower_port_label.pack(side='left', padx=20)
        self.leader_port_label = tk.Label(ports_frame, text="Leader Port: Not Found", font=self.font_small, fg=self.colors['text_secondary'], bg=self.colors['background'])
        self.leader_port_label.pack(side='left', padx=20)
        ports_frame.pack(pady=10)

    def show_installation_view(self):
        self.port_view_frame.pack_forget()
        self.install_view_frame.pack(fill='both', expand=True, padx=20, pady=20)

    def show_port_finding_view(self):
        self.install_view_frame.pack_forget()
        self.port_view_frame.pack(fill='both', expand=True, padx=20, pady=20)

    def update_port_finder_instructions(self, text):
        self.port_instructions_label.config(text=text)

    def set_port_finder_button(self, text, command=None, state='normal'):
        widget_info = self.port_finder_button_widget
        canvas = widget_info['canvas']
        text_widget = widget_info['text']
        canvas.itemconfig(text_widget, text=text)
        if state == 'disabled':
            canvas.itemconfig(text_widget, fill=self.colors['text_secondary'])
            canvas.unbind('<Button-1>')
        else:
            canvas.itemconfig(text_widget, fill=self.colors['text_primary'])
            final_command = command or self.controller.handle_port_finder_action_click
            canvas.bind('<Button-1>', lambda e: final_command())

    def update_follower_port_display(self, port):
        self.follower_port_label.config(text=f"Follower Port: {port}", fg=self.colors['success'])

    def update_leader_port_display(self, port):
        self.leader_port_label.config(text=f"Leader Port: {port}", fg=self.colors['success'])

    def _on_port_finder_button_enter(self, event):
        if self.port_finder_canvas.itemcget(self.port_finder_button_widget['text'], 'fill') == self.colors['text_primary']:
            self.port_finder_canvas.itemconfig(self.port_finder_button_widget['bg'], fill=self.colors['hover'])

    def _on_port_finder_button_leave(self, event):
        self.port_finder_canvas.itemconfig(self.port_finder_button_widget['bg'], fill=self.colors['surface'])

    def _create_main_buttons(self):
        y, h, w = 530, 44, 130
        total_width = w * 3
        start_x = (1000 - total_width) // 2

        buttons = {
            'install': {'text': "Install", 'pos': (start_x, y, start_x + w, y + h)},
            'motor': {'text': " Find Ports", 'pos': (start_x + w, y, start_x + w * 2, y + h)},
            'setup': {'text': "Set Up Motors", 'pos': (start_x + w * 2, y, start_x + w * 3, y + h)},
        }
        
        self.button_widgets = {}
        self.button_coords = {}

        for name, B in buttons.items():
            bg = self.canvas.create_rectangle(B['pos'], fill=self.colors['surface'], outline='', width=0)
            text = self.canvas.create_text(B['pos'][0] + w/2, y + h/2, text=B['text'], font=self.font_button, fill=self.colors['text_secondary'], anchor='center')
            self.button_widgets[name] = {'bg': bg, 'text': text}
            self.button_coords[name] = B['pos']

        self.canvas.create_line(start_x + w, y + 10, start_x + w, y + h - 10, fill=self.colors['border'])
        self.canvas.create_line(start_x + w * 2, y + 10, start_x + w * 2, y + h - 10, fill=self.colors['border'])
            
        self.set_button_state('motor', 'Find Ports', 'text_secondary')
        self.set_button_state('setup', ' Set Up Motors', 'text_secondary')

    def _create_status_section(self):
        self.status_text_id = self.canvas.create_text(500, 600, text="Welcome to the LeRobot Installer", font=self.font_small, fill=self.colors['text_secondary'], anchor='center')

    def _on_mouse_motion(self, event):
        for name, (x1, y1, x2, y2) in self.button_coords.items():
            widget = self.button_widgets[name]
            current_fill = self.canvas.itemcget(widget['text'], 'fill')
            if current_fill == self.colors['text_primary']:
                fill_color = self.colors['hover'] if x1 <= event.x <= x2 and y1 <= event.y <= y2 else self.colors['surface']
                self.canvas.itemconfig(widget['bg'], fill=fill_color)
            else:
                self.canvas.itemconfig(widget['bg'], fill=self.colors['surface'])
            
        (x1, y1, x2, y2) = (450, 235, 550, 255)
        fill_color = self.colors['hover'] if x1 <= event.x <= x2 and y1 <= event.y <= y2 else ''
        self.canvas.itemconfig(self.change_dir_btn_bg, fill=fill_color)

    def _on_canvas_click(self, event):
        for name, (x1, y1, x2, y2) in self.button_coords.items():
            if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                getattr(self.controller, f"handle_{name}_click", lambda: None)()
                return
        
        (x1, y1, x2, y2) = (450, 235, 550, 255)
        if x1 <= event.x <= x2 and y1 <= event.y <= y2:
            self.controller.handle_change_dir_click()

    def update_progress(self, step, total_steps, message):
        if total_steps > 0:
            self.progress_bar['value'] = (step / total_steps) * 100
        else:
            self.progress_bar['value'] = 0
        self.progress_label.config(text=message)
        self.root.update_idletasks()

    def update_status_text(self, message):
        self.canvas.itemconfig(self.status_text_id, text=message)
        self.root.update_idletasks()

    def set_button_state(self, name, text, color):
        if name in self.button_widgets:
            widget = self.button_widgets[name]
            self.canvas.itemconfig(widget['text'], text=text, fill=self.colors.get(color, self.colors['text_secondary']))

    def update_install_dir_text(self, new_dir):
        self.canvas.itemconfig(self.install_dir_text_id, text=f"Directory: {new_dir}") 