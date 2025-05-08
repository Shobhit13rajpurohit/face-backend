import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
import subprocess
import sys
import re
import os
import cv2
import pandas as pd
from datetime import datetime

class FaceRecognitionLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Face Recognition Attendance System")
        self.root.geometry("400x550")  # Increased height for new buttons
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
        
        # View Registered Users button
        view_users_btn = tk.Button(options_frame, text="📋 View Registered Users", 
                                command=self.show_registered_users,
                                height=button_height, width=button_width, 
                                bg="#00BCD4", fg="white")
        view_users_btn.pack(pady=5)
        
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
        
        # Delete Student Data button
        delete_btn = tk.Button(options_frame, text="🗑️ Delete Student Data", 
                            command=self.delete_student_data,
                            height=button_height, width=button_width, 
                            bg="#f44336", fg="white")
        delete_btn.pack(pady=5)
        
        # Footer
        footer_frame = tk.Frame(self.root, bg="#ddd", pady=5)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        quit_btn = tk.Button(footer_frame, text="❌ Exit", command=self.root.quit, 
                            bg="#f44336", fg="white")
        quit_btn.pack(side=tk.RIGHT, padx=10)
    
    def validate_numeric(self, value):
        """Validate that input is numeric only"""
        return re.match(r'^\d*$', value) is not None
    
    def validate_email(self, value):
        """Basic email validation"""
        return re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', value) is not None or value == ""
    
    def run_recognize_mode(self):
        """Run face recognition test mode"""
        try:
            subprocess.run([sys.executable, "script.py", "recognize"])
        except Exception as e:
            messagebox.showerror("Error", f"Error running script: {e}")
    
    def run_collect_mode(self):
        """Run face data collection mode with extended fields"""
        # Create popup dialog
        popup = tk.Toplevel(self.root)
        popup.title("Register New Student")
        popup.geometry("350x300")
        popup.config(bg="#f0f0f0")
        popup.grab_set()  # Make the dialog modal
        
        # User ID field
        id_frame = tk.Frame(popup, bg="#f0f0f0")
        id_frame.pack(pady=5, fill=tk.X, padx=20)
        
        id_label = tk.Label(id_frame, text="Student ID (numeric):", bg="#f0f0f0", width=15, anchor="w")
        id_label.pack(side=tk.LEFT, padx=5)
        
        # Register a validation command
        vcmd = (popup.register(self.validate_numeric), '%P')
        id_entry = tk.Entry(id_frame, validate="key", validatecommand=vcmd, width=20)
        id_entry.pack(side=tk.LEFT)
        
        # User Name field
        name_frame = tk.Frame(popup, bg="#f0f0f0")
        name_frame.pack(pady=5, fill=tk.X, padx=20)
        
        name_label = tk.Label(name_frame, text="Student Name:", bg="#f0f0f0", width=15, anchor="w")
        name_label.pack(side=tk.LEFT, padx=5)
        
        name_entry = tk.Entry(name_frame, width=20)
        name_entry.pack(side=tk.LEFT)
        
        # Roll Number field
        roll_frame = tk.Frame(popup, bg="#f0f0f0")
        roll_frame.pack(pady=5, fill=tk.X, padx=20)
        
        roll_label = tk.Label(roll_frame, text="Roll Number:", bg="#f0f0f0", width=15, anchor="w")
        roll_label.pack(side=tk.LEFT, padx=5)
        
        roll_entry = tk.Entry(roll_frame, width=20)
        roll_entry.pack(side=tk.LEFT)
        
        # Email field
        email_frame = tk.Frame(popup, bg="#f0f0f0")
        email_frame.pack(pady=5, fill=tk.X, padx=20)
        
        email_label = tk.Label(email_frame, text="Email:", bg="#f0f0f0", width=15, anchor="w")
        email_label.pack(side=tk.LEFT, padx=5)
        
        email_vcmd = (popup.register(self.validate_email), '%P')
        email_entry = tk.Entry(email_frame, width=20, validate="key", validatecommand=email_vcmd)
        email_entry.pack(side=tk.LEFT)
        
        def start_collection():
            user_id = id_entry.get().strip()
            user_name = name_entry.get().strip()
            roll_number = roll_entry.get().strip()
            email = email_entry.get().strip()
            
            if not user_id:
                messagebox.showerror("Error", "Student ID is required")
                return
            
            if not user_name:
                messagebox.showerror("Error", "Student Name is required")
                return
            
            # Save extended information
            self.save_extended_user_info(user_id, user_name, roll_number, email)
            
            popup.destroy()
            try:
                # Pass user_id and name to the script
                subprocess.run([sys.executable, "script.py", "collect", user_id, user_name])
                messagebox.showinfo("Success", "Face data collection complete. Please train the model.")
            except Exception as e:
                messagebox.showerror("Error", f"Error running script: {e}")
        
        # Start Collection button
        button = tk.Button(popup, text="Start Collection", command=start_collection, 
                        bg="#4CAF50", fg="white", height=2, width=15)
        button.pack(pady=20)
    
    def save_extended_user_info(self, user_id, name, roll="", email=""):
        """Save extended user information to names.txt"""
        user_data = f"{user_id} {name}"
        if roll or email:
            user_data += f" [roll:{roll}] [email:{email}]"
        
        # Check if user_id already exists
        existing_ids = set()
        lines = []
        try:
            if os.path.exists("names.txt"):
                with open("names.txt", "r") as f:
                    lines = f.readlines()
                    for line in lines:
                        parts = line.strip().split()
                        if len(parts) >= 1 and parts[0].isdigit():
                            existing_ids.add(int(parts[0]))
        except Exception as e:
            messagebox.showerror("Error", f"Error reading names file: {e}")
            return False
        
        # Add new user if ID doesn't exist
        try:
            with open("names.txt", "w") as f:
                for line in lines:
                    if line.strip():
                        parts = line.strip().split()
                        if len(parts) >= 1 and parts[0].isdigit() and int(parts[0]) == int(user_id):
                            continue  # Skip existing entry with same ID
                        f.write(line)
                
                # Add the new entry
                f.write(user_data + "\n")
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Error updating names file: {e}")
            return False
    
    def delete_student_data(self):
        """Delete student data"""
        # Create popup dialog
        popup = tk.Toplevel(self.root)
        popup.title("Delete Student Data")
        popup.geometry("300x250")
        popup.config(bg="#f0f0f0")
        popup.grab_set()  # Make the dialog modal
        
        # Get registered students
        students = []
        try:
            if os.path.exists("names.txt"):
                with open("names.txt", "r") as f:
                    for line in f:
                        parts = line.strip().split()
                        if len(parts) >= 2:
                            student_id = parts[0]
                            name = " ".join([p for p in parts[1:] if not p.startswith("[")])
                            students.append((student_id, name))
        except Exception as e:
            messagebox.showerror("Error", f"Error reading names file: {e}")
        
        # Create a listbox with students
        frame = tk.Frame(popup, bg="#f0f0f0")
        frame.pack(pady=10, fill=tk.BOTH, expand=True, padx=20)
        
        label = tk.Label(frame, text="Select student to delete:", bg="#f0f0f0")
        label.pack(anchor="w")
        
        # Create listbox with scrollbar
        list_frame = tk.Frame(frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        student_listbox = tk.Listbox(list_frame, width=40, height=8)
        student_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Connect scrollbar to listbox
        scrollbar.config(command=student_listbox.yview)
        student_listbox.config(yscrollcommand=scrollbar.set)
        
        # Add students to listbox
        for student_id, name in students:
            student_listbox.insert(tk.END, f"{student_id}: {name}")
        
        def delete_selected():
            selection = student_listbox.curselection()
            if not selection:
                messagebox.showinfo("Info", "Please select a student to delete")
                return
            
            selected_index = selection[0]
            student_id, _ = students[selected_index]
            
            # Confirm deletion
            confirm = messagebox.askyesno("Confirm", f"Are you sure you want to delete student ID {student_id}?\n\nThis will remove the student from the database and delete all training images.")
            if not confirm:
                return
                
            # Delete student from names.txt
            try:
                lines = []
                with open("names.txt", "r") as f:
                    lines = f.readlines()
                
                with open("names.txt", "w") as f:
                    for line in lines:
                        parts = line.strip().split()
                        if len(parts) >= 1 and parts[0] != student_id:
                            f.write(line)
                
                # Delete training images
                if os.path.exists("data"):
                    files = [f for f in os.listdir("data") if f.startswith(f"user.{student_id}.")]
                    for file in files:
                        os.remove(os.path.join("data", file))
                
                messagebox.showinfo("Success", f"Student ID {student_id} deleted successfully. Remember to retrain the model.")
                popup.destroy()
                
                # Refresh status
                if os.path.exists("classifier.yml"):
                    os.remove("classifier.yml")
                    messagebox.showinfo("Info", "Classifier has been reset. Please train the model again.")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error deleting student: {e}")
        
        # Delete button
        button = tk.Button(frame, text="Delete Selected", command=delete_selected, 
                      bg="#f44336", fg="white")
        button.pack(pady=10)
    
    def show_registered_users(self):
        """Show list of registered users"""
        # Create popup window
        popup = tk.Toplevel(self.root)
        popup.title("Registered Users")
        popup.geometry("600x400")
        popup.config(bg="#f0f0f0")
        
        # Create a treeview to display user data
        frame = tk.Frame(popup, bg="#f0f0f0")
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create treeview with scrollbar
        tree_frame = tk.Frame(frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ("ID", "Name", "Roll", "Email")
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        
        # Define headings
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Load user data
        try:
            if os.path.exists("names.txt"):
                with open("names.txt", "r") as f:
                    for line in f:
                        # Parse line data
                        basic_parts = line.strip().split()
                        if len(basic_parts) < 2:
                            continue
                            
                        user_id = basic_parts[0]
                        
                        # Extract name (everything before first [tag])
                        name_parts = []
                        for part in basic_parts[1:]:
                            if part.startswith("["):
                                break
                            name_parts.append(part)
                        name = " ".join(name_parts)
                        
                        # Extract roll and email
                        roll = ""
                        email = ""
                        
                        # Look for tags like [roll:123] and [email:user@example.com]
                        for part in basic_parts:
                            if part.startswith("[roll:"):
                                roll = part[6:-1]  # Remove [roll: and ]
                            elif part.startswith("[email:"):
                                email = part[7:-1]  # Remove [email: and ]
                        
                        # Add to treeview
                        tree.insert("", tk.END, values=(user_id, name, roll, email))
        except Exception as e:
            messagebox.showerror("Error", f"Error loading user data: {e}")
        
        # Button frame
        button_frame = tk.Frame(popup, bg="#f0f0f0")
        button_frame.pack(fill=tk.X, pady=10)
        
        def refresh_data():
            # Clear treeview
            for row in tree.get_children():
                tree.delete(row)
                
            # Reload data
            try:
                if os.path.exists("names.txt"):
                    with open("names.txt", "r") as f:
                        for line in f:
                            # Parse line data
                            basic_parts = line.strip().split()
                            if len(basic_parts) < 2:
                                continue
                                
                            user_id = basic_parts[0]
                            
                            # Extract name (everything before first [tag])
                            name_parts = []
                            for part in basic_parts[1:]:
                                if part.startswith("["):
                                    break
                                name_parts.append(part)
                            name = " ".join(name_parts)
                            
                            # Extract roll and email
                            roll = ""
                            email = ""
                            
                            # Look for tags like [roll:123] and [email:user@example.com]
                            for part in basic_parts:
                                if part.startswith("[roll:"):
                                    roll = part[6:-1]  # Remove [roll: and ]
                                elif part.startswith("[email:"):
                                    email = part[7:-1]  # Remove [email: and ]
                            
                            # Add to treeview
                            tree.insert("", tk.END, values=(user_id, name, roll, email))
            except Exception as e:
                messagebox.showerror("Error", f"Error loading user data: {e}")
        
        refresh_btn = tk.Button(button_frame, text="Refresh", command=refresh_data, 
                             bg="#2196F3", fg="white")
        refresh_btn.pack(side=tk.LEFT, padx=10)
        
        def export_users():
            try:
                file_path = tk.filedialog.asksaveasfilename(
                    defaultextension=".csv",
                    filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                    initialfile="registered_users.csv"
                )
                
                if file_path:
                    # Create dataframe from user data
                    users_data = []
                    for row_id in tree.get_children():
                        values = tree.item(row_id)["values"]
                        users_data.append({
                            "ID": values[0],
                            "Name": values[1],
                            "Roll": values[2],
                            "Email": values[3]
                        })
                    
                    df = pd.DataFrame(users_data)
                    df.to_csv(file_path, index=False)
                    messagebox.showinfo("Success", f"Users exported to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Error exporting users: {e}")
        
        export_btn = tk.Button(button_frame, text="Export to CSV", command=export_users, 
                             bg="#4CAF50", fg="white")
        export_btn.pack(side=tk.RIGHT, padx=10)
    
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