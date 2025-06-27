import tkinter as tk
from tkinter import font
from PIL import ImageTk, Image
import os
import time
import threading

class WelcomeScreen:
    def __init__(self, root, selection_callback):
        self.root = root
        self.selection_callback = selection_callback
        
        self.colors = {
            'background': '#000b2a', 'text_primary': '#e0e8f2',
            'text_secondary': '#8c9bb3', 'accent': '#3025ff',
            'surface': '#0d193b', 'border': '#1a274c',
            'hover': '#2a3f6b'
        }
        
        # Typing animation variables
        self.typing_phrases = [
            "Start Now",
            "Begin Your Journey", 
            "Power Up",
            "Transform Ideas"
        ]
        self.current_phrase_index = 0
        self.current_text = ""
        self.typing_forward = True
        self.typing_paused = False
        self.subtitle_text_id = None
        self.cursor_visible = True
        
        # Button animation variables
        self.robot_image_ids = {}
        self.robot_original_sizes = {}
        self.robot_scale_factors = {}
        self.animation_active = {}
        
        self.setup_fonts()
        self.create_widgets()
        self.start_typing_animation()
        self.animate_cursor()

    def setup_fonts(self):
        font_family = "Roboto Mono"
        try:
            font.nametofont(font_family)
        except tk.TclError:
            font_family = "Courier" 

        self.font_logo = font.Font(family=font_family, size=18, weight='bold')
        self.font_title = font.Font(family=font_family, size=48, weight='bold')
        self.font_subtitle = font.Font(family=font_family, size=18, weight='normal')
        self.font_robot_choice = font.Font(family=font_family, size=16, weight='bold')
        self.font_description = font.Font(family=font_family, size=16, weight='normal')

    def create_widgets(self):
        self.root.title("Tune Robotics")
        self.root.geometry("1200x750")
        
        self.canvas = tk.Canvas(self.root, bg=self.colors['background'], highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)

        # Logo with improved positioning
        logo_path = os.path.join("photos", "logo.png")
        if os.path.exists(logo_path):
            self.logo_img = Image.open(logo_path)
            self.logo_img.thumbnail((250, 80))
            self.logo_photo = ImageTk.PhotoImage(self.logo_img)
            self.canvas.create_image(60, 50, image=self.logo_photo, anchor='nw')
        else:
            self.canvas.create_text(60, 50, text="Tune Robotics", font=self.font_logo, fill=self.colors['text_primary'], anchor='nw')

        # Enhanced main title with better spacing
        self.canvas.create_text(600, 150, text="Choose Your Robot", font=self.font_title, fill=self.colors['text_primary'], anchor='center')
        
        # Animated subtitle with cursor
        self.subtitle_text_id = self.canvas.create_text(600, 210, text="", font=self.font_subtitle, fill=self.colors['accent'], anchor='center')
        self.cursor_id = self.canvas.create_text(600, 210, text="|", font=self.font_subtitle, fill=self.colors['accent'], anchor='w')
        
        # Descriptive text
        self.canvas.create_text(600, 270, text="Choose your robot platform to start setup and unlock full control.", 
                               font=self.font_description, fill=self.colors['text_secondary'], anchor='center')

        # Robot selection cards
        robot_cards = {
            'koch': {
                'text': "Koch V1-1", 
                'pos': (300, 350, 600, 620), 
                'img_path': "photos/bkoch-v1.png"
            },
            'so101': {
                'text': "So-101", 
                'pos': (700, 350, 1000, 620), 
                'img_path': "photos/so101.png"
            },
        }
        
        self.robot_button_coords = {}
        self.robot_images = {}

        for name, card_data in robot_cards.items():
            x1, y1, x2, y2 = card_data['pos']
            
            # Center position for the robot
            center_x = x1 + (x2-x1)/2
            center_y = y1 + 100
            title_y_pos = center_y + 120
            hint_y_pos = title_y_pos + 40

            # Load and display robot images as buttons
            if card_data['img_path'] and os.path.exists(card_data['img_path']):
                try:
                    img = Image.open(card_data['img_path'])
                    img.thumbnail((200, 200))  # Larger size for button
                    self.robot_images[name] = ImageTk.PhotoImage(img)
                    img_id = self.canvas.create_image(center_x, center_y, image=self.robot_images[name], anchor='center', tags=f"robot_img_{name}")
                    
                    # Store for animations
                    self.robot_image_ids[name] = img_id
                    self.robot_original_sizes[name] = (200, 200)
                    self.robot_scale_factors[name] = 1.0
                    self.animation_active[name] = False
                    
                    # Store image bounds for click detection
                    img_bounds = self.canvas.bbox(img_id)
                    if img_bounds:
                        self.robot_button_coords[name] = img_bounds
                    else:
                        # Fallback bounds
                        self.robot_button_coords[name] = (center_x-100, center_y-100, center_x+100, center_y+100)
                except Exception as e:
                    print(f"Error loading image {card_data['img_path']}: {e}")
                    # Fallback placeholder as button
                    placeholder_size = 80
                    text_id = self.canvas.create_text(center_x, center_y, text="📷", 
                                          font=font.Font(size=placeholder_size), fill=self.colors['text_secondary'], 
                                          anchor='center', tags=f"robot_img_{name}")
                    self.robot_image_ids[name] = text_id
                    self.robot_original_sizes[name] = (placeholder_size, placeholder_size)
                    self.robot_scale_factors[name] = 1.0
                    self.animation_active[name] = False
                    self.robot_button_coords[name] = (center_x-placeholder_size, center_y-placeholder_size, 
                                                    center_x+placeholder_size, center_y+placeholder_size)
            else:
                # Robot icon as button
                robot_icon = "🦾"  # So-101 uses robotic arm emoji
                icon_size = 80
                icon_id = self.canvas.create_text(center_x, center_y, text=robot_icon, 
                                      font=font.Font(size=icon_size), fill=self.colors['accent'], 
                                      anchor='center', tags=f"robot_img_{name}")
                self.robot_image_ids[name] = icon_id
                self.robot_original_sizes[name] = (icon_size, icon_size)
                self.robot_scale_factors[name] = 1.0
                self.animation_active[name] = False
                self.robot_button_coords[name] = (center_x-icon_size, center_y-icon_size, 
                                                center_x+icon_size, center_y+icon_size)
            
            # Robot title below the image
            self.canvas.create_text(center_x, title_y_pos, text=card_data['text'], 
                                  font=self.font_robot_choice, fill=self.colors['text_primary'], anchor='center')
            
            # Selection hint
            self.canvas.create_text(center_x, hint_y_pos, text="Click to Select", 
                                  font=font.Font(family="Roboto Mono", size=10), 
                                  fill=self.colors['text_secondary'], anchor='center', tags=f"select_hint_{name}")
        
        # Footer with better styling
        self.canvas.create_text(600, 700, text="Just tell your robot what you want it to do - it'll do it with Tune", 
                               font=font.Font(family="Roboto Mono", size=10), 
                               fill=self.colors['text_secondary'], anchor='center')
        
        self.canvas.bind('<Button-1>', self._on_canvas_click)
        self.canvas.bind('<Motion>', self._on_mouse_motion)



    def start_typing_animation(self):
        """Starts the typing animation for subtitles."""
        self.animate_typing()

    def animate_typing(self):
        """Handles the typing animation logic."""
        if not hasattr(self, 'canvas') or self.subtitle_text_id is None:
            return
            
        current_phrase = self.typing_phrases[self.current_phrase_index]
        
        if self.typing_forward:
            if len(self.current_text) < len(current_phrase):
                self.current_text += current_phrase[len(self.current_text)]
                self.update_subtitle_text()
                self.root.after(100, self.animate_typing)  # Typing speed
            else:
                # Pause at the end of the phrase
                self.typing_paused = True
                self.root.after(2000, self.start_erasing)  # Pause duration
        else:
            if len(self.current_text) > 0:
                self.current_text = self.current_text[:-1]
                self.update_subtitle_text()
                self.root.after(50, self.animate_typing)  # Erasing speed
            else:
                # Move to next phrase
                self.current_phrase_index = (self.current_phrase_index + 1) % len(self.typing_phrases)
                self.typing_forward = True
                self.root.after(500, self.animate_typing)  # Pause before next phrase

    def start_erasing(self):
        """Starts erasing the current text."""
        self.typing_paused = False
        self.typing_forward = False
        self.animate_typing()

    def update_subtitle_text(self):
        """Updates the subtitle text on the canvas."""
        if self.subtitle_text_id:
            self.canvas.itemconfig(self.subtitle_text_id, text=self.current_text)
            # Update cursor position
            bbox = self.canvas.bbox(self.subtitle_text_id)
            if bbox:
                cursor_x = bbox[2] + 5  # Position cursor after text
                self.canvas.coords(self.cursor_id, cursor_x, 210)

    def animate_cursor(self):
        """Animates the blinking cursor."""
        if not hasattr(self, 'canvas') or self.cursor_id is None:
            return
            
        if self.cursor_visible:
            self.canvas.itemconfig(self.cursor_id, fill=self.colors['accent'])
        else:
            self.canvas.itemconfig(self.cursor_id, fill=self.colors['background'])
        
        self.cursor_visible = not self.cursor_visible
        self.root.after(530, self.animate_cursor)  # Cursor blink speed

    def animate_robot_scale(self, robot_name, target_scale, duration=200):
        """Smoothly animate robot scaling."""
        if robot_name not in self.robot_image_ids or self.animation_active.get(robot_name, False):
            return
            
        self.animation_active[robot_name] = True
        start_scale = self.robot_scale_factors[robot_name]
        steps = 10
        scale_diff = target_scale - start_scale
        step_size = scale_diff / steps
        step_duration = duration // steps
        
        def animate_step(step):
            if step >= steps:
                self.robot_scale_factors[robot_name] = target_scale
                self.animation_active[robot_name] = False
                return
                
            current_scale = start_scale + (step_size * step)
            self.robot_scale_factors[robot_name] = current_scale
            
            # Apply visual scaling effect by adjusting the image
            img_id = self.robot_image_ids[robot_name]
            
            # For text-based robots (emojis), change font size
            item_type = self.canvas.type(img_id)
            if item_type == "text":
                original_size = self.robot_original_sizes[robot_name][0]
                new_size = int(original_size * current_scale)
                current_font = self.canvas.itemcget(img_id, "font")
                new_font = font.Font(size=new_size)
                self.canvas.itemconfig(img_id, font=new_font)
            
            self.root.after(step_duration, lambda: animate_step(step + 1))
        
        animate_step(0)

    def animate_robot_bounce(self, robot_name):
        """Create a bounce effect when robot is clicked."""
        if robot_name not in self.robot_image_ids:
            return
            
        # Quick scale down then back up
        self.animate_robot_scale(robot_name, 0.85, 100)
        self.root.after(120, lambda: self.animate_robot_scale(robot_name, 1.1, 100))
        self.root.after(250, lambda: self.animate_robot_scale(robot_name, 1.0, 100))

    def _on_canvas_click(self, event):
        for name, (x1, y1, x2, y2) in self.robot_button_coords.items():
            if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                # Add click effect - bounce animation and highlight
                self.animate_robot_bounce(name)
                self.canvas.itemconfig(f"select_hint_{name}", fill=self.colors['accent'])
                self.root.after(150, lambda n=name: self._reset_selection_hint(n))
                self.root.after(400, lambda n=name: self.selection_callback(n))  # Wait for bounce to finish
                return

    def _reset_selection_hint(self, name):
        """Resets selection hint color after click effect."""
        self.canvas.itemconfig(f"select_hint_{name}", fill=self.colors['text_secondary'])

    def _on_mouse_motion(self, event):
        hover_found = False
        for name, (x1, y1, x2, y2) in self.robot_button_coords.items():
            if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                # Highlight the selection hint on hover
                self.canvas.itemconfig(f"select_hint_{name}", fill=self.colors['accent'])
                # Scale up animation on hover
                if self.robot_scale_factors[name] < 1.1:
                    self.animate_robot_scale(name, 1.1, 150)
                # Change cursor to indicate clickable
                self.canvas.config(cursor="hand2")
                hover_found = True
            else:
                self.canvas.itemconfig(f"select_hint_{name}", fill=self.colors['text_secondary'])
                # Scale back down when not hovering
                if self.robot_scale_factors[name] > 1.0:
                    self.animate_robot_scale(name, 1.0, 150)
        
        if not hover_found:
            self.canvas.config(cursor="")

    def destroy(self):
        # Stop animations before destroying
        if hasattr(self, 'root'):
            self.root.after_cancel  
        self.root.destroy() 