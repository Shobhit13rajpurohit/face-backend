import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
import subprocess
import sys
import re
import os
from datetime import datetime

class FaceRecognitionLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Face Recognition Attendance System")
        self.root.geometry("400x550")
        self.root.config(bg="#f0f0f0")
        
        # Import OpenCV here to handle potential import error properly
        try:
            import cv2
            self.cv2 = cv2
            # Check if required files exist
            self.check_required_files()
        except ImportError:
            messagebox.showerror("Error", "OpenCV is required. Please install it with: pip install opencv-python")
            self.cv2 = None
        
        # Setup UI
        self.setup_ui()
    
    def check_required_files(self):
        """Check if required model and cascade files exist"""
        if not self.cv2:
            return
            
        required_files = [
            (self.cv2.data.haarcascades + "haarcascade_frontalface_default.xml", "Haar Cascade face detector")
        ]
        
        # Check for required Python scripts
        script_files = [
            ("classifier.py", "Face recognition classifier script", False),
            ("attendance_system.py", "Attendance system script", False),
            ("attendance_viewer.py", "Attendance viewer script", False),
            ("student_manager.py", "Student manager script", False)
        ]
        
        missing_files = []
        for file_path, description in required_files:
            if not os.path.exists(file_path):
                missing_files.append(f"{description} ({file_path})")
        
        missing_scripts = []
        for script, description, required in script_files:
            if not os.path.exists(script):
                if required:
                    missing_scripts.append(f"{description} ({script})")
                else:
                    print(f"Warning: {description} ({script}) not found")
        
        if missing_files:
            messagebox.showerror("Missing Required Files", 
                                f"The following required files are missing:\n\n" + 
                                "\n".join(missing_files))
        
        if missing_scripts:
            messagebox.showerror("Missing Required Scripts", 
                                f"The following required scripts are missing:\n\n" + 
                                "\n".join(missing_scripts))
    
    def setup_ui(self):
        # Header
        header_frame = tk.Frame(self.root, bg="#4a86e8", pady=10)
        header_frame.pack(fill=tk.X)
        
        title = tk.Label(header_frame, text="Face Recognition\nAttendance System", 
                        font=("Helvetica", 16, "bold"), bg="#4a86e8", fg="white")
        title.pack()
        
        # Status frame
        status_frame = tk.LabelFrame(self.root, text="System Status", bg="#f0f0f0", pady=10, padx=10)
        status_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Check if classifier exists
        classifier_status = "✅ Found" if os.path.exists("classifier.yml") else "❌ Not Found"
        classifier_color = "green" if os.path.exists("classifier.yml") else "red"
        
        tk.Label(status_frame, text=f"Classifier: {classifier_status}", 
                bg="#f0f0f0", fg=classifier_color).pack(anchor="w")
        
        # Check for registered students
        student_count = 0
        if os.path.exists("names.txt"):
            try:
                with open("names.txt", "r") as f:
                    # Count non-empty lines
                    student_count = sum(1 for line in f if line.strip())
            except Exception as e:
                print(f"Error reading names.txt: {e}")
        
        tk.Label(status_frame, text=f"Registered Students: {student_count}", 
                bg="#f0f0f0").pack(anchor="w")
        
        # Check for attendance records
        attendance_count = 0
        if os.path.exists("attendance"):
            try:
                attendance_count = len([f for f in os.listdir("attendance") if f.endswith(".csv")])
            except Exception as e:
                print(f"Error counting attendance files: {e}")
        
        tk.Label(status_frame, text=f"Attendance Records: {attendance_count}", 
                bg="#f0f0f0").pack(anchor="w")
        
        # Today's date
        today = datetime.now().strftime("%Y-%m-%d")
        tk.Label(status_frame, text=f"Current Date: {today}", 
                bg="#f0f0f0").pack(anchor="w")
        
        # Main options frame
        options_frame = tk.LabelFrame(self.root, text="System Functions", bg="#f0f0f0", pady=10, padx=10)
        options_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
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
        
        # Student Management button
        student_mgmt_btn = tk.Button(options_frame, text="👥 Manage Students", 
                                    command=self.run_student_manager,
                                    height=button_height, width=button_width, 
                                    bg="#FF9800", fg="white")
        student_mgmt_btn.pack(pady=5)
        
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
        
        refresh_btn = tk.Button(footer_frame, text="🔄 Refresh", command=self.refresh_status,
                              bg="#2196F3", fg="white")
        refresh_btn.pack(side=tk.LEFT, padx=10)
        
        quit_btn = tk.Button(footer_frame, text="❌ Exit", command=self.root.quit, 
                            bg="#f44336", fg="white")
        quit_btn.pack(side=tk.RIGHT, padx=10)
    
    def refresh_status(self):
        """Refresh the status display and check for required files"""
        # Re-check required files
        if self.cv2:
            self.check_required_files()
            
        # Recreate the UI to refresh status
        for widget in self.root.winfo_children():
            widget.destroy()
        self.setup_ui()
        messagebox.showinfo("Refresh", "Status refreshed successfully")
    
    def validate_numeric(self, value):
        """Validate that input is numeric only"""
        return re.match(r'^\d*$', value) is not None
    
    def run_recognize_mode(self):
        """Run face recognition test mode"""
        if not os.path.exists("script.py"):
            messagebox.showerror("Error", "Recognition script (script.py) not found.")
            return
            
        try:
            subprocess.run([sys.executable, "script.py", "recognize"])
        except Exception as e:
            messagebox.showerror("Error", f"Error running face recognition: {e}")
    
    def run_student_manager(self):
        """Run student management interface"""
        if not os.path.exists("student_manager.py"):
            messagebox.showerror("Error", "Student manager script (student_manager.py) not found.")
            return
            
        try:
            subprocess.run([sys.executable, "student_manager.py"])
        except Exception as e:
            messagebox.showerror("Error", f"Error running student manager: {e}")
    
    def run_train_model(self):
        """Run model training"""
        if not os.path.exists("classifier.py"):
            messagebox.showerror("Error", "Classifier script (classifier.py) not found.")
            return
            
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
            if result.returncode == 0:
                messagebox.showinfo("Success", "Face recognition model trained successfully!")
                self.refresh_status()  # Refresh the status after training
            else:
                messagebox.showwarning("Warning", 
                                     f"Training might not have completed successfully:\n{result.stderr}")
        except Exception as e:
            messagebox.showerror("Error", f"Error training model: {e}")
    
    def run_attendance_system(self):
        """Run the attendance system"""
        if not os.path.exists("classifier.yml"):
            messagebox.showerror("Error", "Classifier not found. Please train the model first.")
            return
        
        if not os.path.exists("attendance_system.py"):
            messagebox.showerror("Error", "Attendance system script (attendance_system.py) not found.")
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
        if not os.path.exists("attendance_viewer.py"):
            messagebox.showerror("Error", "Attendance viewer script (attendance_viewer.py) not found.")
            return
            
        # Check if we have any attendance records
        if not os.path.exists("attendance"):
            os.makedirs("attendance")  # Create the directory if it doesn't exist
            messagebox.showinfo("Info", "No attendance records found yet.")
            return
            
        if not os.listdir("attendance"):
            messagebox.showinfo("Info", "No attendance records found yet.")
            return
            
        try:
            subprocess.run([sys.executable, "attendance_viewer.py"])
        except Exception as e:
            messagebox.showerror("Error", f"Error running attendance viewer: {e}")


if __name__ == "__main__":
    # Setup exception handling for the entire application
    try:
        # Check for OpenCV before creating the application
        import cv2
        
        # Check for other required packages
        required_packages = ["pandas", "matplotlib", "pillow"]
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            print(f"Warning: The following packages are missing: {', '.join(missing_packages)}")
            print("Please install them using:")
            print(f"pip install {' '.join(missing_packages)}")
        
        # Start the application
        root = tk.Tk()
        app = FaceRecognitionLauncher(root)
        root.mainloop()
        
    except ImportError:
        print("Error: OpenCV is required. Please install it with: pip install opencv-python")
        print("Also ensure you have pandas, matplotlib, and pillow installed:")
        print("pip install pandas matplotlib pillow")
        
        # Try to show a message box if Tkinter is available
        try:
            root = tk.Tk()
            root.withdraw()  # Hide the main window
            messagebox.showerror("Missing Dependencies", 
                              "OpenCV is required. Please install it with:\n\npip install opencv-python\n\n" +
                              "Also ensure you have pandas, matplotlib, and pillow installed:\n\n" +
                              "pip install pandas matplotlib pillow")
            root.destroy()
        except:
            pass  # If Tkinter also fails, just use the console output