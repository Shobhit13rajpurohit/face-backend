import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import os
import re
import glob
import pandas as pd
import subprocess
import sys

class StudentManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Management")
        self.root.geometry("700x500")
        self.root.config(bg="#f0f0f0")
        
        # Setup variables
        self.names_file = "names.txt"
        self.data_dir = "data"
        
        # Create necessary directories
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            
        # Setup UI
        self.setup_ui()
        
        # Load student data
        self.load_students()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(header_frame, text="Student Management", 
                 font=("Helvetica", 16, "bold")).pack(side=tk.LEFT)
        
        # Buttons frame
        btn_frame = ttk.Frame(header_frame)
        btn_frame.pack(side=tk.RIGHT)
        
        ttk.Button(btn_frame, text="Add Student", command=self.add_student).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Edit Selected", command=self.edit_student).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Delete Selected", command=self.delete_student).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Refresh", command=self.load_students).pack(side=tk.LEFT, padx=5)
        
        # Student table
        table_frame = ttk.Frame(main_frame)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Create treeview for data
        self.tree = ttk.Treeview(table_frame, columns=("ID", "Name", "Roll Number", "Email", "Status"), show="headings")
        self.tree.heading("ID", text="Student ID")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Roll Number", text="Roll Number")
        self.tree.heading("Email", text="Email")
        self.tree.heading("Status", text="Status")
        
        self.tree.column("ID", width=60)
        self.tree.column("Name", width=180)
        self.tree.column("Roll Number", width=120)
        self.tree.column("Email", width=150)
        self.tree.column("Status", width=120)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        # Pack tree and scrollbar
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM, pady=5)
    
    def load_students(self):
        """Load students from names.txt file"""
        # Clear existing data
        for row in self.tree.get_children():
            self.tree.delete(row)
            
        if not os.path.exists(self.names_file):
            self.status_var.set("No students registered.")
            return
            
        try:
            students = []
            with open(self.names_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line:  # Skip empty lines
                        continue
                        
                    parts = line.split()
                    if len(parts) >= 2:
                        student_id = parts[0]
                        
                        # Extract roll number if exists
                        roll_match = re.search(r'\[roll:(.*?)\]', line)
                        roll_number = roll_match.group(1) if roll_match else ""
                        
                        # Extract email if exists
                        email_match = re.search(r'\[email:(.*?)\]', line)
                        email = email_match.group(1) if email_match else ""
                        
                        # Extract name (everything before tags)
                        name_part = line
                        if '[roll:' in name_part:
                            name_part = name_part.split('[roll:')[0]
                        if '[email:' in name_part:
                            name_part = name_part.split('[email:')[0]
                            
                        name = ' '.join(name_part.split()[1:]).strip()  # Skip ID
                            
                        # Check if face images exist
                        face_images = glob.glob(f"{self.data_dir}/user.{student_id}.*.jpg")
                        status = f"{len(face_images)} images" if face_images else "No face data"
                        
                        students.append((student_id, name, roll_number, email, status))
            
            # Insert data into treeview
            for student in students:
                self.tree.insert("", tk.END, values=student)
                
            self.status_var.set(f"Loaded {len(students)} students")
        except Exception as e:
            messagebox.showerror("Error", f"Error loading students: {e}")
            self.status_var.set("Error loading students")
    
    def add_student(self):
        """Open dialog to add a new student"""
        add_window = tk.Toplevel(self.root)
        add_window.title("Add New Student")
        add_window.geometry("400x300")
        add_window.config(bg="#f0f0f0")
        add_window.grab_set()  # Make window modal
        
        # Form fields
        form_frame = ttk.Frame(add_window)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # ID field
        id_frame = ttk.Frame(form_frame)
        id_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(id_frame, text="Student ID:").grid(row=0, column=0, sticky=tk.W, padx=5)
        id_var = tk.StringVar()
        id_entry = ttk.Entry(id_frame, textvariable=id_var, width=10)
        id_entry.grid(row=0, column=1, sticky=tk.W)
        
        # Validate ID is numeric
        vcmd = (add_window.register(lambda P: P.isdigit() or P == ""), '%P')
        id_entry.config(validate="key", validatecommand=vcmd)
        
        # Name field
        name_frame = ttk.Frame(form_frame)
        name_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(name_frame, text="Student Name:").grid(row=0, column=0, sticky=tk.W, padx=5)
        name_var = tk.StringVar()
        name_entry = ttk.Entry(name_frame, textvariable=name_var, width=30)
        name_entry.grid(row=0, column=1, sticky=tk.W)
        
        # Roll number field
        roll_frame = ttk.Frame(form_frame)
        roll_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(roll_frame, text="Roll Number:").grid(row=0, column=0, sticky=tk.W, padx=5)
        roll_var = tk.StringVar()
        roll_entry = ttk.Entry(roll_frame, textvariable=roll_var, width=20)
        roll_entry.grid(row=0, column=1, sticky=tk.W)
        
        # Email field
        email_frame = ttk.Frame(form_frame)
        email_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(email_frame, text="Email:").grid(row=0, column=0, sticky=tk.W, padx=5)
        email_var = tk.StringVar()
        email_entry = ttk.Entry(email_frame, textvariable=email_var, width=30)
        email_entry.grid(row=0, column=1, sticky=tk.W)
        
        # Buttons
        btn_frame = ttk.Frame(form_frame)
        btn_frame.pack(fill=tk.X, pady=20)
        
        def save_student():
            student_id = id_var.get().strip()
            name = name_var.get().strip()
            roll = roll_var.get().strip()
            email = email_var.get().strip()
            
            if not student_id:
                messagebox.showerror("Error", "Student ID is required")
                return False
                
            if not name:
                messagebox.showerror("Error", "Student Name is required")
                return False
                
            # Check if ID already exists
            if os.path.exists(self.names_file):
                with open(self.names_file, "r") as f:
                    for line in f:
                        if line.strip().startswith(student_id + " "):
                            messagebox.showerror("Error", f"Student ID {student_id} already exists")
                            return False
            
            # Validate email format if provided
            if email and not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                messagebox.showerror("Error", "Invalid email format")
                return False
                
            # Save student data
            with open(self.names_file, "a+") as f:
                f.write(f"{student_id} {name} [roll:{roll}] [email:{email}]\n")
                
            messagebox.showinfo("Success", "Student added successfully")
            add_window.destroy()
            self.load_students()
            return True
            
        def save_and_collect():
            if save_student():
                self.collect_face_data(id_var.get().strip(), name_var.get().strip())
                
        def cancel():
            add_window.destroy()
            
        ttk.Button(btn_frame, text="Save", command=save_student).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Save & Collect Face Data", 
                  command=save_and_collect).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=cancel).pack(side=tk.RIGHT, padx=5)
        
        # Focus on first field
        id_entry.focus_set()
        
    def edit_student(self):
        """Edit selected student"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Please select a student to edit")
            return
            
        # Get student data
        student_data = self.tree.item(selected[0], "values")
        student_id = student_data[0]
        student_name = student_data[1]
        student_roll = student_data[2]
        student_email = student_data[3] if len(student_data) > 3 else ""
        
        # Create edit window
        edit_window = tk.Toplevel(self.root)
        edit_window.title(f"Edit Student: {student_name}")
        edit_window.geometry("400x300")
        edit_window.config(bg="#f0f0f0")
        edit_window.grab_set()  # Make window modal
        
        # Form fields
        form_frame = ttk.Frame(edit_window)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # ID field (read-only)
        id_frame = ttk.Frame(form_frame)
        id_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(id_frame, text="Student ID:").grid(row=0, column=0, sticky=tk.W, padx=5)
        id_var = tk.StringVar(value=student_id)
        id_entry = ttk.Entry(id_frame, textvariable=id_var, width=10, state="readonly")
        id_entry.grid(row=0, column=1, sticky=tk.W)
        
        # Name field
        name_frame = ttk.Frame(form_frame)
        name_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(name_frame, text="Student Name:").grid(row=0, column=0, sticky=tk.W, padx=5)
        name_var = tk.StringVar(value=student_name)
        name_entry = ttk.Entry(name_frame, textvariable=name_var, width=30)
        name_entry.grid(row=0, column=1, sticky=tk.W)
        
        # Roll number field
        roll_frame = ttk.Frame(form_frame)
        roll_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(roll_frame, text="Roll Number:").grid(row=0, column=0, sticky=tk.W, padx=5)
        roll_var = tk.StringVar(value=student_roll)
        roll_entry = ttk.Entry(roll_frame, textvariable=roll_var, width=20)
        roll_entry.grid(row=0, column=1, sticky=tk.W)
        
        # Email field
        email_frame = ttk.Frame(form_frame)
        email_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(email_frame, text="Email:").grid(row=0, column=0, sticky=tk.W, padx=5)
        email_var = tk.StringVar(value=student_email)
        email_entry = ttk.Entry(email_frame, textvariable=email_var, width=30)
        email_entry.grid(row=0, column=1, sticky=tk.W)
        
        # Buttons
        btn_frame = ttk.Frame(form_frame)
        btn_frame.pack(fill=tk.X, pady=20)
        
        def save_changes():
            name = name_var.get().strip()
            roll = roll_var.get().strip()
            email = email_var.get().strip()
            
            if not name:
                messagebox.showerror("Error", "Student Name is required")
                return False
                
            # Validate email format if provided
            if email and not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                messagebox.showerror("Error", "Invalid email format")
                return False
                
            # Update student data in names.txt
            if os.path.exists(self.names_file):
                lines = []
                with open(self.names_file, "r") as f:
                    for line in f:
                        if line.strip().startswith(student_id + " "):
                            # Replace line with updated info
                            lines.append(f"{student_id} {name} [roll:{roll}] [email:{email}]\n")
                        else:
                            lines.append(line)
                            
                with open(self.names_file, "w") as f:
                    f.writelines(lines)
                    
            messagebox.showinfo("Success", "Student information updated")
            edit_window.destroy()
            self.load_students()
            return True
            
        def collect_faces():
            if save_changes():
                self.collect_face_data(student_id, name_var.get().strip())
            
        def cancel():
            edit_window.destroy()
            
        ttk.Button(btn_frame, text="Save Changes", command=save_changes).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Collect Face Data", command=collect_faces).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=cancel).pack(side=tk.RIGHT, padx=5)
        
    def delete_student(self):
        """Delete selected student"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Please select a student to delete")
            return
            
        # Get student data
        student_data = self.tree.item(selected[0], "values")
        student_id = student_data[0]
        student_name = student_data[1]
        
        # Confirm deletion
        if not messagebox.askyesno("Confirm Delete", 
                               f"Are you sure you want to delete student {student_name} (ID: {student_id})?"):
            return
            
        # Delete student data from names.txt
        if os.path.exists(self.names_file):
            lines = []
            with open(self.names_file, "r") as f:
                for line in f:
                    if not line.strip().startswith(student_id + " "):
                        lines.append(line)
                        
            with open(self.names_file, "w") as f:
                f.writelines(lines)
                
        # Delete face data
        face_images = glob.glob(f"{self.data_dir}/user.{student_id}.*.jpg")
        for img in face_images:
            try:
                os.remove(img)
            except Exception as e:
                print(f"Error deleting {img}: {e}")
                
        messagebox.showinfo("Success", 
                           f"Student {student_name} deleted successfully. {len(face_images)} face images removed.")
        self.load_students()
        
    def collect_face_data(self, student_id, name):
        """Launch face data collection for a student"""
        script_path = "collect_training_data.py"
        
        if not os.path.exists(script_path):
            messagebox.showerror("Error", 
                               f"Face collection script '{script_path}' not found.")
            return
            
        try:
            subprocess.run([sys.executable, script_path, student_id, name])
            
            # Retrain the model if we have enough data
            if os.path.exists("classifier.py"):
                if messagebox.askyesno("Train Model", 
                                      "Do you want to train the recognition model with the new data?"):
                    subprocess.run([sys.executable, "classifier.py"])
            
            # Refresh the student list
            self.load_students()
        except Exception as e:
            messagebox.showerror("Error", f"Error collecting face data: {e}")

# Standalone execution
if __name__ == "__main__":
    root = tk.Tk()
    app = StudentManager(root)
    root.mainloop()