import tkinter as tk
from tkinter import ttk, font
import webbrowser
from PIL import Image, ImageTk
import os

class AboutTab:
    def __init__(self, parent_frame, bg_color, username=None):
        self.parent_frame = parent_frame
        self.bg_color = bg_color
        self.username = username
        
        # Set up fonts
        self.title_font = font.Font(family="Helvetica", size=16, weight="bold")
        self.header_font = font.Font(family="Helvetica", size=12, weight="bold")
        self.normal_font = font.Font(family="Helvetica", size=10)
        self.button_font = font.Font(family="Helvetica", size=10, weight="bold")
        
        # Theme colors (matching main app)
        self.primary_color = "#3498db"  # Blue
        self.secondary_color = "#2ecc71"  # Green
        self.text_color = "#333333"  # Dark Gray
        
        # Create about tab content
        self.create_widgets()
    
    def create_widgets(self):
        # Main container with scrollbar
        self.main_container = tk.Frame(self.parent_frame, bg=self.bg_color)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Create a canvas with scrollbar for content
        self.canvas = tk.Canvas(self.main_container, bg=self.bg_color, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.main_container, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create a frame inside the canvas for the content
        self.content_frame = tk.Frame(self.canvas, bg=self.bg_color)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.content_frame, anchor="nw")
        
        # Configure canvas scrolling
        self.content_frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        
        # Add content sections
        self.add_app_info()
        self.add_features()
        self.add_developer_info()
        # self.add_version_history()
        self.add_contact_info()
    
    def on_frame_configure(self, event):
        # Update the scrollregion when the inner frame changes size
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def on_canvas_configure(self, event):
        # Resize the inner frame to match the canvas
        width = event.width
        self.canvas.itemconfig(self.canvas_window, width=width)
    
    def add_app_info(self):
        # App logo section
        logo_frame = tk.Frame(self.content_frame, bg=self.bg_color)
        logo_frame.pack(fill=tk.X, pady=(20, 10))
        
        try:
            # Try to load the app logo (adjust path as needed)
            logo_path = os.path.join("assets", "logo.png")
            logo_image = Image.open(logo_path)
            logo_image = logo_image.resize((120, 120))
            logo_photo = ImageTk.PhotoImage(logo_image)
            
            logo_label = tk.Label(logo_frame, image=logo_photo, bg=self.bg_color)
            logo_label.image = logo_photo  # Keep a reference
            logo_label.pack()
        except Exception:
            # If logo fails to load, show a placeholder text
            logo_placeholder = tk.Label(
                logo_frame, 
                text="FITNESS TRACKER",
                font=self.title_font,
                bg=self.bg_color,
                fg=self.primary_color
            )
            logo_placeholder.pack()
        
        # App name and version
        app_name_label = tk.Label(
            self.content_frame, 
            text="TrackFit",
            font=self.title_font,
            bg=self.bg_color,
            fg=self.primary_color
        )
        app_name_label.pack(pady=(10, 5))
        
        version_label = tk.Label(
            self.content_frame, 
            text="Version 1.0.0",
            font=self.normal_font,
            bg=self.bg_color,
            fg=self.text_color
        )
        version_label.pack(pady=(0, 20))
        
        # App description
        description_frame = tk.Frame(self.content_frame, bg=self.bg_color)
        description_frame.pack(fill=tk.X, padx=50, pady=(0, 20))
        
        description_text = (
            "TrackFit is your all-in-one fitness companion designed to help you "
            "achieve your health and wellness goals. Track workouts, monitor "
            "nutrition, analyze sleep patterns, and maintain a comprehensive "
            "fitness profile—all in one intuitive application."
            "\n\n"
            "Whether you're a beginner just starting your fitness journey or "
            "an experienced athlete looking to optimize your performance, "
            "TrackFit provides the tools and insights you need to succeed."
        )
        
        description_label = tk.Label(
            description_frame, 
            text=description_text,
            font=self.normal_font,
            bg=self.bg_color,
            fg=self.text_color,
            justify=tk.CENTER,
            wraplength=600
        )
        description_label.pack(fill=tk.X)
        
        # Separator
        ttk.Separator(self.content_frame, orient="horizontal").pack(fill=tk.X, padx=50, pady=10)
    
    def add_features(self):
        # Features section
        features_label = tk.Label(
            self.content_frame, 
            text="Key Features",
            font=self.header_font,
            bg=self.bg_color,
            fg=self.primary_color
        )
        features_label.pack(pady=(10, 15))
        
        features_frame = tk.Frame(self.content_frame, bg=self.bg_color)
        features_frame.pack(fill=tk.X, padx=80, pady=(0, 20))
        
        features = [
            ("User Authentication", "Lets user create accounts and access features"),
            ("Profile Management", "Create and maintain your fitness profile with personal details and metrics"),
            ("Workout Tracking", "Log your workouts, track progress, and view exercise history"),
            ("Diet Monitoring", "Record meals, track calories and macronutrients, and monitor hydration"),
            ("Sleep Analysis", "Track sleep duration and quality to optimize recovery"),
            ("Goal Setting", "Set personalized fitness goals and track your achievements")
        ]
        
        for i, (feature, description) in enumerate(features):
            feature_frame = tk.Frame(features_frame, bg=self.bg_color)
            feature_frame.pack(fill=tk.X, pady=5, anchor=tk.W)
            
            # Feature icon (dot or bullet)
            icon_label = tk.Label(
                feature_frame, 
                text="•",
                font=self.header_font,
                bg=self.bg_color,
                fg=self.secondary_color
            )
            icon_label.pack(side=tk.LEFT, padx=(0, 10))
            
            # Feature name and description
            feature_info_frame = tk.Frame(feature_frame, bg=self.bg_color)
            feature_info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            feature_name = tk.Label(
                feature_info_frame, 
                text=feature,
                font=self.header_font,
                bg=self.bg_color,
                fg=self.text_color,
                anchor=tk.W
            )
            feature_name.pack(fill=tk.X)
            
            feature_desc = tk.Label(
                feature_info_frame, 
                text=description,
                font=self.normal_font,
                bg=self.bg_color,
                fg=self.text_color,
                wraplength=500,
                justify=tk.LEFT,
                anchor=tk.W
            )
            feature_desc.pack(fill=tk.X)
        
        # Separator
        ttk.Separator(self.content_frame, orient="horizontal").pack(fill=tk.X, padx=50, pady=10)
    
    def add_developer_info(self):
        # Developer info section
        developer_label = tk.Label(
            self.content_frame, 
            text="Development Team",
            font=self.header_font,
            bg=self.bg_color,
            fg=self.primary_color
        )
        developer_label.pack(pady=(10, 15))
        
        # Developer info
        developer_frame = tk.Frame(self.content_frame, bg=self.bg_color)
        developer_frame.pack(fill=tk.X, padx=80, pady=(0, 20))
        
        # Replace with actual developer info
        dev_info = tk.Label(
            developer_frame, 
            text="Created by Urvi | Jetshree | Dhruvi",
            font=self.normal_font,
            bg=self.bg_color,
            fg=self.text_color
        )
        dev_info.pack(fill=tk.X, pady=5)
        
        # Separator
        ttk.Separator(self.content_frame, orient="horizontal").pack(fill=tk.X, padx=50, pady=10)
        
    def add_contact_info(self):
        # Contact section
        contact_label = tk.Label(
            self.content_frame, 
            text="Connect With Us",
            font=self.header_font,
            bg=self.bg_color,
            fg=self.primary_color
        )
        contact_label.pack(pady=(10, 15))
        
        # Contact buttons
        contact_frame = tk.Frame(self.content_frame, bg=self.bg_color)
        contact_frame.pack(fill=tk.X, pady=(0, 30))
        
        contact_options = [
            ("Website", "https://www.yourwebsite.com", "#3498db"),
            ("GitHub", "https://github.com/yourusername/trackfit", "#333333"),
            ("Support", "mailto:support@yourwebsite.com", "#2ecc71"),
            ("Report Bug", "mailto:bugs@yourwebsite.com", "#e74c3c")
        ]
        
        for text, url, color in contact_options:
            button = tk.Button(
                contact_frame,
                text=text,
                font=self.button_font,
                bg=color,
                fg="white",
                bd=0,
                padx=15,
                pady=8,
                activebackground=self.primary_color,
                activeforeground="white",
                cursor="hand2",
                command=lambda u=url: self.open_url(u)
            )
            button.pack(side=tk.LEFT, padx=10)
        
        # Copyright
        copyright_label = tk.Label(
            self.content_frame, 
            text="© 2025 TrackFit. All rights reserved.",
            font=("Helvetica", 8),
            bg=self.bg_color,
            fg=self.text_color
        )
        copyright_label.pack(pady=(20, 30))
    
    def open_url(self, url):
        """Open URL in default browser"""
        webbrowser.open(url)


# For testing the tab independently
if __name__ == "__main__":
    root = tk.Tk()
    root.title("TrackFit - About")
    root.geometry("900x700")
    
    content_frame = tk.Frame(root, bg="#f9f9f9")
    content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    about_tab = AboutTab(content_frame, "#f9f9f9")
    
    root.mainloop()