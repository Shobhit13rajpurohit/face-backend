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
        self.date_combo = ttk.Combobox(date_frame, values=available_dates, width=20)
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
        
        # Load initial data if available
        if available_dates:
            self.load_attendance()
    
    def get_available_dates(self):
        """Get list of available attendance dates from files"""
        if not os.path.exists(self.attendance_dir):
            return []
        
        files = [f for f in os.listdir(self.attendance_dir) if f.endswith('.csv')]
        # Extract dates from filenames
        dates = [f.split('.')[0] for f in files]
        # Sort dates in descending order (newest first)
        dates.sort(reverse=True)
        return dates
    
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
    
    def load_attendance(self, event=None):
        """Load attendance data for selected date"""
        selected_date = self.date_combo.get()
        if not selected_date:
            return
        
        self.selected_file = f"{self.attendance_dir}/{selected_date}.csv"
        
        try:
            # Read attendance data
            self.attendance_data = pd.read_csv(self.selected_file)
            
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
    
    def update_stats(self, present_count):
        """Update statistics labels"""
        # Load names file to get total student count
        total_students = 0
        try:
            if os.path.exists("names.txt"):
                with open("names.txt", "r") as f:
                    lines = f.readlines()
                    total_students = len(lines)
        except Exception as e:
            print(f"Error loading names: {e}")
        
        self.total_label.config(text=f"Total Students: {total_students}")
        self.present_label.config(text=f"Present: {present_count}")
    
    def update_chart(self):
        """Update attendance chart"""
        if self.attendance_data is None or len(self.attendance_data) == 0:
            self.clear_chart()
            return
        
        # Get arrival time distribution
        self.attendance_data['Time'] = pd.to_datetime(self.attendance_data['Time']).dt.strftime('%H:%M')
        time_counts = self.attendance_data['Time'].value_counts().sort_index()
        
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
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialfile=f"attendance_report_{self.date_combo.get()}.csv"
            )
            
            if file_path:
                self.attendance_data.to_csv(file_path, index=False)
                messagebox.showinfo("Success", f"Report exported to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export report: {e}")


if __name__ == "__main__":
    # Check for matplotlib
    try:
        import matplotlib
        root = tk.Tk()
        app = AttendanceViewer(root)
        root.mainloop()
    except ImportError:
        print("Please install matplotlib: pip install matplotlib")
        print("Also ensure pandas is installed: pip install pandas")