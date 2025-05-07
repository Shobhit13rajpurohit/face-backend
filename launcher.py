import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
import subprocess
import sys
import re
import os
import cv2
from datetime import datetime

class FaceRecognitionLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Face Recognition Attendance System")
        self.root.geometry("400x500")
        self.root.config(bg="#f0f0f0")
        
        # Check if required files exist
        self.check_required_files()
        
        # Setup UI
        self.setup_ui()
    
    def check_required_files(self):
        """Check if required model and cascade files exist"""
        required_files = [
            (cv2.data.haarcascades + "haarcascade_frontalface_default.xml", "Haar Cascade face detector")
        ]
        
        missing_files = []
        for file_path, description in required_files:
            if not os.path.exists(file_path):
                missing_files.append(f"{description} ({file_path})")
        
        if missing_files:
            messagebox.showerror("Missing Files", 
                                f"The following required files are missing:\n\n" + 
                                "\n".join(missing_files))
    
    def setup_ui(self):
        # Header
        header_frame = tk.Frame(self.root, bg="#4a86e8", pady=10)
        header_frame.pack(fill=tk.X)
        
        title = tk.Label(header_frame, text="Face Recognition\nAttendance System", 
                        font=("Helvetica", 16, "bold"), bg="#4a86e8", fg="white")
        title.pack()
        
        # Status frame
        status_frame = tk.Frame(self.root, bg="#f0f0f0", pady=10)
        status_frame.pack(fill=tk.X, padx=20)
        
        # Check if classifier exists
        classifier_status = "✅ Found" if os.path.exists("classifier.yml") else "❌ Not Found"
        classifier_color = "green" if os.path.exists("classifier.yml") else "red"
        
        tk.Label(status_frame, text=f"Classifier: {classifier_status}", 
                bg="#f0f0f0", fg=classifier_color).pack(anchor="w")
        
        # Check for registered students
        student_count = 0
        if os.path.exists("names.txt"):
            with open("names.txt", "r") as f:
                student_count = len(f.readlines())
        
        tk.Label(status_frame, text=f"Registered Students: {student_count}", 
                bg="#f0f0f0").pack(anchor="w")
        
        # Today's date
        today = datetime.now().strftime("%Y-%m-%d")
        tk.Label(status_frame, text=f"Current Date: {today}", 
                bg="#f0f0f0").pack(anchor="w")
        
        # Main options frame
        options_frame = tk.Frame(self.root, bg="#f0f0f0", pady=10)
        options_frame.pack(fill=tk.BOTH, expand=True, padx=20)
        
        tk.Label(options_frame, text="System Functions", 
                font=("Helvetica", 12, "bold"), bg="#f0f0f0").pack(pady=(10, 20))
        
        # Buttons
        button_width = 25
        button_height = 2
        
        # Take Attendance button
        attendance_btn = tk.Button(options_frame, text="📝 Take Attendance", 
                                command=self.run_attendance_system,
                                height=button_height, width=button_width, 
                                bg="#4CAF50", fg="white")
        attendance_btn.pack(pady=5)
        
        # View Reports button
        reports_btn = tk.Button(options_frame, text="📊 View Attendance Reports", 
                                command=self.run_attendance_viewer,
                                height=button_height, width=button_width, 
                                bg="#2196F3", fg="white")
        reports_btn.pack(pady=5)
        
        # Register New Student button
        register_btn = tk.Button(options_frame, text="👤 Register New Student", 
                                command=self.run_collect_mode,
                                height=button_height, width=button_width, 
                                bg="#FF9800", fg="white")
        register_btn.pack(pady=5)
        
        # Train Model button
        train_btn = tk.Button(options_frame, text="🧠 Train Recognition Model", 
                            command=self.run_train_model,
                            height=button_height, width=button_width, 
                            bg="#9C27B0", fg="white")
        train_btn.pack(pady=5)
        
        # Test Recognition button
        test_btn = tk.Button(options_frame, text="🔍 Test Face Recognition", 
                            command=self.run_recognize_mode,
                            height=button_height, width=button_width, 
                            bg="#607D8B", fg="white")
        test_btn.pack(pady=5)
        
        # Footer
        footer_frame = tk.Frame(self.root, bg="#ddd", pady=5)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        quit_btn = tk.Button(footer_frame, text="❌ Exit", command=self.root.quit, 
                            bg="#f44336", fg="white")
        quit_btn.pack(side=tk.RIGHT, padx=10)
    
    def validate_numeric(self, value):
        """Validate that input is numeric only"""
        return re.match(r'^\d*$', value) is not None
    
    def run_recognize_mode(self):
        """Run face recognition test mode"""
        try:
            subprocess.run([sys.executable, "script.py", "recognize"])
        except Exception as e:
            messagebox.showerror("Error", f"Error running script: {e}")
    
    def run_collect_mode(self):
        """Run face data collection mode"""
        # Create popup dialog
        popup = tk.Toplevel(self.root)
        popup.title("Register New Student")
        popup.geometry("300x200")
        popup.config(bg="#f0f0f0")
        popup.grab_set()  # Make the dialog modal
        
        # User ID field
        id_frame = tk.Frame(popup, bg="#f0f0f0")
        id_frame.pack(pady=10)
        
        id_label = tk.Label(id_frame, text="Student ID (numeric):", bg="#f0f0f0")
        id_label.pack(side=tk.LEFT, padx=5)
        
        # Register a validation command
        vcmd = (popup.register(self.validate_numeric), '%P')
        id_entry = tk.Entry(id_frame, validate="key", validatecommand=vcmd, width=10)
        id_entry.pack(side=tk.LEFT)
        
        # User Name field
        name_frame = tk.Frame(popup, bg="#f0f0f0")
        name_frame.pack(pady=10)
        
        name_label = tk.Label(name_frame, text="Student Name:", bg="#f0f0f0")
        name_label.pack(side=tk.LEFT, padx=5)
        
        name_entry = tk.Entry(name_frame, width=20)
        name_entry.pack(side=tk.LEFT)
        
        def start_collection():
            user_id = id_entry.get().strip()
            user_name = name_entry.get().strip()
            
            if not user_id:
                messagebox.showerror("Error", "Student ID is required")
                return
            
            if not user_name:
                messagebox.showerror("Error", "Student Name is required")
                return
            
            popup.destroy()
            try:
                # Fix: Pass user_id and name to the script
                subprocess.run([sys.executable, "script.py", "collect", user_id, user_name])
                messagebox.showinfo("Success", "Face data collection complete. Please train the model.")
            except Exception as e:
                messagebox.showerror("Error", f"Error running script: {e}")
        
        # Start Collection button
        button = tk.Button(popup, text="Start Collection", command=start_collection, 
                        bg="#4CAF50", fg="white", height=2, width=15)
        button.pack(pady=20)
    
    def run_train_model(self):
        """Run model training"""
        try:
            # Check if there are any images in the data directory
            if not os.path.exists("data"):
                messagebox.showerror("Error", "No training data found. Please register students first.")
                return
                
            if not os.listdir("data"):
                messagebox.showerror("Error", "No training data found. Please register students first.")
                return
                
            result = subprocess.run([sys.executable, "classifier.py"], 
                                  capture_output=True, text=True)
            if "Training complete" in result.stdout:
                messagebox.showinfo("Success", "Face recognition model trained successfully!")
            else:
                messagebox.showwarning("Warning", f"Training might not have completed successfully:\n{result.stdout}")
        except Exception as e:
            messagebox.showerror("Error", f"Error training model: {e}")
    
    def run_attendance_system(self):
        """Run the attendance system"""
        if not os.path.exists("classifier.yml"):
            messagebox.showerror("Error", "Classifier not found. Please train the model first.")
            return
        
        # Check if we have registered students
        if not os.path.exists("names.txt") or os.path.getsize("names.txt") == 0:
            messagebox.showerror("Error", "No students registered. Please register students first.")
            return
            
        try:
            subprocess.run([sys.executable, "attendance_system.py"])
        except Exception as e:
            messagebox.showerror("Error", f"Error running attendance system: {e}")
    
    def run_attendance_viewer(self):
        """Run the attendance viewer"""
        # Check if we have any attendance records
        if not os.path.exists("attendance") or not os.listdir("attendance"):
            messagebox.showinfo("Info", "No attendance records found yet.")
            return
            
        try:
            subprocess.run([sys.executable, "attendance_viewer.py"])
        except Exception as e:
            messagebox.showerror("Error", f"Error running attendance viewer: {e}")


if __name__ == "__main__":
    try:
        import cv2
        root = tk.Tk()
        app = FaceRecognitionLauncher(root)
        root.mainloop()
    except ImportError:
        print("Error: OpenCV is required. Please install it with: pip install opencv-python")
        print("Also ensure you have pandas, matplotlib, and pillow installed:")
        print("pip install pandas matplotlib pillow")