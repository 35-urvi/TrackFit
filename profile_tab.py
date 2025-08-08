import tkinter as tk
from tkinter import ttk, messagebox, font
import sqlite3
from PIL import Image, ImageTk
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class ProfileTab:
    def __init__(self, parent, bg_color, username):
        self.parent = parent
        self.bg_color = bg_color
        self.username = username
        
        # Set up fonts
        self.title_font = font.Font(family="Helvetica", size=14, weight="bold")
        self.header_font = font.Font(family="Helvetica", size=12, weight="bold")
        self.normal_font = font.Font(family="Helvetica", size=10)
        
        # Create main frame
        self.main_frame = tk.Frame(parent, bg=self.bg_color)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create two columns: input form and profile display
        self.form_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        self.form_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.display_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        self.display_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create profile input form
        self.create_input_form()
        
        # Create profile display area
        self.create_display_area()
        
        # Load existing profile if any
        self.load_profile()
    
    def create_input_form(self):
        # Title
        title_label = tk.Label(self.form_frame, text="Personal Information", 
                             font=self.title_font, bg=self.bg_color)
        title_label.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))
        
        # Form fields
        fields = [
            ("Name:", "name"),
            ("Age:", "age"),
            ("Gender:", "gender"),
            ("Height (cm):", "height"),
            ("Weight (kg):", "weight"),
            ("Daily Workout Goal (minutes):", "daily_workout_goal")
        ]
        
        self.entries = {}
        
        for i, (label_text, field_name) in enumerate(fields):
            label = tk.Label(self.form_frame, text=label_text, 
                           font=self.normal_font, bg=self.bg_color)
            label.grid(row=i+1, column=0, sticky="w", pady=5)
            
            var = tk.StringVar()
            
            # Special case for name (read-only)
            if field_name == "name":
                entry = tk.Entry(self.form_frame, textvariable=var, width=20, state="readonly")
                self.entries[field_name] = var
            # Special case for gender (dropdown instead of entry)
            elif field_name == "gender":
                entry = ttk.Combobox(self.form_frame, textvariable=var, 
                                     values=["Male", "Female", "Other"], width=18)
                self.entries[field_name] = var
            else:
                entry = tk.Entry(self.form_frame, textvariable=var, width=20)
                self.entries[field_name] = var
            
            entry.grid(row=i+1, column=1, sticky="w", pady=5)
        
        # Buttons frame
        buttons_frame = tk.Frame(self.form_frame, bg=self.bg_color)
        buttons_frame.grid(row=len(fields)+1, column=0, columnspan=2, pady=15)
        
        # Save button
        save_button = tk.Button(buttons_frame, text="Save Profile", 
                             font=self.normal_font, bg="#2ecc71", fg="white",
                             padx=15, pady=5, command=self.save_profile)
        save_button.pack(side=tk.LEFT, padx=5)
        
        # Reset button
        reset_button = tk.Button(buttons_frame, text="Reset Form", 
                              font=self.normal_font, bg="#e74c3c", fg="white",
                              padx=15, pady=5, command=self.reset_form)
        reset_button.pack(side=tk.LEFT, padx=5)
    
    def create_display_area(self):
        # Title
        title_label = tk.Label(self.display_frame, text="Your Profile", 
                             font=self.title_font, bg=self.bg_color)
        title_label.pack(anchor="w", pady=(0, 10))
        
        # Profile info frame
        self.profile_info_frame = tk.Frame(self.display_frame, bg=self.bg_color)
        self.profile_info_frame.pack(fill=tk.X, expand=False)
        
        # BMI gauge frame (will contain the matplotlib figure)
        self.bmi_frame = tk.Frame(self.display_frame, bg=self.bg_color)
        self.bmi_frame.pack(fill=tk.BOTH, expand=True, pady=10)
    
    def update_profile_display(self, profile_data):
        # Clear existing widgets
        for widget in self.profile_info_frame.winfo_children():
            widget.destroy()
        
        # No profile data
        if not profile_data:
            no_profile_label = tk.Label(self.profile_info_frame, 
                                      text="No profile saved yet. Please fill in your details.",
                                      font=self.normal_font, bg=self.bg_color)
            no_profile_label.pack(anchor="w", pady=10)
            return
        
        # Profile frame with border
        profile_frame = tk.Frame(self.profile_info_frame, bg=self.bg_color,
                               relief=tk.RIDGE, bd=1, padx=15, pady=15)
        profile_frame.pack(fill=tk.X, expand=False)
        
        # Display user info
        name_label = tk.Label(profile_frame, 
                            text=f"Name: {profile_data['name']}", 
                            font=self.normal_font, bg=self.bg_color)
        name_label.pack(anchor="w", pady=2)
        
        age_gender_label = tk.Label(profile_frame, 
                                  text=f"Age: {profile_data['age']} | Gender: {profile_data['gender']}", 
                                  font=self.normal_font, bg=self.bg_color)
        age_gender_label.pack(anchor="w", pady=2)
        
        height_weight_label = tk.Label(profile_frame, 
                                     text=f"Height: {profile_data['height']} cm | Weight: {profile_data['weight']} kg", 
                                     font=self.normal_font, bg=self.bg_color)
        height_weight_label.pack(anchor="w", pady=2)
        
        goal_label = tk.Label(profile_frame, 
                            text=f"Daily Workout Goal: {profile_data['daily_workout_goal']} minutes", 
                            font=self.normal_font, bg=self.bg_color)
        goal_label.pack(anchor="w", pady=2)
        
        # Calculate and display BMI
        bmi = self.calculate_bmi(float(profile_data['weight']), float(profile_data['height']))
        bmi_label = tk.Label(profile_frame, 
                           text=f"BMI: {bmi:.1f} - {self.get_bmi_category(bmi)}", 
                           font=self.header_font, bg=self.bg_color, fg=self.get_bmi_color(bmi))
        bmi_label.pack(anchor="w", pady=(10, 2))
        
        # Create BMI visualization
        self.create_bmi_gauge(bmi)
    
    def calculate_bmi(self, weight, height):
        # BMI = weight(kg) / height(m)²
        height_m = height / 100  # Convert cm to m
        return weight / (height_m * height_m)
    
    def get_bmi_category(self, bmi):
        if bmi < 18.5:
            return "    Underweight"
        elif bmi < 25:
            return "Normal weight"
        elif bmi < 30:
            return "Overweight"
        else:
            return "Obese"
    
    def get_bmi_color(self, bmi):
        if bmi < 18.5:
            return "#3498db"  # Blue for underweight
        elif bmi < 25:
            return "#2ecc71"  # Green for normal
        elif bmi < 30:
            return "#f39c12"  # Orange for overweight
        else:
            return "#e74c3c"  # Red for obese
    
    def create_bmi_gauge(self, bmi):
        # Clear existing widgets
        for widget in self.bmi_frame.winfo_children():
            widget.destroy()
        
        # Create matplotlib figure
        fig, ax = plt.subplots(figsize=(6, 3), dpi=100)
        
        # BMI ranges
        bmi_ranges = [
            (0, 18.5, "#3498db", "    Underweight"),
            (18.5, 25, "#2ecc71", "Normal"),
            (25, 30, "#f39c12", "Overweight"),
            (30, 40, "#e74c3c", "Obese")
        ]
        
        # Create a horizontal BMI gauge
        for start, end, color, label in bmi_ranges:
            ax.barh(0, end-start, left=start, height=0.5, color=color, alpha=0.7)
            
            # Adjust position of "Underweight" text to move it slightly to the right
            if label == "    Underweight":
                # Move the text slightly to the right to avoid the 'w' being cut off
                ax.text((start + end) / 2 + 6, 0, label, ha='right', va='center', color='white', fontweight='bold')
            else:
                ax.text((start + end) / 2, 0, label, ha='center', va='center', color='white', fontweight='bold')
        
        # Add a marker for the user's BMI
        ax.plot(bmi, 0, 'ko', markersize=12)
        ax.plot(bmi, 0, 'wo', markersize=8)
        
        # Add text indicating the exact BMI value
        ax.text(bmi, 0.7, f'Your BMI: {bmi:.1f}', ha='center', fontweight='bold')
        
        # Set up the plot
        ax.set_xlim(10, 40)
        ax.set_ylim(-1, 1)
        ax.set_title('BMI Chart')
        ax.set_yticks([])
        ax.spines['left'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        
        # Embed the plot in the Tkinter frame
        canvas = FigureCanvasTkAgg(fig, master=self.bmi_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def save_profile(self):
        # Validate form
        try:
            name = self.entries["name"].get().strip()
            age = int(self.entries["age"].get())
            gender = self.entries["gender"].get()
            height = float(self.entries["height"].get())
            weight = float(self.entries["weight"].get())
            daily_workout_goal = int(self.entries["daily_workout_goal"].get())
            
            if not name:
                raise ValueError("Name cannot be empty")
            
            if age <= 0:
                raise ValueError("Age must be positive")
            
            if not gender:
                raise ValueError("Please select a gender")
            
            if height <= 0:
                raise ValueError("Height must be positive")
            
            if weight <= 0:
                raise ValueError("Weight must be positive")
            
            if daily_workout_goal < 0:
                raise ValueError("Daily workout goal cannot be negative")
            
        except ValueError as e:
            messagebox.showerror("Input Error", str(e))
            return
        
        # Save to database
        try:
            conn = sqlite3.connect('data/fitness_tracker.db')
            cursor = conn.cursor()
            
            # Check if profile already exists for this username
            cursor.execute("SELECT id FROM profile WHERE username=?", (self.username,))
            profile_id = cursor.fetchone()
            
            if profile_id:
                # Update existing profile
                cursor.execute("""
                UPDATE profile 
                SET name=?, age=?, gender=?, height=?, weight=?, daily_workout_goal=?
                WHERE username=?
                """, (name, age, gender, height, weight, daily_workout_goal, self.username))
            else:
                # Insert new profile
                cursor.execute("""
                INSERT INTO profile (username, name, age, gender, height, weight, daily_workout_goal)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (self.username, name, age, gender, height, weight, daily_workout_goal))
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", "Profile saved successfully!")
            
            # Update profile display
            self.load_profile()
            
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not save profile: {str(e)}")
    
    def load_profile(self):
        try:
            conn = sqlite3.connect('data/fitness_tracker.db')
            cursor = conn.cursor()
            
            cursor.execute("""
            SELECT name, age, gender, height, weight, daily_workout_goal
            FROM profile
            WHERE username=?
            LIMIT 1
            """, (self.username,))
            
            profile_data = cursor.fetchone()
            conn.close()
            
            if profile_data:
                # Create dictionary from profile data
                profile_dict = {
                    "name": profile_data[0],
                    "age": profile_data[1],
                    "gender": profile_data[2],
                    "height": profile_data[3],
                    "weight": profile_data[4],
                    "daily_workout_goal": profile_data[5]
                }
                
                # Update form fields
                self.entries["name"].set(profile_data[0])
                self.entries["age"].set(str(profile_data[1]))
                self.entries["gender"].set(profile_data[2])
                self.entries["height"].set(str(profile_data[3]))
                self.entries["weight"].set(str(profile_data[4]))
                self.entries["daily_workout_goal"].set(str(profile_data[5]))
                
                # Update display
                self.update_profile_display(profile_dict)
            else:
                # Set name from username and make other fields empty
                self.entries["name"].set(self.username)
                self.update_profile_display(None)
                
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not load profile: {str(e)}")
            self.update_profile_display(None)
    
    def reset_form(self):
        # Reset all entry fields except name
        name_value = self.entries["name"].get()
        
        for field, entry in self.entries.items():
            if field != "name":
                entry.set("")
                
        # Restore the name
        self.entries["name"].set(name_value)