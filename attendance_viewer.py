import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import os
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class AttendanceViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Attendance Records Viewer")
        self.root.geometry("800x600")
        self.root.config(bg="#f0f0f0")
        
        self.attendance_dir = "attendance"
        self.selected_file = None
        self.attendance_data = None
        
        # Ensure attendance directory exists
        if not os.path.exists(self.attendance_dir):
            os.makedirs(self.attendance_dir)
        
        self.setup_ui()
    
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Date selection frame
        date_frame = ttk.LabelFrame(main_frame, text="Select Date")
        date_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Get available dates from attendance files
        available_dates = self.get_available_dates()
        
        # Date combobox
        self.date_combo = ttk.Combobox(date_frame, values=available_dates, width=20, state="readonly")
        if available_dates:
            self.date_combo.current(0)
        self.date_combo.pack(side=tk.LEFT, padx=10, pady=10)
        self.date_combo.bind("<<ComboboxSelected>>", self.load_attendance)
        
        # Refresh button
        refresh_btn = ttk.Button(date_frame, text="Refresh", command=self.refresh_dates)
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        # Export button
        export_btn = ttk.Button(date_frame, text="Export Report", command=self.export_report)
        export_btn.pack(side=tk.RIGHT, padx=10)
        
        # Stats frame
        stats_frame = ttk.LabelFrame(main_frame, text="Attendance Statistics")
        stats_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Stats labels
        self.total_label = ttk.Label(stats_frame, text="Total Students: 0")
        self.total_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        self.present_label = ttk.Label(stats_frame, text="Present: 0")
        self.present_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Table frame
        table_frame = ttk.LabelFrame(main_frame, text="Attendance Records")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create treeview for data
        self.tree = ttk.Treeview(table_frame, columns=("ID", "Name", "Date", "Time"), show="headings")
        self.tree.heading("ID", text="Student ID")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Date", text="Date")
        self.tree.heading("Time", text="Time")
        
        self.tree.column("ID", width=80)
        self.tree.column("Name", width=200)
        self.tree.column("Date", width=100)
        self.tree.column("Time", width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        # Pack tree and scrollbar
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Charts frame
        chart_frame = ttk.LabelFrame(main_frame, text="Attendance Chart")
        chart_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Canvas for chart
        self.chart_canvas = None
        self.chart_container = ttk.Frame(chart_frame)
        self.chart_container.pack(fill=tk.BOTH, expand=True)
        
        # Make chart resize with window
        self.root.bind("<Configure>", self.on_window_resize)
        
        # Load initial data if available
        if available_dates:
            self.load_attendance()
    
    def on_window_resize(self, event=None):
        """Update chart when window is resized"""
        # Only update if we have data and if the event is from the root window
        if self.attendance_data is not None and event and event.widget == self.root:
            # Add a small delay to prevent excessive redrawing during resize
            self.root.after_cancel(self.resize_job) if hasattr(self, 'resize_job') else None
            self.resize_job = self.root.after(200, self.update_chart)
    
    def get_available_dates(self):
        """Get list of available attendance dates from files"""
        if not os.path.exists(self.attendance_dir):
            return []
        
        try:
            files = [f for f in os.listdir(self.attendance_dir) if f.endswith('.csv')]
            # Extract dates from filenames
            dates = [f.split('.')[0] for f in files]
            # Sort dates in descending order (newest first)
            dates.sort(reverse=True)
            return dates
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get attendance files: {e}")
            return []
    
    def refresh_dates(self):
        """Refresh the list of available dates"""
        available_dates = self.get_available_dates()
        self.date_combo['values'] = available_dates
        
        if available_dates:
            self.date_combo.current(0)
            self.load_attendance()
        else:
            # Clear the table if no dates available
            for row in self.tree.get_children():
                self.tree.delete(row)
            self.update_stats(0)
            self.clear_chart()
            messagebox.showinfo("Info", "No attendance records found.")
    
    def load_attendance(self, event=None):
        """Load attendance data for selected date"""
        selected_date = self.date_combo.get()
        if not selected_date:
            return
        
        self.selected_file = os.path.join(self.attendance_dir, f"{selected_date}.csv")
        
        try:
            # Check if file exists
            if not os.path.exists(self.selected_file):
                messagebox.showerror("Error", f"File not found: {self.selected_file}")
                return
                
            # Read attendance data
            self.attendance_data = pd.read_csv(self.selected_file)
            
            # Validate columns
            required_columns = ['ID', 'Name', 'Date', 'Time']
            for col in required_columns:
                if col not in self.attendance_data.columns:
                    messagebox.showerror("Error", f"Missing required column: {col}")
                    self.attendance_data = None
                    return
            
            # Clear existing data
            for row in self.tree.get_children():
                self.tree.delete(row)
            
            # Insert new data
            for idx, row in self.attendance_data.iterrows():
                self.tree.insert("", tk.END, values=(row['ID'], row['Name'], row['Date'], row['Time']))
            
            # Update statistics
            self.update_stats(len(self.attendance_data))
            
            # Update chart
            self.update_chart()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load attendance data: {e}")
            self.attendance_data = None
    
    def update_stats(self, present_count):
        """Update statistics labels"""
        # Load names file to get total student count
        total_students = 0
        try:
            if os.path.exists("names.txt"):
                with open("names.txt", "r") as f:
                    # Count non-empty lines
                    lines = [line.strip() for line in f.readlines() if line.strip()]
                    total_students = len(lines)
            
            # Update labels
            self.total_label.config(text=f"Total Students: {total_students}")
            self.present_label.config(text=f"Present: {present_count}")
            
            # Calculate and show percentage if there are students
            if total_students > 0:
                percentage = (present_count / total_students) * 100
                attendance_rate = ttk.Label(self.total_label.master, 
                                          text=f"Attendance Rate: {percentage:.1f}%")
                # Check if we already have a percentage label
                for widget in self.total_label.master.winfo_children():
                    if isinstance(widget, ttk.Label) and "Attendance Rate" in widget.cget("text"):
                        widget.config(text=f"Attendance Rate: {percentage:.1f}%")
                        break
                else:
                    # If we don't have a percentage label yet, create one
                    attendance_rate = ttk.Label(self.total_label.master, 
                                              text=f"Attendance Rate: {percentage:.1f}%")
                    attendance_rate.pack(side=tk.LEFT, padx=10, pady=5)
            
        except Exception as e:
            print(f"Error updating stats: {e}")
            self.total_label.config(text="Total Students: Unknown")
            self.present_label.config(text=f"Present: {present_count}")
    
    def update_chart(self):
        """Update attendance chart"""
        if self.attendance_data is None or len(self.attendance_data) == 0:
            self.clear_chart()
            return
        
        try:
            # Get arrival time distribution
            # First make a copy to avoid modifying the original data
            chart_data = self.attendance_data.copy()
            
            # Handle time data safely
            try:
                # Try to convert the Time column to datetime format
                chart_data['TimeObj'] = pd.to_datetime(chart_data['Time'], format='%H:%M:%S', errors='coerce')
                
                # Check if conversion was successful
                if chart_data['TimeObj'].isna().all():
                    # If all conversions failed, try another format
                    chart_data['TimeObj'] = pd.to_datetime(chart_data['Time'], errors='coerce')
                
                # Format to hour:minute for display
                chart_data['TimeFormatted'] = chart_data['TimeObj'].dt.strftime('%H:%M')
                
                # Use the formatted time for grouping
                time_counts = chart_data['TimeFormatted'].value_counts().sort_index()
            except Exception as e:
                print(f"Error processing time data: {e}")
                # Fallback: use the original time data
                time_counts = chart_data['Time'].value_counts().sort_index()
            
            # Create figure
            fig, ax = plt.subplots(figsize=(5, 3))
            ax.bar(time_counts.index, time_counts.values, color='skyblue')
            ax.set_title('Student Arrival Times')
            ax.set_xlabel('Time')
            ax.set_ylabel('Number of Students')
            ax.tick_params(axis='x', rotation=45)
            plt.tight_layout()
            
            # Add to canvas
            self.clear_chart()
            self.chart_canvas = FigureCanvasTkAgg(fig, self.chart_container)
            self.chart_canvas.draw()
            self.chart_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update chart: {e}")
            self.clear_chart()
    
    def clear_chart(self):
        """Clear chart canvas"""
        if self.chart_canvas is not None:
            self.chart_canvas.get_tk_widget().destroy()
            self.chart_canvas = None
    
    def export_report(self):
        """Export attendance report as CSV"""
        if self.attendance_data is None:
            messagebox.showinfo("Info", "No attendance data to export")
            return
        
        try:
            # Ask for save location
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx"), ("All files", "*.*")],
                initialfile=f"attendance_report_{self.date_combo.get()}.csv"
            )
            
            if not file_path:
                return  # User cancelled
                
            # Export based on file extension
            if file_path.endswith('.xlsx'):
                self.attendance_data.to_excel(file_path, index=False)
            else:
                self.attendance_data.to_csv(file_path, index=False)
                
            messagebox.showinfo("Success", f"Report exported to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export report: {e}")


if __name__ == "__main__":
    try:
        # Check for required libraries
        import matplotlib
        import pandas
        
        # Set up exception handling
        def show_error(exc_type, exc_value, exc_traceback):
            error_msg = f"An unexpected error occurred:\n{exc_type.__name__}: {exc_value}"
            messagebox.showerror("Application Error", error_msg)
            # Also print to console for debugging
            import traceback
            traceback.print_exception(exc_type, exc_value, exc_traceback)
        
        # Set up global exception handler
        import sys
        sys.excepthook = show_error
        
        # Start application
        root = tk.Tk()
        app = AttendanceViewer(root)
        root.mainloop()
    except ImportError as e:
        print(f"Error: Missing required libraries: {e}")
        print("Please install required packages:")
        print("pip install pandas matplotlib")