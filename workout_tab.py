import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import pandas as pd
from tkinter import font

class WorkoutTab:
    def __init__(self, parent, bg_color, username):
        self.parent = parent
        self.bg_color = bg_color
        self.username = username
        
        # Set up fonts
        self.title_font = font.Font(family="Helvetica", size=14, weight="bold")
        self.header_font = font.Font(family="Helvetica", size=12, weight="bold")
        self.normal_font = font.Font(family="Helvetica", size=10)
        
        # Workout data
        self.workout_levels = {
            "Beginner": [
                {"name": "Push-ups", "reps": 10, "sets": 3, "calories_per_rep": 0.5},
                {"name": "Squats", "reps": 15, "sets": 3, "calories_per_rep": 0.6},
                {"name": "Plank", "reps": 30, "sets": 3, "calories_per_rep": 0.4, "is_duration": True},
                {"name": "Jumping Jacks", "reps": 20, "sets": 3, "calories_per_rep": 0.3},
                {"name": "Crunches", "reps": 12, "sets": 3, "calories_per_rep": 0.25}
            ],
            "Intermediate": [
                {"name": "Push-ups", "reps": 15, "sets": 4, "calories_per_rep": 0.5},
                {"name": "Squats", "reps": 20, "sets": 4, "calories_per_rep": 0.6},
                {"name": "Plank", "reps": 45, "sets": 4, "calories_per_rep": 0.4, "is_duration": True},
                {"name": "Burpees", "reps": 12, "sets": 3, "calories_per_rep": 1.0},
                {"name": "Mountain Climbers", "reps": 30, "sets": 3, "calories_per_rep": 0.3},
                {"name": "Lunges", "reps": 10, "sets": 3, "calories_per_rep": 0.4}
            ],
            "Advanced": [
                {"name": "Push-ups", "reps": 25, "sets": 4, "calories_per_rep": 0.5},
                {"name": "Squats", "reps": 30, "sets": 4, "calories_per_rep": 0.6},
                {"name": "Plank", "reps": 60, "sets": 3, "calories_per_rep": 0.4, "is_duration": True},
                {"name": "Burpees", "reps": 20, "sets": 4, "calories_per_rep": 1.0},
                {"name": "Pull-ups", "reps": 8, "sets": 3, "calories_per_rep": 1.0},
                {"name": "Box Jumps", "reps": 15, "sets": 4, "calories_per_rep": 0.7},
                {"name": "Diamond Push-ups", "reps": 12, "sets": 3, "calories_per_rep": 0.6}
            ]
        }
        
        # Current workout state
        self.current_workout = None
        self.current_level = None
        self.workout_in_progress = False
        self.workout_start_time = None
        self.completed_exercises = {}
        
        # Create UI elements
        self.create_widgets()
        
        # Load workout history
        self.load_workout_history()
        
    def create_widgets(self):
        # Create main container
        main_frame = ttk.Frame(self.parent, style="TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create top frame for workout selection
        self.top_frame = ttk.Frame(main_frame, style="TFrame")
        self.top_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Title
        title_label = ttk.Label(self.top_frame, text="Workout Tracker 💪", font=self.title_font, background=self.bg_color)
        title_label.grid(row=0, column=0, sticky="w", pady=(0, 20))
        
        # Level selection
        level_label = ttk.Label(self.top_frame, text="Select Workout Level:", font=self.normal_font, background=self.bg_color)
        level_label.grid(row=1, column=0, sticky="w")
        
        self.level_var = tk.StringVar()
        self.level_dropdown = ttk.Combobox(self.top_frame, textvariable=self.level_var, values=list(self.workout_levels.keys()), state="readonly", width=15)
        self.level_dropdown.grid(row=1, column=1, sticky="w", padx=(10, 20))
        self.level_dropdown.current(0)
        self.level_dropdown.bind("<<ComboboxSelected>>", self.on_level_selected)
        
        # Start/End workout buttons
        self.button_frame = ttk.Frame(self.top_frame, style="TFrame")
        self.button_frame.grid(row=1, column=2, sticky="w")
        
        self.start_button = ttk.Button(self.button_frame, text="Start Workout", command=self.start_workout)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.end_button = ttk.Button(self.button_frame, text="End Workout", command=self.end_workout, state=tk.DISABLED)
        self.end_button.pack(side=tk.LEFT, padx=5)
        
        # Create middle frame for current workout
        self.workout_frame = ttk.Frame(main_frame, style="TFrame")
        self.workout_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Create a label for initial state
        self.placeholder_label = ttk.Label(self.workout_frame, text="Select a workout level and press 'Start Workout' to begin", 
                                          font=self.normal_font, background=self.bg_color)
        self.placeholder_label.pack(pady=50)
        
        # Create bottom frame for workout history
        self.history_frame = ttk.Frame(main_frame, style="TFrame")
        self.history_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # History label
        history_label = ttk.Label(self.history_frame, text="Workout History", font=self.header_font, background=self.bg_color)
        history_label.pack(anchor="w", pady=(0, 10))
        
        # Create treeview for workout history
        self.history_tree = ttk.Treeview(self.history_frame, columns=("Date", "Level", "Duration", "Calories", "Status"), show="headings", height=5)
        self.history_tree.pack(fill=tk.BOTH, expand=True)
        
        # Configure columns
        self.history_tree.heading("Date", text="Date")
        self.history_tree.heading("Level", text="Level")
        self.history_tree.heading("Duration", text="Duration (min)")
        self.history_tree.heading("Calories", text="Calories Burned")
        self.history_tree.heading("Status", text="Status")
        
        self.history_tree.column("Date", width=120)
        self.history_tree.column("Level", width=100)
        self.history_tree.column("Duration", width=100)
        self.history_tree.column("Calories", width=100)
        self.history_tree.column("Status", width=100)
        
        # Add scrollbar to treeview
        history_scrollbar = ttk.Scrollbar(self.history_tree, orient=tk.VERTICAL, command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=history_scrollbar.set)
        history_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind double-click to view workout details
        self.history_tree.bind("<Double-1>", self.view_workout_details)
        
        # Create graph frame for workout visualization
        self.graph_frame = ttk.Frame(main_frame, style="TFrame")
        self.graph_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Create workout summary graph
        self.create_workout_graph()
        
    def on_level_selected(self, event=None):
        # Update exercises list when level is selected
        if not self.workout_in_progress:
            self.current_level = self.level_var.get()
            self.update_exercise_preview()
    
    def update_exercise_preview(self):
        # Clear any existing widgets
        for widget in self.workout_frame.winfo_children():
            widget.destroy()
        
        # Get exercises for selected level
        level = self.level_var.get()
        exercises = self.workout_levels.get(level, [])
        
        # Create a scrollable frame
        canvas = tk.Canvas(self.workout_frame, bg=self.bg_color)
        scrollbar = ttk.Scrollbar(self.workout_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style="TFrame")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Add preview header
        preview_label = ttk.Label(scrollable_frame, text=f"{level} Workout Preview", font=self.header_font, background=self.bg_color)
        preview_label.grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 10))
        
        # Add column headers
        ttk.Label(scrollable_frame, text="Exercise", font=self.normal_font, background=self.bg_color).grid(row=1, column=0, sticky="w", padx=(0, 20))
        ttk.Label(scrollable_frame, text="Reps", font=self.normal_font, background=self.bg_color).grid(row=1, column=1, sticky="w", padx=(0, 20))
        ttk.Label(scrollable_frame, text="Sets", font=self.normal_font, background=self.bg_color).grid(row=1, column=2, sticky="w", padx=(0, 20))
        
        # Add exercise details
        for i, exercise in enumerate(exercises):
            row = i + 2
            name = exercise["name"]
            reps = f"{exercise['reps']} {'seconds' if exercise.get('is_duration', False) else 'reps'}"
            sets = exercise["sets"]
            
            ttk.Label(scrollable_frame, text=name, font=self.normal_font, background=self.bg_color).grid(row=row, column=0, sticky="w", padx=(0, 20), pady=5)
            ttk.Label(scrollable_frame, text=reps, font=self.normal_font, background=self.bg_color).grid(row=row, column=1, sticky="w", padx=(0, 20), pady=5)
            ttk.Label(scrollable_frame, text=sets, font=self.normal_font, background=self.bg_color).grid(row=row, column=2, sticky="w", padx=(0, 20), pady=5)
        
        # Pack the canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def start_workout(self):
        # Initialize new workout
        self.current_level = self.level_var.get()
        self.current_workout = self.workout_levels[self.current_level]
        self.workout_in_progress = True
        self.workout_start_time = datetime.now()
        self.completed_exercises = {}
        
        # Update UI state
        self.start_button.configure(state=tk.DISABLED)
        self.end_button.configure(state=tk.NORMAL)
        self.level_dropdown.configure(state=tk.DISABLED)
        
        # Show workout interface
        self.show_workout_interface()
    
    def show_workout_interface(self):
        # Clear workout frame
        for widget in self.workout_frame.winfo_children():
            widget.destroy()
        
        # Create a scrollable frame
        canvas = tk.Canvas(self.workout_frame, bg=self.bg_color)
        scrollbar = ttk.Scrollbar(self.workout_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style="TFrame")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Add workout header
        workout_label = ttk.Label(scrollable_frame, text=f"{self.current_level} Workout in Progress", font=self.header_font, background=self.bg_color)
        workout_label.grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 10))
        
        # Create progress bar
        self.progress_var = tk.DoubleVar(value=0.0)
        progress_frame = ttk.Frame(scrollable_frame, style="TFrame")
        progress_frame.grid(row=1, column=0, columnspan=4, sticky="ew", pady=(0, 20))
        
        ttk.Label(progress_frame, text="Progress:", font=self.normal_font, background=self.bg_color).pack(side=tk.LEFT, padx=(0, 10))
        progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, length=300, mode="determinate")
        progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Create calories burned display
        self.calories_var = tk.StringVar(value="0")
        calories_frame = ttk.Frame(scrollable_frame, style="TFrame")
        calories_frame.grid(row=2, column=0, columnspan=4, sticky="ew", pady=(0, 20))
        
        ttk.Label(calories_frame, text="Calories Burned:", font=self.normal_font, background=self.bg_color).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Label(calories_frame, textvariable=self.calories_var, font=self.normal_font, background=self.bg_color).pack(side=tk.LEFT)
        
        # Add column headers
        ttk.Label(scrollable_frame, text="Exercise", font=self.normal_font, background=self.bg_color).grid(row=3, column=0, sticky="w", padx=(0, 20))
        ttk.Label(scrollable_frame, text="Sets Completed", font=self.normal_font, background=self.bg_color).grid(row=3, column=1, sticky="w", padx=(0, 20))
        ttk.Label(scrollable_frame, text="Target", font=self.normal_font, background=self.bg_color).grid(row=3, column=2, sticky="w", padx=(0, 20))
        ttk.Label(scrollable_frame, text="Actions", font=self.normal_font, background=self.bg_color).grid(row=3, column=3, sticky="w", padx=(0, 20))
        
        # Add exercise rows with set tracking
        for i, exercise in enumerate(self.current_workout):
            row = i + 4
            name = exercise["name"]
            target_sets = exercise["sets"]
            rep_text = f"{exercise['reps']} {'seconds' if exercise.get('is_duration', False) else 'reps'}"
            
            # Initialize exercise in completed_exercises
            if name not in self.completed_exercises:
                self.completed_exercises[name] = {
                    "completed_sets": 0,
                    "target_sets": target_sets,
                    "reps": exercise["reps"],
                    "calories_per_rep": exercise["calories_per_rep"]
                }
            
            # Exercise name
            ttk.Label(scrollable_frame, text=name, font=self.normal_font, background=self.bg_color).grid(row=row, column=0, sticky="w", padx=(0, 20), pady=5)
            
            # Sets completed counter
            sets_frame = ttk.Frame(scrollable_frame, style="TFrame")
            sets_frame.grid(row=row, column=1, sticky="w", padx=(0, 20), pady=5)
            
            sets_var = tk.StringVar(value=f"{self.completed_exercises[name]['completed_sets']}")
            ttk.Label(sets_frame, textvariable=sets_var, font=self.normal_font, background=self.bg_color).pack(side=tk.LEFT)
            
            # Update reference to the StringVar in completed_exercises
            self.completed_exercises[name]["sets_var"] = sets_var
            
            # Target display
            ttk.Label(scrollable_frame, text=f"{target_sets} sets of {rep_text}", font=self.normal_font, background=self.bg_color).grid(row=row, column=2, sticky="w", padx=(0, 20), pady=5)
            
            # Complete set button
            complete_button = ttk.Button(
                scrollable_frame, 
                text="Complete Set", 
                command=lambda ex=name: self.complete_set(ex)
            )
            complete_button.grid(row=row, column=3, sticky="w", padx=(0, 20), pady=5)
            
        # Pack the canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def complete_set(self, exercise_name):
        # Update completed sets
        exercise = self.completed_exercises[exercise_name]
        
        if exercise["completed_sets"] < exercise["target_sets"]:
            exercise["completed_sets"] += 1
            exercise["sets_var"].set(f"{exercise['completed_sets']}")
            
            # Update calories burned
            new_calories = float(self.calories_var.get()) + (exercise["reps"] * exercise["calories_per_rep"])
            self.calories_var.set(f"{new_calories:.1f}")
            
            # Update progress bar
            total_sets = sum(ex["target_sets"] for ex in self.completed_exercises.values())
            completed_sets = sum(ex["completed_sets"] for ex in self.completed_exercises.values())
            progress = (completed_sets / total_sets) * 100
            self.progress_var.set(progress)
    
    def end_workout(self):
        # Check if workout is in progress
        if not self.workout_in_progress:
            return
        
        # Calculate workout duration
        duration = (datetime.now() - self.workout_start_time).total_seconds() / 60  # in minutes
        
        # Calculate completion status
        total_sets = sum(ex["target_sets"] for ex in self.completed_exercises.values())
        completed_sets = sum(ex["completed_sets"] for ex in self.completed_exercises.values())
        
        completion_percentage = (completed_sets / total_sets) * 100
        
        if completion_percentage == 100:
            status = "Completed"
        elif completion_percentage >= 75:
            status = "Mostly Done"
        elif completion_percentage >= 50:
            status = "Half Done"
        else:
            status = "Partial"
        
        # Get calories burned
        calories_burned = float(self.calories_var.get())
        
        # Save workout to database
        self.save_workout(self.current_level, duration, calories_burned, status, completed_sets, total_sets)
        
        # Reset workout state
        self.workout_in_progress = False
        self.current_workout = None
        
        # Update UI
        self.start_button.configure(state=tk.NORMAL)
        self.end_button.configure(state=tk.DISABLED)
        self.level_dropdown.configure(state="readonly")
        
        # Show exercise preview again
        self.update_exercise_preview()
        
        # Refresh history
        self.load_workout_history()
        
        # Show completion message
        messagebox.showinfo("Workout Completed", 
                           f"Workout ended!\nDuration: {duration:.1f} minutes\nCalories Burned: {calories_burned:.1f}\nCompletion: {completion_percentage:.1f}%")
    
    def save_workout(self, level, duration, calories_burned, status, completed_sets, total_sets):
        try:
            conn = sqlite3.connect('data/fitness_tracker.db')
            cursor = conn.cursor()
            
            # Insert workout record
            cursor.execute('''
                INSERT INTO workouts (username, date, level, duration, calories_burned, completed)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (self.username, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 
                 level, duration, calories_burned, 1 if status == "Completed" else 0))
            
            workout_id = cursor.lastrowid
            
            # Insert exercise details
            for exercise_name, exercise_data in self.completed_exercises.items():
                cursor.execute('''
                    INSERT INTO workout_exercises (workout_id, exercise_name, sets, reps)
                    VALUES (?, ?, ?, ?)
                ''', (workout_id, exercise_name, exercise_data["completed_sets"], exercise_data["reps"]))
            
            conn.commit()
            conn.close()
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred while saving workout: {e}")
    
    def load_workout_history(self):
        # Clear existing items
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        try:
            conn = sqlite3.connect('data/fitness_tracker.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, date, level, duration, calories_burned, completed
                FROM workouts
                WHERE username = ?
                ORDER BY date DESC
                LIMIT 10
            ''', (self.username,))
            
            workouts = cursor.fetchall()
            
            for workout in workouts:
                workout_id, date, level, duration, calories, completed = workout
                status = "Completed" if completed == 1 else "Partial"
                
                # Format date
                date_obj = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
                formatted_date = date_obj.strftime('%b %d, %Y %I:%M %p')
                
                # Insert into treeview
                self.history_tree.insert("", "end", values=(formatted_date, level, f"{duration:.1f}", f"{calories:.1f}", status), tags=(workout_id,))
            
            conn.close()
            
            # Update workout graph
            self.create_workout_graph()
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred while loading workout history: {e}")
    
    def view_workout_details(self, event):
        # Get selected item
        item_id = self.history_tree.focus()
        if not item_id:
            return
        
        # Get workout_id from tags
        workout_id = self.history_tree.item(item_id, "tags")[0]
        
        try:
            conn = sqlite3.connect('data/fitness_tracker.db')
            cursor = conn.cursor()
            
            # Get workout details
            cursor.execute('''
                SELECT date, level, duration, calories_burned, completed
                FROM workouts
                WHERE id = ?
            ''', (workout_id,))
            
            workout = cursor.fetchone()
            
            if not workout:
                conn.close()
                return
                
            date, level, duration, calories, completed = workout
            
            # Get exercise details
            cursor.execute('''
                SELECT exercise_name, sets, reps
                FROM workout_exercises
                WHERE workout_id = ?
            ''', (workout_id,))
            
            exercises = cursor.fetchall()
            
            conn.close()
            
            # Create details window
            details_window = tk.Toplevel(self.parent)
            details_window.title("Workout Details")
            details_window.geometry("400x500")
            details_window.resizable(False, False)
            
            # Add workout details
            details_frame = ttk.Frame(details_window, padding=20)
            details_frame.pack(fill=tk.BOTH, expand=True)
            
            ttk.Label(details_frame, text="Workout Details", font=self.title_font).pack(anchor="w", pady=(0, 20))
            
            # Format date
            date_obj = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
            formatted_date = date_obj.strftime('%B %d, %Y at %I:%M %p')
            
            ttk.Label(details_frame, text=f"Date: {formatted_date}", font=self.normal_font).pack(anchor="w", pady=2)
            ttk.Label(details_frame, text=f"Level: {level}", font=self.normal_font).pack(anchor="w", pady=2)
            ttk.Label(details_frame, text=f"Duration: {duration:.1f} minutes", font=self.normal_font).pack(anchor="w", pady=2)
            ttk.Label(details_frame, text=f"Calories Burned: {calories:.1f}", font=self.normal_font).pack(anchor="w", pady=2)
            ttk.Label(details_frame, text=f"Status: {'Completed' if completed == 1 else 'Partial'}", font=self.normal_font).pack(anchor="w", pady=2)
            
            # Add separator
            ttk.Separator(details_frame, orient="horizontal").pack(fill="x", pady=10)
            
            # Add exercises
            ttk.Label(details_frame, text="Exercises Completed", font=self.header_font).pack(anchor="w", pady=(10, 5))
            
            # Create treeview for exercises
            exercise_tree = ttk.Treeview(details_frame, columns=("Exercise", "Sets", "Reps"), show="headings", height=len(exercises))
            exercise_tree.pack(fill=tk.BOTH, expand=True, pady=10)
            
            exercise_tree.heading("Exercise", text="Exercise")
            exercise_tree.heading("Sets", text="Sets")
            exercise_tree.heading("Reps", text="Reps")
            
            exercise_tree.column("Exercise", width=200)
            exercise_tree.column("Sets", width=80)
            exercise_tree.column("Reps", width=80)
            
            # Add exercise data
            for exercise in exercises:
                name, sets, reps = exercise
                exercise_tree.insert("", "end", values=(name, sets, reps))
            
            # Add close button
            ttk.Button(details_frame, text="Close", command=details_window.destroy).pack(pady=20)
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred while loading workout details: {e}")
    
    def create_workout_graph(self):
        # Clear existing graph
        for widget in self.graph_frame.winfo_children():
            widget.destroy()
        
        try:
            conn = sqlite3.connect('data/fitness_tracker.db')
            cursor = conn.cursor()
            
            # Get workout data for last 10 workouts
            cursor.execute('''
                SELECT date, calories_burned, duration
                FROM workouts
                WHERE username = ?
                ORDER BY date ASC
                LIMIT 10
            ''', (self.username,))
            
            workouts = cursor.fetchall()
            conn.close()
            
            if not workouts:
                # Show placeholder if no data
                ttk.Label(self.graph_frame, text="Complete workouts to see your progress graph", 
                         font=self.normal_font, background=self.bg_color).pack(pady=20)
                return
            
            # Create figure and axis
            figure = plt.Figure(figsize=(8, 3), dpi=100)
            ax = figure.add_subplot(111)
            
            # Prepare data
            dates = [datetime.strptime(workout[0], '%Y-%m-%d %H:%M:%S').strftime('%m/%d') for workout in workouts]
            calories = [workout[1] for workout in workouts]
            
            # Create bar chart
            bars = ax.bar(dates, calories, color='#3498db')
            ax.set_title('Calories Burned per Workout')
            ax.set_xlabel('Date')
            ax.set_ylabel('Calories')
            
            # Adjust layout
            figure.tight_layout()
            
            # Create canvas
            canvas = FigureCanvasTkAgg(figure, self.graph_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
        except Exception as e:
            # Show error message if graph creation fails
            ttk.Label(self.graph_frame, text=f"Unable to create graph: {e}", 
                     font=self.normal_font, background=self.bg_color).pack(pady=20)