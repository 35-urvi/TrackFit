import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import calendar
import matplotlib.dates as mdates

class SleepTab:
    def __init__(self, parent, bg_color, username):
        self.parent = parent
        self.bg_color = bg_color
        self.username = username
        
        # Set theme colors (matching main app)
        self.primary_color = "#3498db"  # Blue
        self.secondary_color = "#2ecc71"  # Green
        self.warning_color = "#e74c3c"  # Red
        self.text_color = "#333333"  # Dark Gray
        
        # Define fonts
        self.title_font = ("Helvetica", 16, "bold")
        self.header_font = ("Helvetica", 12, "bold")
        self.normal_font = ("Helvetica", 10)
        self.button_font = ("Helvetica", 10, "bold")
        
        # Create main container
        self.main_frame = tk.Frame(parent, bg=bg_color)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create different tabs
        self.log_tab = tk.Frame(self.notebook, bg=bg_color)
        self.history_tab = tk.Frame(self.notebook, bg=bg_color)
        self.analytics_tab = tk.Frame(self.notebook, bg=bg_color)
        self.recommendations_tab = tk.Frame(self.notebook, bg=bg_color)
        
        # Add tabs to notebook
        self.notebook.add(self.log_tab, text="Log Sleep")
        self.notebook.add(self.history_tab, text="History")
        self.notebook.add(self.analytics_tab, text="Analytics")
        self.notebook.add(self.recommendations_tab, text="Recommendations")
        
        # Set up each tab
        self.setup_log_tab()
        self.setup_history_tab()
        self.setup_analytics_tab()
        self.setup_recommendations_tab()
    
    def setup_log_tab(self):
        # Header
        header = tk.Label(self.log_tab, text="Log Your Sleep", font=self.title_font, 
                          bg=self.bg_color, fg=self.text_color)
        header.pack(pady=(20, 30))
        
        # Create form frame
        form_frame = tk.Frame(self.log_tab, bg=self.bg_color)
        form_frame.pack(fill=tk.BOTH, padx=50, pady=10)
        
        # Date selection
        date_frame = tk.Frame(form_frame, bg=self.bg_color)
        date_frame.pack(fill=tk.X, pady=10)
        
        date_label = tk.Label(date_frame, text="Date:", font=self.normal_font, 
                             bg=self.bg_color, fg=self.text_color, width=15, anchor='w')
        date_label.pack(side=tk.LEFT, padx=5)
        
        # Get today's date
        today = datetime.now()
        
        # Date comboboxes
        self.day_var = tk.StringVar(value=str(today.day))
        self.month_var = tk.StringVar(value=str(today.month))
        self.year_var = tk.StringVar(value=str(today.year))
        
        # Day dropdown
        day_dropdown = ttk.Combobox(date_frame, textvariable=self.day_var, width=3,
                                    values=[str(i).zfill(2) for i in range(1, 32)])
        day_dropdown.pack(side=tk.LEFT, padx=5)
        
        # Month dropdown
        month_dropdown = ttk.Combobox(date_frame, textvariable=self.month_var, width=3,
                                      values=[str(i).zfill(2) for i in range(1, 13)])
        month_dropdown.pack(side=tk.LEFT, padx=5)
        
        # Year dropdown
        year_dropdown = ttk.Combobox(date_frame, textvariable=self.year_var, width=5,
                                    values=[str(i) for i in range(today.year-5, today.year+1)])
        year_dropdown.pack(side=tk.LEFT, padx=5)
        
        # Sleep duration
        duration_frame = tk.Frame(form_frame, bg=self.bg_color)
        duration_frame.pack(fill=tk.X, pady=10)
        
        duration_label = tk.Label(duration_frame, text="Sleep Duration:", font=self.normal_font, 
                                 bg=self.bg_color, fg=self.text_color, width=15, anchor='w')
        duration_label.pack(side=tk.LEFT, padx=5)
        
        self.hours_var = tk.StringVar(value="8")
        hours_dropdown = ttk.Combobox(duration_frame, textvariable=self.hours_var, width=5,
                                    values=[str(i) for i in range(13)])
        hours_dropdown.pack(side=tk.LEFT, padx=5)
        
        hours_label = tk.Label(duration_frame, text="hours", font=self.normal_font, 
                              bg=self.bg_color, fg=self.text_color)
        hours_label.pack(side=tk.LEFT)
        
        self.minutes_var = tk.StringVar(value="0")
        minutes_dropdown = ttk.Combobox(duration_frame, textvariable=self.minutes_var, width=5,
                                      values=[str(i*15) for i in range(4)])
        minutes_dropdown.pack(side=tk.LEFT, padx=5)
        
        minutes_label = tk.Label(duration_frame, text="minutes", font=self.normal_font, 
                                bg=self.bg_color, fg=self.text_color)
        minutes_label.pack(side=tk.LEFT)
        
        # Sleep quality
        quality_frame = tk.Frame(form_frame, bg=self.bg_color)
        quality_frame.pack(fill=tk.X, pady=10)
        
        quality_label = tk.Label(quality_frame, text="Sleep Quality:", font=self.normal_font, 
                                bg=self.bg_color, fg=self.text_color, width=15, anchor='w')
        quality_label.pack(side=tk.LEFT, padx=5)
        
        self.quality_var = tk.StringVar(value="Average")
        quality_options = ["Good", "Average", "Poor"]
        
        for i, option in enumerate(quality_options):
            rb = tk.Radiobutton(quality_frame, text=option, variable=self.quality_var, value=option,
                              font=self.normal_font, bg=self.bg_color, fg=self.text_color)
            rb.pack(side=tk.LEFT, padx=10)
        
        # Notes
        notes_frame = tk.Frame(form_frame, bg=self.bg_color)
        notes_frame.pack(fill=tk.X, pady=10)
        
        notes_label = tk.Label(notes_frame, text="Notes:", font=self.normal_font, 
                              bg=self.bg_color, fg=self.text_color, width=15, anchor='w')
        notes_label.pack(side=tk.LEFT, padx=5, anchor='n')
        
        self.notes_text = tk.Text(notes_frame, font=self.normal_font, height=3, width=30)
        self.notes_text.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
        
        # Submit button
        button_frame = tk.Frame(form_frame, bg=self.bg_color)
        button_frame.pack(fill=tk.X, pady=20)
        
        submit_button = tk.Button(button_frame, text="Save Sleep Record", font=self.button_font,
                                 bg=self.primary_color, fg="white", padx=15, pady=5,
                                 command=self.save_sleep_record)
        submit_button.pack(pady=10)
    
    def save_sleep_record(self):
        try:
        # Get date
            day = int(self.day_var.get())
            month = int(self.month_var.get())
            year = int(self.year_var.get())
            date_str = f"{year}-{month:02d}-{day:02d}"

        # Validate date
            datetime(year, month, day)  # Will raise ValueError if invalid

        # Get duration
            hours = float(self.hours_var.get())
            minutes = float(self.minutes_var.get())
            total_hours = hours + (minutes / 60)

        # Get quality
            quality = self.quality_var.get()

        # Get notes
            notes = self.notes_text.get("1.0", tk.END).strip()

        # Connect to database
            conn = sqlite3.connect('data/fitness_tracker.db')
            cursor = conn.cursor()

        # Check if record already exists for this date
            cursor.execute("SELECT id FROM sleep WHERE username = ? AND date = ?", 
                       (self.username, date_str))
            existing = cursor.fetchone()

            if existing:
            # Update existing record
                cursor.execute("""
                UPDATE sleep 
                SET hours = ?, quality = ?, notes = ?
                WHERE username = ? AND date = ?
                """, (total_hours, quality, notes, self.username, date_str))
                message = "Sleep record updated successfully!"
            else:
            # Insert new record
                cursor.execute("""
                INSERT INTO sleep (username, date, hours, quality, notes)
                VALUES (?, ?, ?, ?, ?)
            """, (self.username, date_str, total_hours, quality, notes))
            message = "Sleep record saved successfully!"

            ####################

            messagebox.showinfo("Success", message)

        # Refresh other tabs
            self.load_sleep_history()
            self.update_analytics()
            self.update_recommendations()

        # Ensure the UI updates properly
            self.parent.after(100, self.update_analytics)
            self.parent.after(200, self.update_recommendations)

        except ValueError as e:
            messagebox.showerror("Input Error", f"Please enter valid values: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            
            
        conn.commit()
        conn.close()

    
    def setup_history_tab(self):
        # Header
        header = tk.Label(self.history_tab, text="Sleep History", font=self.title_font, 
                          bg=self.bg_color, fg=self.text_color)
        header.pack(pady=(20, 30))
        
        # Create control frame
        control_frame = tk.Frame(self.history_tab, bg=self.bg_color)
        control_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Add refresh button
        refresh_button = tk.Button(control_frame, text="Refresh", font=self.button_font,
                                  bg=self.primary_color, fg="white", padx=10, pady=2,
                                  command=self.load_sleep_history)
        refresh_button.pack(side=tk.RIGHT, padx=5)
        
        # Create table frame
        table_frame = tk.Frame(self.history_tab, bg=self.bg_color)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Create treeview
        columns = ("date", "hours", "quality", "notes")
        self.history_tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        
        # Define headings
        self.history_tree.heading("date", text="Date")
        self.history_tree.heading("hours", text="Hours")
        self.history_tree.heading("quality", text="Quality")
        self.history_tree.heading("notes", text="Notes")
        
        # Define columns
        self.history_tree.column("date", width=100, anchor="center")
        self.history_tree.column("hours", width=50, anchor="center")
        self.history_tree.column("quality", width=80, anchor="center")
        self.history_tree.column("notes", width=300)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview and scrollbar
        self.history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add edit and delete buttons
        button_frame = tk.Frame(self.history_tab, bg=self.bg_color)
        button_frame.pack(fill=tk.X, padx=20, pady=10)
        
        edit_button = tk.Button(button_frame, text="Edit", font=self.button_font,
                               bg=self.secondary_color, fg="white", padx=15, pady=3,
                               command=self.edit_sleep_record)
        edit_button.pack(side=tk.LEFT, padx=5)
        
        delete_button = tk.Button(button_frame, text="Delete", font=self.button_font,
                                 bg=self.warning_color, fg="white", padx=15, pady=3,
                                 command=self.delete_sleep_record)
        delete_button.pack(side=tk.LEFT, padx=5)
        
        # Load sleep history
        self.load_sleep_history()
    
    def load_sleep_history(self):
        # Clear existing data
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        # Connect to database
        conn = sqlite3.connect('data/fitness_tracker.db')
        cursor = conn.cursor()
        
        # Query sleep records
        cursor.execute("""
            SELECT date, hours, quality, notes, id
            FROM sleep 
            WHERE username = ?
            ORDER BY date DESC
        """, (self.username,))
        
        # Add data to treeview
        for row in cursor.fetchall():
            date_str, hours, quality, notes, record_id = row
            # Format hours as decimal
            hours_display = f"{hours:.1f}"
            # Truncate notes if too long
            notes_display = notes[:40] + "..." if notes and len(notes) > 40 else notes
            
            # Insert into treeview with record_id as tag
            self.history_tree.insert("", "end", values=(date_str, hours_display, quality, notes_display),
                                    tags=(record_id,))
        
        # Close connection
        conn.close()
    
    def edit_sleep_record(self):
        # Get selected item
        selected = self.history_tree.selection()
        if not selected:
            messagebox.showinfo("Selection Required", "Please select a record to edit.")
            return
        
        # Get record ID (stored as tag)
        record_id = self.history_tree.item(selected[0], "tags")[0]
        
        # Connect to database
        conn = sqlite3.connect('data/fitness_tracker.db')
        cursor = conn.cursor()
        
        # Query record details
        cursor.execute("""
            SELECT date, hours, quality, notes
            FROM sleep 
            WHERE id = ?
        """, (record_id,))
        
        record = cursor.fetchone()
        conn.close()
        
        if not record:
            messagebox.showerror("Error", "Record not found.")
            return
        
        date_str, hours, quality, notes = record
        
        # Create edit dialog
        edit_window = tk.Toplevel(self.parent)
        edit_window.title("Edit Sleep Record")
        edit_window.geometry("400x350")
        edit_window.configure(bg=self.bg_color)
        edit_window.grab_set()  # Make dialog modal
        
        # Date display (read-only)
        date_frame = tk.Frame(edit_window, bg=self.bg_color)
        date_frame.pack(fill=tk.X, padx=20, pady=10)
        
        date_label = tk.Label(date_frame, text="Date:", font=self.normal_font, 
                             bg=self.bg_color, fg=self.text_color, width=15, anchor='w')
        date_label.pack(side=tk.LEFT, padx=5)
        
        date_display = tk.Label(date_frame, text=date_str, font=self.normal_font, 
                               bg=self.bg_color, fg=self.text_color)
        date_display.pack(side=tk.LEFT, padx=5)
        
        # Sleep duration
        duration_frame = tk.Frame(edit_window, bg=self.bg_color)
        duration_frame.pack(fill=tk.X, padx=20, pady=10)
        
        duration_label = tk.Label(duration_frame, text="Sleep Duration:", font=self.normal_font, 
                                 bg=self.bg_color, fg=self.text_color, width=15, anchor='w')
        duration_label.pack(side=tk.LEFT, padx=5)
        
        # Split hours into hours and minutes
        hours_whole = int(hours)
        minutes_part = int((hours - hours_whole) * 60)
        
        hours_var = tk.StringVar(value=str(hours_whole))
        hours_dropdown = ttk.Combobox(duration_frame, textvariable=hours_var, width=5,
                                    values=[str(i) for i in range(13)])
        hours_dropdown.pack(side=tk.LEFT, padx=5)
        
        hours_label = tk.Label(duration_frame, text="hours", font=self.normal_font, 
                              bg=self.bg_color, fg=self.text_color)
        hours_label.pack(side=tk.LEFT)
        
        minutes_var = tk.StringVar(value=str(minutes_part))
        minutes_dropdown = ttk.Combobox(duration_frame, textvariable=minutes_var, width=5,
                                      values=[str(i*15) for i in range(4)])
        minutes_dropdown.pack(side=tk.LEFT, padx=5)
        
        minutes_label = tk.Label(duration_frame, text="minutes", font=self.normal_font, 
                                bg=self.bg_color, fg=self.text_color)
        minutes_label.pack(side=tk.LEFT)
        
        # Sleep quality
        quality_frame = tk.Frame(edit_window, bg=self.bg_color)
        quality_frame.pack(fill=tk.X, padx=20, pady=10)
        
        quality_label = tk.Label(quality_frame, text="Sleep Quality:", font=self.normal_font, 
                                bg=self.bg_color, fg=self.text_color, width=15, anchor='w')
        quality_label.pack(side=tk.LEFT, padx=5)
        
        quality_var = tk.StringVar(value=quality)
        quality_options = ["Good", "Average", "Poor"]
        
        for i, option in enumerate(quality_options):
            rb = tk.Radiobutton(quality_frame, text=option, variable=quality_var, value=option,
                              font=self.normal_font, bg=self.bg_color, fg=self.text_color)
            rb.pack(side=tk.LEFT, padx=10)
        
        # Notes
        notes_frame = tk.Frame(edit_window, bg=self.bg_color)
        notes_frame.pack(fill=tk.X, padx=20, pady=10)
        
        notes_label = tk.Label(notes_frame, text="Notes:", font=self.normal_font, 
                              bg=self.bg_color, fg=self.text_color, width=15, anchor='w')
        notes_label.pack(side=tk.LEFT, padx=5, anchor='n')
        
        notes_text = tk.Text(notes_frame, font=self.normal_font, height=3, width=30)
        notes_text.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
        notes_text.insert("1.0", notes if notes else "")
        
        # Save button
        button_frame = tk.Frame(edit_window, bg=self.bg_color)
        button_frame.pack(fill=tk.X, padx=20, pady=20)
        
        def save_edits():
            try:
                # Get updated values
                new_hours = float(hours_var.get())
                new_minutes = float(minutes_var.get())
                new_total_hours = new_hours + (new_minutes / 60)
                new_quality = quality_var.get()
                new_notes = notes_text.get("1.0", tk.END).strip()
                
                # Update database
                conn = sqlite3.connect('data/fitness_tracker.db')
                cursor = conn.cursor()
                
                cursor.execute("""
                    UPDATE sleep
                    SET hours = ?, quality = ?, notes = ?
                    WHERE id = ?
                """, (new_total_hours, new_quality, new_notes, record_id))
                
                # 
                
                messagebox.showinfo("Success", "Sleep record updated successfully!")
                
                # Close edit window
                edit_window.destroy()
                
                # Refresh history
                self.load_sleep_history()
                self.update_analytics()
                self.update_recommendations()
                
                conn.commit()
                conn.close()
                
            except ValueError as e:
                messagebox.showerror("Input Error", f"Please enter valid values: {str(e)}")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred line 459: {str(e)}")
                
            
        
        save_button = tk.Button(button_frame, text="Save Changes", font=self.button_font,
                               bg=self.primary_color, fg="white", padx=15, pady=5,
                               command=save_edits)
        save_button.pack(pady=10)
    
    def delete_sleep_record(self):
        # Get selected item
        selected = self.history_tree.selection()
        if not selected:
            messagebox.showinfo("Selection Required", "Please select a record to delete.")
            return
        
        # Confirm deletion
        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this sleep record?"):
            return
        
        # Get record ID (stored as tag)
        record_id = self.history_tree.item(selected[0], "tags")[0]
        
        # Connect to database
        conn = sqlite3.connect('data/fitness_tracker.db')
        cursor = conn.cursor()
        
        # Delete record
        cursor.execute("DELETE FROM sleep WHERE id = ?", (record_id,))
        
        # 
        
        messagebox.showinfo("Success", "Sleep record deleted successfully!")
        
        # Refresh history
        self.load_sleep_history()
        self.update_analytics()
        self.update_recommendations()
        
        conn.commit()
        conn.close()
        
    
    #####################################################################
    def setup_analytics_tab(self):
    # Header
        header = tk.Label(self.analytics_tab, text="Sleep Analytics", font=self.title_font, 
                        bg=self.bg_color, fg=self.text_color)
        header.pack(pady=(20, 30))
        
        # Create summary frame
        self.summary_frame = tk.Frame(self.analytics_tab, bg=self.bg_color)
        self.summary_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Create graphs frame
        self.graphs_frame = tk.Frame(self.analytics_tab, bg=self.bg_color)
        self.graphs_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Create refresh button
        refresh_button = tk.Button(self.analytics_tab, text="Refresh Analytics", 
                                command=self.update_analytics, bg=self.primary_color, 
                                fg="white", font=self.normal_font)
        refresh_button.pack(pady=10)
        
        # Initial update of analytics
        self.update_analytics()

    def update_analytics(self):
        # Clear existing widgets
        for widget in self.summary_frame.winfo_children():
            widget.destroy()
        
        for widget in self.graphs_frame.winfo_children():
            widget.destroy()
        
        # Connect to database
        conn = sqlite3.connect('data/fitness_tracker.db')
        cursor = conn.cursor()
        
        # Query ALL sleep records for the user (no date restriction)
        cursor.execute("""
            SELECT date, hours, quality
            FROM sleep 
            WHERE username = ?
            ORDER BY date
        """, (self.username,))
        
        records = cursor.fetchall()
        
        # Create summary statistics
        if records:
            # Extract data
            dates = [datetime.strptime(r[0], "%Y-%m-%d") for r in records]
            hours = [r[1] for r in records]
            qualities = [r[2] for r in records]
            
            # Calculate statistics
            total_hours = sum(hours)
            total_days = len(hours)
            avg_hours = total_hours / total_days
            
            # Calculate consistency
            consistency_scores = [max(0, 1 - abs(h - avg_hours) / avg_hours) for h in hours]
            consistency_percentage = int(sum(consistency_scores) / len(consistency_scores) * 100) if consistency_scores else 0
            
            # Calculate weekday vs weekend sleep
            weekday_hours = []
            weekend_hours = []
            
            for date, hour in zip(dates, hours):
                if date.weekday() < 5:  # Monday-Friday
                    weekday_hours.append(hour)
                else:  # Saturday-Sunday
                    weekend_hours.append(hour)
            
            weekday_avg = sum(weekday_hours) / len(weekday_hours) if weekday_hours else 0
            weekend_avg = sum(weekend_hours) / len(weekend_hours) if weekend_hours else 0
            
            # Display summary
            summary_title = tk.Label(self.summary_frame, text="Sleep Summary", font=self.header_font,
                                bg=self.bg_color, fg=self.text_color)
            summary_title.grid(row=0, column=0, columnspan=3, pady=(0, 10), sticky='w')
            
            # Create metric displays
            metrics = [
                ("Total Sleep", f"{total_hours:.1f} hours"),
                ("Total Days", f"{total_days}"),
                ("Average Sleep", f"{avg_hours:.1f} hours"),
                ("Sleep Consistency", f"{consistency_percentage}%"),
                ("Weekday Average", f"{weekday_avg:.1f} hours"),
                ("Weekend Average", f"{weekend_avg:.1f} hours")
            ]
            
            # Display metrics in grid
            for i, (label, value) in enumerate(metrics):
                col = i % 3
                row = i // 3 + 1
                
                metric_frame = tk.Frame(self.summary_frame, bg=self.bg_color, padx=10, pady=5)
                metric_frame.grid(row=row, column=col, padx=10, pady=5, sticky='w')
                
                label_widget = tk.Label(metric_frame, text=label, font=self.normal_font,
                                    bg=self.bg_color, fg=self.text_color)
                label_widget.pack(anchor='w')
                
                value_widget = tk.Label(metric_frame, text=value, font=self.header_font,
                                    bg=self.bg_color, fg=self.primary_color)
                value_widget.pack(anchor='w')
            
            # Create graphs
            # 1. Sleep hours over time
            fig = plt.Figure(figsize=(10, 8), dpi=100)
            fig.subplots_adjust(hspace=0.5)
            
            # First subplot - Sleep duration over time
            ax1 = fig.add_subplot(211)
            ax1.plot([d.date() for d in dates], hours, 'o-', color=self.primary_color)
            ax1.set_title('Sleep Duration Over Time')
            ax1.set_ylabel('Hours')
            ax1.set_ylim(0, max(12, max(hours) + 1))
            ax1.axhline(y=avg_hours, color='r', linestyle='--', alpha=0.7)
            ax1.text(dates[0].date(), avg_hours + 0.2, f'Average ({avg_hours:.1f}h)', color='r')
            ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
            
            # Second subplot - Quality distribution
            ax2 = fig.add_subplot(212)
            quality_counts = {"Good": 0, "Average": 0, "Poor": 0}
            for q in qualities:
                quality_counts[q] = quality_counts.get(q, 0) + 1
                
            colors = {
                "Good": self.secondary_color,
                "Average": "#f39c12",  # Orange
                "Poor": self.warning_color
            }
            
            qualities_list = list(quality_counts.keys())
            counts = list(quality_counts.values())
            bar_colors = [colors[q] for q in qualities_list]
            
            ax2.bar(qualities_list, counts, color=bar_colors)
            ax2.set_title('Sleep Quality Distribution')
            ax2.set_ylabel('Number of Days')
            
            # Add canvas
            canvas = FigureCanvasTkAgg(fig, master=self.graphs_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
        else:
            # No data message
            no_data_label = tk.Label(self.summary_frame, text="No sleep data available. Please add sleep records.", 
                                font=self.header_font, bg=self.bg_color, fg=self.text_color)
            no_data_label.pack(pady=50)
        
        conn.close()

    def setup_recommendations_tab(self):
        # Header
        header = tk.Label(self.recommendations_tab, text="Sleep Recommendations", font=self.title_font, 
                        bg=self.bg_color, fg=self.text_color)
        header.pack(pady=(20, 30))
        
        # Create recommendations container
        self.recommendations_container = tk.Frame(self.recommendations_tab, bg=self.bg_color)
        self.recommendations_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Create refresh button
        refresh_button = tk.Button(self.recommendations_tab, text="Refresh Recommendations", 
                                command=self.update_recommendations, bg=self.primary_color, 
                                fg="white", font=self.normal_font)
        refresh_button.pack(pady=10)
        
        # Initial update of recommendations
        self.update_recommendations()

    def update_recommendations(self):
        # Clear existing recommendations
        for widget in self.recommendations_container.winfo_children():
            widget.destroy()
        
        # Connect to database
        conn = sqlite3.connect('data/fitness_tracker.db')
        cursor = conn.cursor()
        
        # Query ALL sleep records for the user (no date restriction)
        cursor.execute("""
            SELECT date, hours, quality
            FROM sleep 
            WHERE username = ?
            ORDER BY date
        """, (self.username,))
        
        records = cursor.fetchall()
        
        if records:
            # Extract data
            dates = [datetime.strptime(r[0], "%Y-%m-%d") for r in records]
            hours = [r[1] for r in records]
            qualities = [r[2] for r in records]
            
            # Calculate statistics
            avg_hours = sum(hours) / len(hours)
            recommended_hours = 7.5  # Recommended sleep duration range is 7-9 hours
            
            # Generate recommendations
            recommendations = []
            
            # Sleep duration recommendation
            if avg_hours < 7:
                recommendations.append(f"Your average sleep duration ({avg_hours:.1f} hours) is below the recommended 7-9 hours. Try to sleep {(recommended_hours - avg_hours):.1f} hours more each night for better health.")
            elif avg_hours > 9:
                recommendations.append(f"Your average sleep duration ({avg_hours:.1f} hours) is above the recommended 7-9 hours. While this may be normal for some people, consider if you're spending too much time in bed.")
            else:
                recommendations.append(f"Great job! Your average sleep duration ({avg_hours:.1f} hours) is within the recommended 7-9 hours range.")
            
            # Sleep consistency recommendation
            recent_dates = dates[-14:] if len(dates) >= 14 else dates
            recent_hours = hours[-14:] if len(hours) >= 14 else hours
            
            if recent_hours:
                variance = sum((h - avg_hours) ** 2 for h in recent_hours) / len(recent_hours)
                if variance > 1.5:
                    recommendations.append(f"Your sleep duration varies significantly from day to day. Try to maintain a more consistent sleep schedule by going to bed and waking up at the same time each day.")
                else:
                    recommendations.append("You have a consistent sleep schedule. This is excellent for your circadian rhythm and overall health.")
            
            # Sleep quality recommendation
            quality_counts = {"Good": 0, "Average": 0, "Poor": 0}
            for q in qualities:
                quality_counts[q] = quality_counts.get(q, 0) + 1
            
            poor_percentage = quality_counts["Poor"] / len(qualities) * 100 if qualities else 0
            
            if poor_percentage > 25:  # If more than 25% of nights had poor sleep
                recommendations.append(f"You're experiencing frequent nights of poor sleep quality ({poor_percentage:.1f}% of recorded nights). Consider factors that might be affecting your sleep, such as noise, light, temperature, caffeine intake, screen time, or stress.")
                
                # Additional recommendations for improving sleep quality
                sleep_tips = [
                    "Avoid caffeine and alcohol before bedtime.",
                    "Create a relaxing bedtime routine.",
                    "Keep your bedroom cool, dark, and quiet.",
                    "Limit screen time at least 1 hour before bed.",
                    "Consider relaxation techniques like meditation or deep breathing."
                ]
                
                recommendations.append("Some tips to improve your sleep quality:\n• " + "\n• ".join(sleep_tips))
            
            # Weekday vs weekend recommendation
            weekday_hours = [h for d, h in zip(dates, hours) if d.weekday() < 5]
            weekend_hours = [h for d, h in zip(dates, hours) if d.weekday() >= 5]
            
            if weekday_hours and weekend_hours:
                weekday_avg = sum(weekday_hours) / len(weekday_hours)
                weekend_avg = sum(weekend_hours) / len(weekend_hours)
                
                if abs(weekday_avg - weekend_avg) > 1.5:
                    recommendations.append(f"Your sleep schedule differs significantly between weekdays ({weekday_avg:.1f} hours) and weekends ({weekend_avg:.1f} hours). This 'social jet lag' can disrupt your body clock. Try to maintain a more consistent schedule throughout the week.")
            
            # Display recommendations
            rec_header = tk.Label(self.recommendations_container, text="Based on your sleep data:", 
                                font=self.header_font, bg=self.bg_color, fg=self.text_color)
            rec_header.pack(anchor='w', padx=20, pady=(0, 10))
            
            for i, rec in enumerate(recommendations):
                rec_frame = tk.Frame(self.recommendations_container, bg=self.bg_color, pady=10)
                rec_frame.pack(fill=tk.X, padx=20)
                
                bullet = tk.Label(rec_frame, text=f"{i+1}.", font=self.normal_font, 
                                bg=self.bg_color, fg=self.primary_color, width=3, anchor='e')
                bullet.pack(side=tk.LEFT, padx=(0, 5))
                
                rec_label = tk.Label(rec_frame, text=rec, font=self.normal_font, 
                                    bg=self.bg_color, fg=self.text_color, wraplength=500, justify=tk.LEFT)
                rec_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        else:
            # No data message
            no_data_label = tk.Label(self.recommendations_container, 
                                    text="No sleep data available. Start logging your sleep to get personalized recommendations.", 
                                    font=self.normal_font, bg=self.bg_color, fg=self.text_color,
                                    wraplength=500, justify=tk.CENTER)
            no_data_label.pack(pady=50)
        
        conn.close()

    # Additional function to ensure analytics update when new sleep data is added
    def add_sleep_entry(self, date, hours, quality):
        # Your existing code to add a sleep entry to the database
        
        # After adding the entry, update the analytics and recommendations
        self.update_analytics()
        self.update_recommendations()