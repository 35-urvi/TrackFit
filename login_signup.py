import tkinter as tk
from tkinter import ttk, font, messagebox
import sqlite3
import hashlib
import os
import re
from functools import *

class AuthenticationSystem:
    def __init__(self, root, app_callback):
        self.root = root
        self.app_callback = app_callback  # Callback to initialize main app after login
        
        # Set theme colors (matching the main app)
        self.primary_color = "#3498db"  # Blue
        self.secondary_color = "#2ecc71"  # Green
        self.bg_color = "#f9f9f9"  # Light Gray
        self.text_color = "#333333"  # Dark Gray
        
        # Setup fonts
        self.title_font = font.Font(family="Helvetica", size=16, weight="bold")
        self.header_font = font.Font(family="Helvetica", size=12, weight="bold")
        self.normal_font = font.Font(family="Helvetica", size=10)
        self.button_font = font.Font(family="Helvetica", size=10, weight="bold")
        
        # Configure root window
        self.root.title("TrackFit - Login")
        self.root.geometry("500x500")
        self.root.minsize(400, 400)
        self.root.configure(bg=self.bg_color)
        
        # Create authentication database if needed
        self.initialize_auth_database()
        
        # Create main container frame
        self.main_frame = tk.Frame(self.root, bg=self.bg_color)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Start with login form
        self.show_login_form()
    
    def initialize_auth_database(self):
        # Create database directory if it doesn't exist
        if not os.path.exists('data'):
            os.makedirs('data')
            
        # Connect to SQLite database
        conn = sqlite3.connect('data/fitness_tracker.db')
        cursor = conn.cursor()
        
        # Create users table if it doesn't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            email TEXT UNIQUE,
            password_hash TEXT,
            salt TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Commit changes and close connection
        conn.commit()
        conn.close()
    
    def show_login_form(self):
        # Clear current content
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        # App logo/title
        title_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        title_frame.pack(fill=tk.X, pady=20)
        
        logo_label = tk.Label(title_frame, text="TRACKFIT", 
                              font=self.title_font, bg=self.bg_color, fg=self.primary_color)
        logo_label.pack()
        
        subtitle_label = tk.Label(title_frame, text="Login to your account", 
                                 font=self.header_font, bg=self.bg_color, fg=self.text_color)
        subtitle_label.pack(pady=10)
        
        # Login form
        form_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        form_frame.pack(fill=tk.X, pady=20)
        
        # Username
        username_frame = tk.Frame(form_frame, bg=self.bg_color)
        username_frame.pack(fill=tk.X, pady=10)
        
        username_label = tk.Label(username_frame, text="Username:", 
                                 font=self.normal_font, bg=self.bg_color, fg=self.text_color,
                                 anchor="w", width=15)
        username_label.pack(side=tk.LEFT)
        
        self.username_entry = tk.Entry(username_frame, font=self.normal_font, width=25)
        self.username_entry.pack(side=tk.LEFT, ipady=3)
        
        # Password
        password_frame = tk.Frame(form_frame, bg=self.bg_color)
        password_frame.pack(fill=tk.X, pady=10)
        
        password_label = tk.Label(password_frame, text="Password:", 
                                 font=self.normal_font, bg=self.bg_color, fg=self.text_color,
                                 anchor="w", width=15)
        password_label.pack(side=tk.LEFT)
        
        self.password_entry = tk.Entry(password_frame, font=self.normal_font, width=25, show="•")
        self.password_entry.pack(side=tk.LEFT, ipady=3)
        
        # Login button
        button_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        button_frame.pack(fill=tk.X, pady=20)
        
        login_button = tk.Button(
            button_frame, text="Login", command=self.login, 
            font=self.button_font, bg=self.primary_color, fg="white",
            padx=20, pady=8, bd=0, highlightthickness=0
        )
        login_button.pack(pady=10)
        
        # Signup link
        signup_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        signup_frame.pack(fill=tk.X, pady=10)
        
        signup_label = tk.Label(signup_frame, text="Don't have an account?", 
                               font=self.normal_font, bg=self.bg_color, fg=self.text_color)
        signup_label.pack(side=tk.LEFT, padx=(100, 0))
        
        signup_link = tk.Label(signup_frame, text="Sign up", 
                              font=self.normal_font, bg=self.bg_color, fg=self.primary_color,
                              cursor="hand2")
        signup_link.pack(side=tk.LEFT, padx=5)
        signup_link.bind("<Button-1>", lambda e: self.show_signup_form())
    
    def show_signup_form(self):
        # Clear current content
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        # App logo/title
        title_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        title_frame.pack(fill=tk.X, pady=20)
        
        logo_label = tk.Label(title_frame, text="TRACKFIT", 
                              font=self.title_font, bg=self.bg_color, fg=self.primary_color)
        logo_label.pack()
        
        subtitle_label = tk.Label(title_frame, text="Create a new account", 
                                 font=self.header_font, bg=self.bg_color, fg=self.text_color)
        subtitle_label.pack(pady=10)
        
        # Signup form
        form_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        form_frame.pack(fill=tk.X, pady=10)
        
        # Username
        username_frame = tk.Frame(form_frame, bg=self.bg_color)
        username_frame.pack(fill=tk.X, pady=8)
        
        username_label = tk.Label(username_frame, text="Username:", 
                                 font=self.normal_font, bg=self.bg_color, fg=self.text_color,
                                 anchor="w", width=15)
        username_label.pack(side=tk.LEFT)
        
        self.new_username_entry = tk.Entry(username_frame, font=self.normal_font, width=25)
        self.new_username_entry.pack(side=tk.LEFT, ipady=3)
        
        # Email
        email_frame = tk.Frame(form_frame, bg=self.bg_color)
        email_frame.pack(fill=tk.X, pady=8)
        
        email_label = tk.Label(email_frame, text="Email:", 
                              font=self.normal_font, bg=self.bg_color, fg=self.text_color,
                              anchor="w", width=15)
        email_label.pack(side=tk.LEFT)
        
        self.email_entry = tk.Entry(email_frame, font=self.normal_font, width=25)
        self.email_entry.pack(side=tk.LEFT, ipady=3)
        
        # Password
        password_frame = tk.Frame(form_frame, bg=self.bg_color)
        password_frame.pack(fill=tk.X, pady=8)
        
        password_label = tk.Label(password_frame, text="Password:", 
                                 font=self.normal_font, bg=self.bg_color, fg=self.text_color,
                                 anchor="w", width=15)
        password_label.pack(side=tk.LEFT)
        
        self.new_password_entry = tk.Entry(password_frame, font=self.normal_font, width=25, show="•")
        self.new_password_entry.pack(side=tk.LEFT, ipady=3)
        
        # Confirm Password
        confirm_frame = tk.Frame(form_frame, bg=self.bg_color)
        confirm_frame.pack(fill=tk.X, pady=8)
        
        confirm_label = tk.Label(confirm_frame, text="Confirm Password:", 
                                font=self.normal_font, bg=self.bg_color, fg=self.text_color,
                                anchor="w", width=15)
        confirm_label.pack(side=tk.LEFT)
        
        self.confirm_password_entry = tk.Entry(confirm_frame, font=self.normal_font, width=25, show="•")
        self.confirm_password_entry.pack(side=tk.LEFT, ipady=3)
        
        # Register button
        button_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        button_frame.pack(fill=tk.X, pady=15)
        
        register_button = tk.Button(
            button_frame, text="Sign Up", command=self.register, 
            font=self.button_font, bg=self.secondary_color, fg="white",
            padx=20, pady=8, bd=0, highlightthickness=0
        )
        register_button.pack(pady=10)
        
        # Login link
        login_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        login_frame.pack(fill=tk.X, pady=10)
        
        login_label = tk.Label(login_frame, text="Already have an account?", 
                              font=self.normal_font, bg=self.bg_color, fg=self.text_color)
        login_label.pack(side=tk.LEFT, padx=(100, 0))
        
        login_link = tk.Label(login_frame, text="Login", 
                             font=self.normal_font, bg=self.bg_color, fg=self.primary_color,
                             cursor="hand2")
        login_link.pack(side=tk.LEFT, padx=5)
        login_link.bind("<Button-1>", lambda e: self.show_login_form())
    
    def generate_salt(self):
        """Generate a random salt for password hashing"""
        return os.urandom(32).hex()
    
    def hash_password(self, password, salt):
        """Hash password with the given salt"""
        key = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        )
        return key.hex()
    
    def validate_email(self, email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return re.match(pattern, email) is not None
    
    def register(self):
        """Handle user registration"""
        username = self.new_username_entry.get().strip()
        email = self.email_entry.get().strip()
        password = self.new_password_entry.get()
        confirm_password = self.confirm_password_entry.get()
        
        # Validate inputs
        if not username or not email or not password or not confirm_password:
            messagebox.showerror("Error", "All fields are required")
            return
        
        if not self.validate_email(email):
            messagebox.showerror("Error", "Invalid email format")
            return
        
        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match")
            return
        
        if len(password) < 8:
            messagebox.showerror("Error", "Password must be at least 8 characters long")
            return
        
        # Hash password with salt
        salt = self.generate_salt()
        password_hash = self.hash_password(password, salt)
        
        # Save user to database
        try:
            conn = sqlite3.connect('data/fitness_tracker.db')
            cursor = conn.cursor()
            
            cursor.execute(
                "INSERT INTO users (username, email, password_hash, salt) VALUES (?, ?, ?, ?)",
                (username, email, password_hash, salt)
            )
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", "Account created successfully! You can now login.")
            self.show_login_form()
            
        except sqlite3.IntegrityError as e:
            if "username" in str(e):
                messagebox.showerror("Error", "Username already exists")
            elif "email" in str(e):
                messagebox.showerror("Error", "Email already exists")
            else:
                messagebox.showerror("Error", "An error occurred")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def login(self):
        """Handle user login"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        # Validate inputs
        if not username or not password:
            messagebox.showerror("Error", "Username and password are required")
            return
        
        try:
            conn = sqlite3.connect('data/fitness_tracker.db')
            cursor = conn.cursor()
            
            # Get user from database
            cursor.execute(
                "SELECT password_hash, salt FROM users WHERE username = ?",
                (username,)
            )
            
            result = cursor.fetchone()
            conn.close()
            
            if not result:
                messagebox.showerror("Error", "Invalid username or password")
                return
            
            stored_hash, salt = result
            
            # Verify password
            input_hash = self.hash_password(password, salt)
            
            if input_hash == stored_hash:
                messagebox.showinfo("Success", "Login successful!")
                
                # Initialize main app
                self.initialize_main_app(username)
            else:
                messagebox.showerror("Error", "Invalid username or password")
                
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def initialize_main_app(self, username):
        """Initialize the main application after successful login"""
        # Clear login window
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Update window properties
        self.root.title("TrackFit")
        self.root.geometry("900x700")
        
        # Initialize the main app
        from fitness_tracker_main import FitnessTrackerApp
        app = FitnessTrackerApp(self.root, username)


# Modify the main script to include authentication system
def main():
    root = tk.Tk()
    auth_system = AuthenticationSystem(root, None)
    root.mainloop()

if __name__ == "__main__":
    main()