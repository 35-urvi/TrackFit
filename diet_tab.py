import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
import datetime
from tkcalendar import DateEntry
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from collections import defaultdict
from matplotlib.figure import Figure

class DietTab:
    def __init__(self, parent, bg_color, username):
        self.parent = parent
        self.bg_color = bg_color
        self.username = username
        
        # Set theme colors (matching main app)
        self.primary_color = "#3498db"  # Blue
        self.secondary_color = "#2ecc71"  # Green
        self.text_color = "#333333"  # Dark Gray
        
        # Initialize dates
        self.today = datetime.date.today()
        self.selected_date = self.today
        
        # Set default goals
        self.default_calorie_goal = 2000
        self.default_hydration_goal = 2000  # ml
        
        # Check if the user has custom goals
        self.load_user_goals()
        
        # Create main frame
        self.main_frame = tk.Frame(parent, bg=bg_color, width=900, height=600)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create persistent buttons first so they're at the bottom layer
        self.create_persistent_buttons()
        
        # Create left and right sections
        self.setup_main_layout()
        
        # Fill the sections with content
        self.setup_diet_tracker()
        self.setup_hydration_tracker()
        # self.setup_weekly_summary()
        
        # Load data for current date
        self.refresh_data()
    
    def setup_main_layout(self):
        # Create upper and lower sections
        self.upper_frame = tk.Frame(self.main_frame, bg=self.bg_color, height=400)
        self.upper_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.lower_frame = tk.Frame(self.main_frame, bg=self.bg_color, height=200)
        self.lower_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create left and right sections in upper frame
        self.left_frame = tk.Frame(self.upper_frame, bg=self.bg_color, width=450)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.right_frame = tk.Frame(self.upper_frame, bg=self.bg_color, width=450)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
    
    def create_persistent_buttons(self):
        """Create persistent buttons that will always be visible at the bottom"""
        # Create a frame at the bottom of the main frame for persistent buttons
        self.persistent_button_frame = tk.Frame(self.main_frame, bg=self.bg_color, height=50)
        self.persistent_button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
        
        # Create the buttons
        self.add_meal_button = tk.Button(self.persistent_button_frame, text="Add Meal", command=self.add_meal, 
                                       bg=self.secondary_color, fg="white", height=2, width=15)
        self.add_meal_button.pack(side=tk.LEFT, padx=5)#, expand=True)
        
        self.quick_add_button = tk.Button(self.persistent_button_frame, text="Quick Add", command=self.quick_add_meal, 
                                        bg=self.secondary_color, fg="white", height=2, width=15)
        self.quick_add_button.pack(side=tk.LEFT, padx=5)#, expand=True)
    
    def load_user_goals(self):
        try:
            conn = sqlite3.connect('data/fitness_tracker.db')
            cursor = conn.cursor()
            
            # Check if goals table exists, if not create it
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS diet_goals (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE,
                calorie_goal INTEGER,
                hydration_goal INTEGER,
                protein_goal INTEGER,
                carbs_goal INTEGER,
                fats_goal INTEGER
            )
            ''')
            
            # Get user's goals
            cursor.execute('SELECT calorie_goal, hydration_goal FROM diet_goals WHERE username = ?', 
                          (self.username,))
            result = cursor.fetchone()
            
            if result:
                self.calorie_goal, self.hydration_goal = result
            else:
                # Set defaults and create entry
                self.calorie_goal = self.default_calorie_goal
                self.hydration_goal = self.default_hydration_goal
                
                cursor.execute('''
                INSERT INTO diet_goals (username, calorie_goal, hydration_goal, protein_goal, carbs_goal, fats_goal)
                VALUES (?, ?, ?, ?, ?, ?)
                ''', (self.username, self.calorie_goal, self.hydration_goal, 50, 250, 70))
                
            conn.commit()
            conn.close()
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            self.calorie_goal = self.default_calorie_goal
            self.hydration_goal = self.default_hydration_goal
    
    def setup_diet_tracker(self):
        # Create a frame for the diet tracker section with border
        diet_frame = tk.LabelFrame(self.left_frame, text="Meal Tracker", padx=10, pady=10, bg=self.bg_color)
        diet_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Date selector
        date_frame = tk.Frame(diet_frame, bg=self.bg_color)
        date_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(date_frame, text="Date:", bg=self.bg_color).pack(side=tk.LEFT, padx=5)
        self.date_picker = DateEntry(date_frame, width=12, background=self.primary_color, 
                                     foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.date_picker.pack(side=tk.LEFT, padx=5)
        self.date_picker.set_date(self.selected_date)
        self.date_picker.bind("<<DateEntrySelected>>", self.date_changed)
        
        # Calorie goal display
        goal_frame = tk.Frame(diet_frame, bg=self.bg_color)
        goal_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(goal_frame, text="Daily Calorie Goal:", bg=self.bg_color).pack(side=tk.LEFT, padx=5)
        self.calorie_goal_label = tk.Label(goal_frame, text=f"{self.calorie_goal} kcal", bg=self.bg_color)
        self.calorie_goal_label.pack(side=tk.LEFT, padx=5)
        
        tk.Button(goal_frame, text="Set Goal", command=self.set_calorie_goal, 
                 bg=self.primary_color, fg="white").pack(side=tk.RIGHT, padx=5)
        
        # Calorie progress
        progress_frame = tk.Frame(diet_frame, bg=self.bg_color)
        progress_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(progress_frame, text="Today's Calories:", bg=self.bg_color).pack(side=tk.LEFT, padx=5)
        self.calorie_progress_label = tk.Label(progress_frame, text="0/2000 kcal", bg=self.bg_color)
        self.calorie_progress_label.pack(side=tk.LEFT, padx=5)
        
        # Calorie progress bar
        self.calorie_progress = ttk.Progressbar(diet_frame, orient="horizontal", length=300, mode="determinate")
        self.calorie_progress.pack(fill=tk.X, pady=5)
        
        # Macronutrient Frame for Pie Chart (make it smaller)
        self.macro_frame = tk.Frame(diet_frame, bg=self.bg_color, height=180)  # Reduced height
        self.macro_frame.pack(fill=tk.X, expand=False, pady=5)
        
        log_frame = tk.LabelFrame(diet_frame, text="Today's Meals", padx=10, pady=10, bg=self.bg_color)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # Create a frame to hold both the Treeview and the Scrollbar
        table_frame = tk.Frame(log_frame, bg=self.bg_color)
        table_frame.pack(fill=tk.BOTH, expand=True)

        # Meal log table inside table_frame
        self.meal_log = ttk.Treeview(table_frame, columns=("type", "food", "calories", "protein", "carbs", "fats"), 
                                    show="headings", height=6)
        self.meal_log.heading("type", text="Meal Type")
        self.meal_log.heading("food", text="Food Name")
        self.meal_log.heading("calories", text="Calories")
        self.meal_log.heading("protein", text="Protein(g)")
        self.meal_log.heading("carbs", text="Carbs(g)")
        self.meal_log.heading("fats", text="Fats(g)")

        self.meal_log.column("type", width=80)
        self.meal_log.column("food", width=120)
        self.meal_log.column("calories", width=70, anchor=tk.CENTER)
        self.meal_log.column("protein", width=70, anchor=tk.CENTER)
        self.meal_log.column("carbs", width=70, anchor=tk.CENTER)
        self.meal_log.column("fats", width=70, anchor=tk.CENTER)

        self.meal_log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Add scrollbar inside table_frame, beside the table
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.meal_log.yview)
        self.meal_log.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)  # Now correctly positioned beside the table

        # Add buttons for managing meals (only Delete button remains here)
        button_frame = tk.Frame(diet_frame, bg=self.bg_color)
        button_frame.pack(fill=tk.X, pady=5)

        tk.Button(button_frame, text="Delete Selected", command=self.delete_meal, 
                bg="#e74c3c", fg="white").pack(side=tk.RIGHT, padx=5)

    
    def setup_hydration_tracker(self):
        # Create a frame for the hydration tracker
        hydration_frame = tk.LabelFrame(self.right_frame, text="Hydration Tracker", padx=10, pady=10, bg=self.bg_color)
        hydration_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Hydration goal
        goal_frame = tk.Frame(hydration_frame, bg=self.bg_color)
        goal_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(goal_frame, text="Daily Hydration Goal:", bg=self.bg_color).pack(side=tk.LEFT, padx=5)
        self.hydration_goal_label = tk.Label(goal_frame, text=f"{self.hydration_goal} ml", bg=self.bg_color)
        self.hydration_goal_label.pack(side=tk.LEFT, padx=5)
        
        tk.Button(goal_frame, text="Set Goal", command=self.set_hydration_goal, 
                 bg=self.primary_color, fg="white").pack(side=tk.RIGHT, padx=5)
        
        # Hydration progress
        progress_frame = tk.Frame(hydration_frame, bg=self.bg_color)
        progress_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(progress_frame, text="Today's Hydration:", bg=self.bg_color).pack(side=tk.LEFT, padx=5)
        self.hydration_progress_label = tk.Label(progress_frame, text="0/2000 ml", bg=self.bg_color)
        self.hydration_progress_label.pack(side=tk.LEFT, padx=5)
        
        # Hydration progress bar
        self.hydration_progress = ttk.Progressbar(hydration_frame, orient="horizontal", length=300, mode="determinate")
        self.hydration_progress.pack(fill=tk.X, pady=5)
        
        # Water bottle visualization frame
        self.bottle_frame = tk.Frame(hydration_frame, bg=self.bg_color, height=200)
        self.bottle_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Quick add water buttons
        button_frame = tk.Frame(hydration_frame, bg=self.bg_color)
        button_frame.pack(fill=tk.X, pady=5)
        
        amounts = [100, 250, 500, 1000]
        for amount in amounts:
            tk.Button(button_frame, text=f"+{amount} ml", command=lambda amt=amount: self.add_water(amt),
                     bg=self.primary_color, fg="white").pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="Custom Amount", command=self.add_custom_water,
                 bg=self.secondary_color, fg="white").pack(side=tk.RIGHT, padx=5)
    
    def setup_weekly_summary(self):
        # Create a frame for the weekly summary
        summary_frame = tk.LabelFrame(self.lower_frame, text="Weekly Summary & Insights", padx=10, pady=10, bg=self.bg_color)
        summary_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Split into left (graph) and right (insights) sections
        summary_left = tk.Frame(summary_frame, bg=self.bg_color)
        summary_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        summary_right = tk.Frame(summary_frame, bg=self.bg_color)
        summary_right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)
        
        # Graph frame for weekly calorie trends
        self.graph_frame = tk.Frame(summary_left, bg=self.bg_color)
        self.graph_frame.pack(fill=tk.BOTH, expand=True)
        
        # Insights text box
        tk.Label(summary_right, text="Nutritional Insights", bg=self.bg_color, font=('Helvetica', 12, 'bold')).pack(anchor=tk.W, pady=5)
        
        self.insights_text = tk.Text(summary_right, wrap=tk.WORD, height=12, width=40)
        self.insights_text.pack(fill=tk.BOTH, expand=True)
        self.insights_text.config(state=tk.DISABLED)
        
        # Achievements and streaks
        achievement_frame = tk.Frame(summary_right, bg=self.bg_color)
        achievement_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(achievement_frame, text="Achievements & Streaks", bg=self.bg_color, font=('Helvetica', 12, 'bold')).pack(anchor=tk.W)
        
        self.achievement_label = tk.Label(achievement_frame, text="", bg=self.bg_color)
        self.achievement_label.pack(anchor=tk.W, pady=5)
    
    def refresh_data(self):
        """Refresh all data displays for the selected date"""
        self.load_meals()
        self.load_hydration()
        self.update_macronutrient_chart()
        # self.update_weekly_graph()
        # self.update_insights()
        
        # Always keep the persistent buttons visible
        self.persistent_button_frame.lift()
    
    def date_changed(self, event=None):
        """Handle date change event"""
        self.selected_date = self.date_picker.get_date()
        
        self.refresh_data()
    
    def load_meals(self):
        """Load meals for the selected date"""
        try:
            # Clear existing items
            for item in self.meal_log.get_children():
                self.meal_log.delete(item)
            
            conn = sqlite3.connect('data/fitness_tracker.db')
            cursor = conn.cursor()
            
            date_str = self.selected_date.strftime('%Y-%m-%d')
            
            cursor.execute('''
            SELECT id, meal_type, food_name, calories, protein, carbs, fats
            FROM meals
            WHERE username = ? AND date = ?
            ORDER BY meal_type
            ''', (self.username, date_str))
            
            total_calories = 0
            self.meals_data = []
            
            for row in cursor.fetchall():
                meal_id, meal_type, food_name, calories, protein, carbs, fats = row
                self.meal_log.insert('', 'end', iid=meal_id, values=(meal_type, food_name, calories, protein, carbs, fats))
                total_calories += calories
                self.meals_data.append({
                    'id': meal_id,
                    'meal_type': meal_type,
                    'food_name': food_name,
                    'calories': calories,
                    'protein': protein,
                    'carbs': carbs,
                    'fats': fats
                })
            
            # Update progress
            self.update_calorie_progress(total_calories)
            
            conn.close()
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            messagebox.showerror("Database Error", "Error loading meals from database.")
    
    def update_calorie_progress(self, total_calories):
        """Update the calorie progress display"""
        # Update label
        self.calorie_progress_label.config(text=f"{total_calories}/{self.calorie_goal} kcal")
        
        # Update progress bar
        progress_percentage = min(100, (total_calories / self.calorie_goal) * 100)
        self.calorie_progress["value"] = progress_percentage
    
    def add_meal(self):
        """Open dialog to add a new meal"""
        add_meal_window = tk.Toplevel(self.parent)
        add_meal_window.title("Add Meal")
        add_meal_window.geometry("400x400")
        add_meal_window.resizable(False, False)
        add_meal_window.configure(bg=self.bg_color)
        add_meal_window.transient(self.parent)
        add_meal_window.grab_set()
        
        # Meal type selection
        tk.Label(add_meal_window, text="Meal Type:", bg=self.bg_color).grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        meal_types = ["Breakfast", "Lunch", "Dinner", "Snack"]
        meal_type_var = tk.StringVar(value=meal_types[0])
        meal_type_dropdown = ttk.Combobox(add_meal_window, textvariable=meal_type_var, values=meal_types, state="readonly")
        meal_type_dropdown.grid(row=0, column=1, padx=10, pady=10, sticky=tk.W)
        
        # Food name entry
        tk.Label(add_meal_window, text="Food Name:", bg=self.bg_color).grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        food_name_var = tk.StringVar()
        food_name_entry = tk.Entry(add_meal_window, textvariable=food_name_var, width=30)
        food_name_entry.grid(row=1, column=1, padx=10, pady=10, sticky=tk.W)
        
        # Calories entry
        tk.Label(add_meal_window, text="Calories:", bg=self.bg_color).grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)
        calories_var = tk.IntVar(value=0)
        calories_entry = tk.Entry(add_meal_window, textvariable=calories_var, width=10)
        calories_entry.grid(row=2, column=1, padx=10, pady=10, sticky=tk.W)
        
        # Macronutrient entries
        tk.Label(add_meal_window, text="Protein (g):", bg=self.bg_color).grid(row=3, column=0, padx=10, pady=10, sticky=tk.W)
        protein_var = tk.DoubleVar(value=0)
        protein_entry = tk.Entry(add_meal_window, textvariable=protein_var, width=10)
        protein_entry.grid(row=3, column=1, padx=10, pady=10, sticky=tk.W)
        
        tk.Label(add_meal_window, text="Carbs (g):", bg=self.bg_color).grid(row=4, column=0, padx=10, pady=10, sticky=tk.W)
        carbs_var = tk.DoubleVar(value=0)
        carbs_entry = tk.Entry(add_meal_window, textvariable=carbs_var, width=10)
        carbs_entry.grid(row=4, column=1, padx=10, pady=10, sticky=tk.W)
        
        tk.Label(add_meal_window, text="Fats (g):", bg=self.bg_color).grid(row=5, column=0, padx=10, pady=10, sticky=tk.W)
        fats_var = tk.DoubleVar(value=0)
        fats_entry = tk.Entry(add_meal_window, textvariable=fats_var, width=10)
        fats_entry.grid(row=5, column=1, padx=10, pady=10, sticky=tk.W)
        
        # Buttons
        button_frame = tk.Frame(add_meal_window, bg=self.bg_color)
        button_frame.grid(row=6, column=0, columnspan=2, pady=20)
        
        tk.Button(button_frame, text="Cancel", command=add_meal_window.destroy, 
                 bg="#e74c3c", fg="white").pack(side=tk.LEFT, padx=10)
        
        tk.Button(button_frame, text="Save", command=lambda: self.save_meal(
            meal_type_var.get(), 
            food_name_var.get(), 
            calories_var.get(), 
            protein_var.get(), 
            carbs_var.get(), 
            fats_var.get(), 
            add_meal_window
        ), bg=self.secondary_color, fg="white").pack(side=tk.LEFT, padx=10)
    
    def quick_add_meal(self):
        """Open dialog with common foods for quick adding"""
        quick_add_window = tk.Toplevel(self.parent)
        quick_add_window.title("Quick Add Meal")
        quick_add_window.geometry("500x400")
        quick_add_window.resizable(False, False)
        quick_add_window.configure(bg=self.bg_color)
        quick_add_window.transient(self.parent)
        quick_add_window.grab_set()
        
        # Common foods with nutritional info
        common_foods = [
            {"name": "Chicken Breast (100g)", "calories": 165, "protein": 31, "carbs": 0, "fats": 3.6},
            {"name": "Brown Rice (100g cooked)", "calories": 112, "protein": 2.6, "carbs": 23, "fats": 0.9},
            {"name": "Egg (large)", "calories": 70, "protein": 6, "carbs": 0.6, "fats": 5},
            {"name": "Banana (medium)", "calories": 105, "protein": 1.3, "carbs": 27, "fats": 0.4},
            {"name": "Greek Yogurt (100g)", "calories": 59, "protein": 10, "carbs": 3.6, "fats": 0.4},
            {"name": "Oatmeal (100g cooked)", "calories": 71, "protein": 2.5, "carbs": 12, "fats": 1.5},
            {"name": "Salmon (100g)", "calories": 206, "protein": 22, "carbs": 0, "fats": 13},
            {"name": "Apple (medium)", "calories": 95, "protein": 0.5, "carbs": 25, "fats": 0.3},
            {"name": "Avocado (half)", "calories": 160, "protein": 2, "carbs": 8.5, "fats": 15},
            {"name": "Whole Wheat Bread (slice)", "calories": 81, "protein": 4, "carbs": 13.8, "fats": 1.1}
        ]
        
        # Meal type selection
        tk.Label(quick_add_window, text="Meal Type:", bg=self.bg_color).grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        meal_types = ["Breakfast", "Lunch", "Dinner", "Snack"]
        meal_type_var = tk.StringVar(value=meal_types[0])
        meal_type_dropdown = ttk.Combobox(quick_add_window, textvariable=meal_type_var, values=meal_types, state="readonly")
        meal_type_dropdown.grid(row=0, column=1, padx=10, pady=10, sticky=tk.W)
        
        # Create a frame for the food list
        list_frame = tk.Frame(quick_add_window, bg=self.bg_color)
        list_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky=tk.NSEW)
        
        # Create treeview for foods
        food_list = ttk.Treeview(list_frame, columns=("name", "calories", "protein", "carbs", "fats"), show="headings", height=10)
        food_list.heading("name", text="Food Name")
        food_list.heading("calories", text="Calories")
        food_list.heading("protein", text="Protein(g)")
        food_list.heading("carbs", text="Carbs(g)")
        food_list.heading("fats", text="Fats(g)")
        
        food_list.column("name", width=200)
        food_list.column("calories", width=70, anchor=tk.CENTER)
        food_list.column("protein", width=70, anchor=tk.CENTER)
        food_list.column("carbs", width=70, anchor=tk.CENTER)
        food_list.column("fats", width=70, anchor=tk.CENTER)
        
        # Add foods to the list
        for i, food in enumerate(common_foods):
            food_list.insert('', 'end', iid=i, values=(
                food["name"], 
                food["calories"], 
                food["protein"], 
                food["carbs"], 
                food["fats"]
            ))
        
        food_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Buttons
        button_frame = tk.Frame(quick_add_window, bg=self.bg_color)
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        tk.Button(button_frame, text="Cancel", command=quick_add_window.destroy, 
                 bg="#e74c3c", fg="white").pack(side=tk.LEFT, padx=10)
        
        tk.Button(button_frame, text="Add Selected", command=lambda: self.add_selected_food(
            meal_type_var.get(), 
            food_list.selection(), 
            common_foods, 
            quick_add_window
        ), bg=self.secondary_color, fg="white").pack(side=tk.LEFT, padx=10)
    
    def add_selected_food(self, meal_type, selection, common_foods, window):
        """Add the selected food from the quick add list"""
        if not selection:
            messagebox.showwarning("No Selection", "Please select a food item.")
            return
        
        try:
            selected_index = int(selection[0])
            food = common_foods[selected_index]
            
            self.save_meal(
                meal_type, 
                food["name"], 
                food["calories"], 
                food["protein"], 
                food["carbs"], 
                food["fats"], 
                window
            )
            
        except (IndexError, ValueError) as e:
            print(f"Error selecting food: {e}")
            messagebox.showerror("Error", "Error adding selected food.")
    
    def save_meal(self, meal_type, food_name, calories, protein, carbs, fats, window):
        """Save meal to database"""
        # Validate inputs
        if not food_name:
            messagebox.showwarning("Validation Error", "Please enter a food name.")
            return
        
        try:
            conn = sqlite3.connect('data/fitness_tracker.db')
            cursor = conn.cursor()
            
            date_str = self.selected_date.strftime('%Y-%m-%d')
            
            cursor.execute('''
            INSERT INTO meals (username, date, meal_type, food_name, calories, protein, carbs, fats)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (self.username, date_str, meal_type, food_name, calories, protein, carbs, fats))
            
            conn.commit()
            conn.close()
            
            # Close the window
            window.destroy()
            
            # Refresh the display
            self.refresh_data()
            
            # Make sure the persistent buttons are still visible
            self.persistent_button_frame.lift()
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            messagebox.showerror("Database Error", "Error saving meal to database.")
    
    def delete_meal(self):
        """Delete the selected meal"""
        selection = self.meal_log.selection()
        
        if not selection:
            messagebox.showwarning("No Selection", "Please select a meal to delete.")
            return
        
        confirmed = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this meal?")
        
        if confirmed:
            try:
                conn = sqlite3.connect('data/fitness_tracker.db')
                cursor = conn.cursor()
                
                for meal_id in selection:
                    cursor.execute('DELETE FROM meals WHERE id = ?', (meal_id,))
                
                conn.commit()
                conn.close()
                
                # Refresh the display
                self.refresh_data()
                
            except sqlite3.Error as e:
                print(f"Database error: {e}")
                messagebox.showerror("Database Error", "Error deleting meal from database.")
    
    def set_calorie_goal(self):
        """Open dialog to set calorie goal"""
        goal_window = tk.Toplevel(self.parent)
        goal_window.title("Set Calorie Goal")
        goal_window.geometry("300x150")
        goal_window.resizable(False, False)
        goal_window.configure(bg=self.bg_color)
        goal_window.transient(self.parent)
        goal_window.grab_set()
        
        # Goal entry
        tk.Label(goal_window, text="Daily Calorie Goal:", bg=self.bg_color).pack(pady=10)
        goal_var = tk.IntVar(value=self.calorie_goal)
        goal_entry = tk.Entry(goal_window, textvariable=goal_var, width=10)
        goal_entry.pack(pady=10)
        
        # Buttons
        button_frame = tk.Frame(goal_window, bg=self.bg_color)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="Cancel", command=goal_window.destroy, 
                 bg="#e74c3c", fg="white").pack(side=tk.LEFT, padx=10)
        
        tk.Button(button_frame, text="Save", command=lambda: self.save_calorie_goal(goal_var.get(), goal_window), 
                 bg=self.secondary_color, fg="white").pack(side=tk.LEFT, padx=10)
    
    def save_calorie_goal(self, goal, window):
        """Save calorie goal to database"""
        if goal <= 0:
            messagebox.showwarning("Validation Error", "Please enter a positive calorie goal.")
            return
        
        try:
            conn = sqlite3.connect('data/fitness_tracker.db')
            cursor = conn.cursor()
            
            cursor.execute('''
            UPDATE diet_goals SET calorie_goal = ? WHERE username = ?
            ''', (goal, self.username))
            
            conn.commit()
            conn.close()
            
            # Update local variable
            self.calorie_goal = goal
            self.calorie_goal_label.config(text=f"{self.calorie_goal} kcal")
            
            # Close window
            window.destroy()
            
            # Refresh data
            self.refresh_data()
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            messagebox.showerror("Database Error", "Error saving calorie goal to database.")
    
    def update_macronutrient_chart(self):
        """Update the macronutrient pie chart"""
        # Clear previous chart
        for widget in self.macro_frame.winfo_children():
            widget.destroy()
        
        # Calculate total macros for the day
        total_protein = sum(meal['protein'] for meal in self.meals_data)
        total_carbs = sum(meal['carbs'] for meal in self.meals_data)
        total_fats = sum(meal['fats'] for meal in self.meals_data)
        
        # If no data, show placeholder
        if total_protein == 0 and total_carbs == 0 and total_fats == 0:
            tk.Label(self.macro_frame, text="No macronutrient data for today", 
                    bg=self.bg_color).pack(expand=True)
            return
        
        # Calculate calories from each macro
        protein_cals = total_protein * 4
        carbs_cals = total_carbs * 4
        fats_cals = total_fats * 9
        total_cals = protein_cals + carbs_cals + fats_cals
        
        # If no calories, skip chart
        if total_cals == 0:
            return
            
        # Create pie chart using matplotlib
        try:
            # Create a figure and axis
            figure = Figure(figsize=(3, 1.25), dpi=100)
            ax = figure.add_subplot(111)
            
            # Data for pie chart
            labels = ['Protein', 'Carbs', 'Fats']
            sizes = [protein_cals, carbs_cals, fats_cals]
            colors = ['#ff9999','#66b3ff','#99ff99']
            
            # Plot
            wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', 
                                             startangle=90, wedgeprops={'edgecolor': 'w'})
            ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
            
            # Make labels more readable
            for text in texts:
                text.set_fontsize(8)
            for autotext in autotexts:
                autotext.set_fontsize(8)
                autotext.set_color('black')
            
            # Add title
            ax.set_title("", fontsize=10)
            
            # Create canvas
            canvas = FigureCanvasTkAgg(figure, master=self.macro_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
        except Exception as e:
            print(f"Error creating chart: {e}")
            tk.Label(self.macro_frame, text="Error creating macronutrient chart", 
                    bg=self.bg_color).pack(expand=True)
    
    # def update_weekly_graph(self):
    #     """Update the weekly calorie graph"""
    #     try:
    #         # Clear previous chart
    #         for widget in self.graph_frame.winfo_children():
    #             widget.destroy()
                
    #         # Get data for the past 7 days
    #         end_date = self.selected_date
    #         start_date = end_date - datetime.timedelta(days=6)
            
    #         conn = sqlite3.connect('data/fitness_tracker.db')
    #         cursor = conn.cursor()
            
    #         dates = []
    #         calories = []
    #         goal_line = []
            
    #         current_date = start_date
    #         while current_date <= end_date:
    #             date_str = current_date.strftime('%Y-%m-%d')
    #             dates.append(date_str)
                
    #             # Get total calories for the day
    #             cursor.execute('''
    #             SELECT SUM(calories) FROM meals 
    #             WHERE username = ? AND date = ?
    #             ''', (self.username, date_str))
                
    #             result = cursor.fetchone()[0]
    #             day_calories = result if result else 0
    #             calories.append(day_calories)
                
    #             # Add goal for comparison
    #             goal_line.append(self.calorie_goal)
                
    #             current_date += datetime.timedelta(days=1)
            
    #         conn.close()
            
    #         # Create bar chart
    #         figure = Figure(figsize=(8, 3), dpi=100)
    #         ax = figure.add_subplot(111)
            
    #         # Convert dates to shorter format for display
    #         short_dates = [datetime.datetime.strptime(date, '%Y-%m-%d').strftime('%a %d') for date in dates]
            
    #         # Plot bars
    #         bars = ax.bar(short_dates, calories, color=self.primary_color, alpha=0.7)
            
    #         # Plot goal line
    #         ax.plot(short_dates, goal_line, 'r--', label=f'Goal ({self.calorie_goal} kcal)')
            
    #         # Set labels and title
    #         ax.set_ylabel('Calories')
    #         ax.set_title('Weekly Calorie Intake')
            
    #         # Rotate x-axis labels for readability
    #         plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
            
    #         # Add legend
    #         ax.legend()
            
    #         # Adjust layout
    #         figure.tight_layout()
            
    #         # Create canvas
    #         canvas = FigureCanvasTkAgg(figure, master=self.graph_frame)
    #         canvas.draw()
    #         canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
    #     except Exception as e:
    #         print(f"Error creating weekly graph: {e}")
    #         tk.Label(self.graph_frame, text="Error creating weekly graph", 
    #                 bg=self.bg_color).pack(expand=True)
    
    # def update_insights(self):
    #     """Update the nutritional insights section"""
    #     try:
    #         # Clear current insights
    #         self.insights_text.config(state=tk.NORMAL)
    #         self.insights_text.delete(1.0, tk.END)
            
    #         # If no meals data, show default message
    #         if not self.meals_data:
    #             self.insights_text.insert(tk.END, "No meal data available for the selected date. Add meals to see nutritional insights.")
    #             self.insights_text.config(state=tk.DISABLED)
    #             return
            
    #         # Calculate totals
    #         total_calories = sum(meal['calories'] for meal in self.meals_data)
    #         total_protein = sum(meal['protein'] for meal in self.meals_data)
    #         total_carbs = sum(meal['carbs'] for meal in self.meals_data)
    #         total_fats = sum(meal['fats'] for meal in self.meals_data)
            
    #         # Calculate calorie breakdown
    #         protein_cals = total_protein * 4
    #         carbs_cals = total_carbs * 4
    #         fats_cals = total_fats * 9
            
    #         # Check if data for weekly analysis
    #         end_date = self.selected_date
    #         start_date = end_date - datetime.timedelta(days=6)
            
    #         conn = sqlite3.connect('data/fitness_tracker.db')
    #         cursor = conn.cursor()
            
    #         # Get average calories for the past week
    #         cursor.execute('''
    #         SELECT AVG(daily_total) FROM (
    #             SELECT date, SUM(calories) as daily_total 
    #             FROM meals 
    #             WHERE username = ? AND date BETWEEN ? AND ?
    #             GROUP BY date
    #         )
    #         ''', (self.username, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
            
    #         avg_calories = cursor.fetchone()[0]
    #         avg_calories = avg_calories if avg_calories else 0
            
    #         # Generate insights text
    #         insights = "Nutritional Analysis:\n\n"
            
    #         # Calorie insights
    #         insights += f"• Daily Calories: {total_calories} kcal"
            
    #         if total_calories > self.calorie_goal:
    #             insights += f" (↑ {total_calories - self.calorie_goal} above goal)\n"
    #         elif total_calories < self.calorie_goal:
    #             insights += f" (↓ {self.calorie_goal - total_calories} below goal)\n"
    #         else:
    #             insights += " (exactly at goal)\n"
                
    #         insights += f"• Weekly Average: {avg_calories:.0f} kcal\n\n"
            
    #         # Macro breakdown
    #         insights += "Macronutrient Breakdown:\n"
    #         if total_calories > 0:
    #             insights += f"• Protein: {total_protein:.1f}g ({(protein_cals/total_calories*100):.1f}%)\n"
    #             insights += f"• Carbs: {total_carbs:.1f}g ({(carbs_cals/total_calories*100):.1f}%)\n"
    #             insights += f"• Fats: {total_fats:.1f}g ({(fats_cals/total_calories*100):.1f}%)\n\n"
    #         else:
    #             insights += "• No calorie data available\n\n"
            
    #         # Recommendations
    #         insights += "Recommendations:\n"
            
    #         # Protein recommendation (0.8g per kg body weight minimum)
    #         ideal_protein = 50  # Default recommendation
    #         if total_protein < ideal_protein:
    #             insights += f"• Consider increasing protein intake (current: {total_protein:.1f}g)\n"
            
    #         # Balance recommendation
    #         if total_calories > 0:
    #             if (protein_cals/total_calories*100) < 10:
    #                 insights += "• Your protein intake seems low relative to total calories\n"
    #             if (fats_cals/total_calories*100) > 40:
    #                 insights += "• Your fat intake is high relative to total calories\n"
    #             if (carbs_cals/total_calories*100) > 70:
    #                 insights += "• Your carbohydrate intake is very high\n"
            
    #         # Add insights to text widget
    #         self.insights_text.insert(tk.END, insights)
    #         self.insights_text.config(state=tk.DISABLED)
            
    #         # Update achievements
    #         self.update_achievements()
            
    #         conn.close()
            
    #     except Exception as e:
    #         print(f"Error generating insights: {e}")
    #         self.insights_text.insert(tk.END, "Error generating nutritional insights.")
    #         self.insights_text.config(state=tk.DISABLED)
    
    # def update_achievements(self):
    #     """Update the achievements and streaks section"""
    #     try:
    #         # Check how many days in a row the user has logged meals
    #         streak = 0
    #         check_date = self.selected_date
            
    #         conn = sqlite3.connect('data/fitness_tracker.db')
    #         cursor = conn.cursor()
            
    #         while True:
    #             date_str = check_date.strftime('%Y-%m-%d')
                
    #             cursor.execute('''
    #             SELECT COUNT(*) FROM meals 
    #             WHERE username = ? AND date = ?
    #             ''', (self.username, date_str))
                
    #             count = cursor.fetchone()[0]
                
    #             if count > 0:
    #                 streak += 1
    #                 check_date -= datetime.timedelta(days=1)
    #             else:
    #                 break
            
    #         conn.close()
            
    #         # Generate achievement text
    #         achievement_text = ""
            
    #         if streak > 1:
    #             achievement_text += f"🔥 {streak}-day logging streak!\n"
            
    #         # Check for tracking achievements
    #         total_meals = len(self.meals_data)
    #         if total_meals >= 3:
    #             achievement_text += "✅ Tracked all main meals today\n"
            
    #         # Check for goal achievements
    #         if self.selected_date == self.today:  # Only show for today
    #             total_calories = sum(meal['calories'] for meal in self.meals_data)
    #             if abs(total_calories - self.calorie_goal) <= 100:
    #                 achievement_text += "🎯 Hit calorie goal (±100 kcal)\n"
            
    #         # If no achievements, show a message
    #         if not achievement_text:
    #             achievement_text = "Keep tracking your meals to earn achievements!"
            
    #         # Update label
    #         self.achievement_label.config(text=achievement_text)
            
    #     except Exception as e:
    #         print(f"Error updating achievements: {e}")
    #         self.achievement_label.config(text="Error updating achievements")
    
    def setup_hydration_tracker(self):
        # Create a frame for the hydration tracker
        hydration_frame = tk.LabelFrame(self.right_frame, text="Hydration Tracker", padx=10, pady=10, bg=self.bg_color)
        hydration_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Hydration goal
        goal_frame = tk.Frame(hydration_frame, bg=self.bg_color)
        goal_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(goal_frame, text="Daily Hydration Goal:", bg=self.bg_color).pack(side=tk.LEFT, padx=5)
        self.hydration_goal_label = tk.Label(goal_frame, text=f"{self.hydration_goal} ml", bg=self.bg_color)
        self.hydration_goal_label.pack(side=tk.LEFT, padx=5)
        
        tk.Button(goal_frame, text="Set Goal", command=self.set_hydration_goal, 
                 bg=self.primary_color, fg="white").pack(side=tk.RIGHT, padx=5)
        
        # Hydration progress
        progress_frame = tk.Frame(hydration_frame, bg=self.bg_color)
        progress_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(progress_frame, text="Today's Hydration:", bg=self.bg_color).pack(side=tk.LEFT, padx=5)
        self.hydration_progress_label = tk.Label(progress_frame, text="0/2000 ml", bg=self.bg_color)
        self.hydration_progress_label.pack(side=tk.LEFT, padx=5)
        
        # Hydration progress bar
        self.hydration_progress = ttk.Progressbar(hydration_frame, orient="horizontal", length=300, mode="determinate")
        self.hydration_progress.pack(fill=tk.X, pady=5)
        
        # Water bottle visualization frame
        self.bottle_frame = tk.Frame(hydration_frame, bg=self.bg_color, height=200)
        self.bottle_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Quick add water buttons
        button_frame = tk.Frame(hydration_frame, bg=self.bg_color)
        button_frame.pack(fill=tk.X, pady=5)
        
        amounts = [100, 250, 500, 1000]
        for amount in amounts:
            tk.Button(button_frame, text=f"+{amount} ml", command=lambda amt=amount: self.add_water(amt),
                     bg=self.primary_color, fg="white").pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="Custom Amount", command=self.add_custom_water,
                 bg=self.secondary_color, fg="white").pack(side=tk.RIGHT, padx=5)
        
    def load_hydration(self):
        """Load hydration data for the selected date"""
        try:
            conn = sqlite3.connect('data/fitness_tracker.db')
            cursor = conn.cursor()
            
            date_str = self.selected_date.strftime('%Y-%m-%d')
            
            cursor.execute('''
            SELECT SUM(amount) FROM hydration
            WHERE username = ? AND date = ?
            ''', (self.username, date_str))
            
            result = cursor.fetchone()
            total_hydration = result[0] if result[0] else 0
            
            conn.close()
            
            # Update hydration progress
            self.update_hydration_progress(total_hydration)
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            messagebox.showerror("Database Error", "Error loading hydration data from database.")
    
    def update_hydration_progress(self, total_hydration):
        """Update the hydration progress display"""
        # Update label
        self.hydration_progress_label.config(text=f"{total_hydration}/{self.hydration_goal} ml")
        
        # Update progress bar
        progress_percentage = min(100, (total_hydration / self.hydration_goal) * 100)
        self.hydration_progress["value"] = progress_percentage
        
        # Update water bottle visualization
        self.update_water_bottle(total_hydration)
    
    def update_water_bottle(self, total_hydration):
        """Update the water bottle visualization"""
        # Clear previous visualization
        for widget in self.bottle_frame.winfo_children():
            widget.destroy()
        
        # Create water bottle outline
        bottle_height = 180
        bottle_width = 100
        bottle = tk.Canvas(self.bottle_frame, width=bottle_width, height=bottle_height, bg=self.bg_color, highlightthickness=0)
        bottle.pack()
        
        # Draw bottle outline
        bottle.create_rectangle(10, 20, 90, 170, outline="blue", width=2)
        bottle.create_polygon(10, 20, 40, 0, 60, 0, 90, 20, outline="blue", width=2, fill="")
        
        # Calculate water level
        water_height = min(150, (total_hydration / self.hydration_goal) * 150)
        
        # Draw water level
        bottle.create_rectangle(12, 170 - water_height, 88, 170, fill="lightblue", outline="")
        
        # Add text showing current amount
        bottle.create_text(50, 185, text=f"{total_hydration} ml", fill="blue")
    
    def add_water(self, amount):
        """Add water to the hydration tracker"""
        try:
            conn = sqlite3.connect('data/fitness_tracker.db')
            cursor = conn.cursor()
            
            date_str = self.selected_date.strftime('%Y-%m-%d')
            
            cursor.execute('''
            INSERT INTO hydration (username, date, amount)
            VALUES (?, ?, ?)
            ''', (self.username, date_str, amount))
            
            conn.commit()
            conn.close()
            
            # Refresh the display
            self.load_hydration()
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            messagebox.showerror("Database Error", "Error adding water to database.")
    
    def add_custom_water(self):
        """Add custom amount of water"""
        amount = simpledialog.askinteger("Custom Water Amount", "Enter amount of water (ml):", 
                                         parent=self.parent, minvalue=1, maxvalue=5000)
        if amount:
            self.add_water(amount)
    
    def set_hydration_goal(self):
        """Set new hydration goal"""
        new_goal = simpledialog.askinteger("Set Hydration Goal", "Enter new daily hydration goal (ml):", 
                                           parent=self.parent, minvalue=500, maxvalue=10000)
        if new_goal:
            self.hydration_goal = new_goal
            self.hydration_goal_label.config(text=f"{self.hydration_goal} ml")
            self.save_user_goals()
            self.refresh_data()
            
    def save_user_goals(self):
        """Save user goals to database"""
        try:
            conn = sqlite3.connect('data/fitness_tracker.db')
            cursor = conn.cursor()
            
            cursor.execute('''
            UPDATE diet_goals
            SET calorie_goal = ?, hydration_goal = ?
            WHERE username = ?
            ''', (self.calorie_goal, self.hydration_goal, self.username))
            
            conn.commit()
            conn.close()
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            messagebox.showerror("Database Error", "Error saving user goals to database.")