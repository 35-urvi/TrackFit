import tkinter as tk
from tkinter import ttk, font
import sqlite3
import os
from profile_tab import ProfileTab
from workout_tab import WorkoutTab
from diet_tab import DietTab
from sleep_tab import SleepTab
from about_tab import AboutTab

class FitnessTrackerApp:
    def __init__(self, root, username=None):
        self.root = root
        self.root.title("TrackFit")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        # Store username
        self.username = username
        
        # Initialize the database
        self.initialize_database()
        
        # Set up custom fonts
        self.setup_fonts()
        
        # Set theme colors
        self.primary_color = "#3498db"  # Blue
        self.secondary_color = "#2ecc71"  # Green
        self.bg_color = "#f9f9f9"  # Light Gray
        self.text_color = "#333333"  # Dark Gray
        
        # Configure root window
        self.root.configure(bg=self.bg_color)
        
        # Create main frames
        self.setup_frames()
        
        # Create navigation bar
        self.setup_navbar()
        
        # Initialize content (default to Profile tab)
        self.current_tab = None
        self.show_tab("Profile")
        
    def initialize_database(self):
        # Create database directory if it doesn't exist
        if not os.path.exists('data'):
            os.makedirs('data')
            
        # Connect to SQLite database
        conn = sqlite3.connect('data/fitness_tracker.db')
        cursor = conn.cursor()
        
        # Create necessary tables if they don't exist
        
        # Profile table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS profile (
            id INTEGER PRIMARY KEY,
            username TEXT,
            name TEXT,
            age INTEGER,
            gender TEXT,
            height REAL,
            weight REAL,
            daily_workout_goal INTEGER,
            UNIQUE(username)
        )
        ''')
        
        # Workout table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS workouts (
            id INTEGER PRIMARY KEY,
            username TEXT,
            date TEXT,
            level TEXT,
            duration INTEGER,
            calories_burned INTEGER,
            completed INTEGER
        )
        ''')
        
        # Workout exercises table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS workout_exercises (
            id INTEGER PRIMARY KEY,
            workout_id INTEGER,
            exercise_name TEXT,
            sets INTEGER,
            reps INTEGER,
            FOREIGN KEY (workout_id) REFERENCES workouts (id)
        )
        ''')
        
        # Diet table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS meals (
            id INTEGER PRIMARY KEY,
            username TEXT,
            date TEXT,
            meal_type TEXT,
            food_name TEXT,
            calories INTEGER,
            protein REAL,
            carbs REAL,
            fats REAL
        )
        ''')
        
        # Hydration table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS hydration (
            id INTEGER PRIMARY KEY,
            username TEXT,
            date TEXT,
            amount INTEGER
        )
        ''')
        
        # # Sleep table
        # cursor.execute('''
        # CREATE TABLE IF NOT EXISTS sleep (
        #     id INTEGER PRIMARY KEY,
        #     username TEXT,
        #     date TEXT,
        #     hours REAL,
        #     quality TEXT
        # )
        # ''')
         # Sleep table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS sleep (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            date TEXT NOT NULL,
            hours REAL NOT NULL,
            quality TEXT NOT NULL,
            notes TEXT,
            UNIQUE(username, date)
        )
        ''')
        
        # Commit changes and close connection
        conn.commit()
        conn.close()
    
    def setup_fonts(self):
        # Define custom fonts
        self.title_font = font.Font(family="Helvetica", size=16, weight="bold")
        self.header_font = font.Font(family="Helvetica", size=12, weight="bold")
        self.normal_font = font.Font(family="Helvetica", size=10)
        self.button_font = font.Font(family="Helvetica", size=10, weight="bold")
    
    def setup_frames(self):
        # Create main container frame
        self.main_frame = tk.Frame(self.root, bg=self.bg_color)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create navbar frame
        self.navbar_frame = tk.Frame(self.main_frame, bg=self.primary_color, height=60)
        self.navbar_frame.pack(fill=tk.X, side=tk.TOP)
        
        # Create content frame
        self.content_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    def setup_navbar(self):
        # App title
        title_label = tk.Label(self.navbar_frame, text="TRACKFIT", 
                               font=self.title_font, bg=self.primary_color, fg="white")
        title_label.pack(side=tk.LEFT, padx=20, pady=10)
        
        # Navigation buttons
        self.nav_buttons = {}
        
        tabs = ["Profile", "Workout", "Diet", "Sleep", "About"]
        
        for tab in tabs:
            self.nav_buttons[tab] = tk.Button(
                self.navbar_frame, 
                text=tab, 
                font=self.button_font,
                bg=self.primary_color,
                fg="white",
                bd=0,
                highlightthickness=0,
                padx=15,
                pady=5,
                activebackground="#2980b9",
                activeforeground="white",
                command=lambda t=tab: self.show_tab(t)
            )
            self.nav_buttons[tab].pack(side=tk.LEFT, padx=5, pady=10)
        
        # Add username display and logout button if logged in
        if self.username:
            # Spacer
            spacer = tk.Label(self.navbar_frame, text="", bg=self.primary_color)
            spacer.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            # Username display
            user_label = tk.Label(
                self.navbar_frame, 
                text=f"User: {self.username}", 
                font=self.normal_font,
                bg=self.primary_color,
                fg="white"
            )
            user_label.pack(side=tk.LEFT, padx=10)
            
            # Logout button
            logout_button = tk.Button(
                self.navbar_frame, 
                text="Logout", 
                font=self.button_font,
                bg="#e74c3c",  # Red
                fg="white",
                bd=0,
                highlightthickness=0,
                padx=10,
                pady=5,
                activebackground="#c0392b",
                activeforeground="white",
                command=self.logout
            )
            logout_button.pack(side=tk.LEFT, padx=10, pady=10)
    
    def logout(self):
        """Handle user logout"""
        # Destroy current window
        self.root.destroy()
        
        # Create new window and start auth system
        new_root = tk.Tk()
        from login_signup import AuthenticationSystem
        auth_system = AuthenticationSystem(new_root, None)
        new_root.mainloop()
    
    def show_tab(self, tab_name):
        # Clear current content
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Update button styles
        for tab, button in self.nav_buttons.items():
            if tab == tab_name:
                button.configure(bg="#2980b9")
            else:
                button.configure(bg=self.primary_color)
        
        # Create new content based on selected tab
        if tab_name == "Profile":
            self.current_tab = ProfileTab(self.content_frame, self.bg_color, self.username)
        elif tab_name == "Workout":
            self.current_tab = WorkoutTab(self.content_frame, self.bg_color, self.username)
        elif tab_name == "Diet":
            self.current_tab = DietTab(self.content_frame, self.bg_color, self.username)
        elif tab_name == "Sleep":
            self.current_tab = SleepTab(self.content_frame, self.bg_color, self.username)
        elif tab_name == "About":
            self.current_tab = AboutTab(self.content_frame, self.bg_color)
    

if __name__ == "__main__":
    # Start with authentication system
    root = tk.Tk()
    from login_signup import AuthenticationSystem
    auth_system = AuthenticationSystem(root, None)
    root.mainloop()