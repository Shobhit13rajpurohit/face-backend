import tkinter as tk
from tkinter import simpledialog, messagebox
import subprocess
import sys
import re

def run_recognize_mode():
    try:
        subprocess.run([sys.executable, "script.py", "recognize"])
    except Exception as e:
        print("Error running script:", e)

def validate_numeric(value):
    """Validate that input is numeric only"""
    return re.match(r'^\d*$', value) is not None

def run_collect_mode():
    # Create popup dialog
    popup = tk.Toplevel(root)
    popup.title("User Information")
    popup.geometry("300x200")
    popup.config(bg="#f0f0f0")
    popup.grab_set()  # Make the dialog modal
    
    # User ID field
    id_frame = tk.Frame(popup, bg="#f0f0f0")
    id_frame.pack(pady=10)
    
    id_label = tk.Label(id_frame, text="User ID (numeric):", bg="#f0f0f0")
    id_label.pack(side=tk.LEFT, padx=5)
    
    # Register a validation command
    vcmd = (popup.register(validate_numeric), '%P')
    id_entry = tk.Entry(id_frame, validate="key", validatecommand=vcmd, width=10)
    id_entry.pack(side=tk.LEFT)
    
    # User Name field
    name_frame = tk.Frame(popup, bg="#f0f0f0")
    name_frame.pack(pady=10)
    
    name_label = tk.Label(name_frame, text="User Name:", bg="#f0f0f0")
    name_label.pack(side=tk.LEFT, padx=5)
    
    name_entry = tk.Entry(name_frame, width=20)
    name_entry.pack(side=tk.LEFT)
    
    def start_collection():
        user_id = id_entry.get().strip()
        user_name = name_entry.get().strip()
        
        if not user_id:
            messagebox.showerror("Error", "User ID is required")
            return
        
        if not user_name:
            messagebox.showerror("Error", "User Name is required")
            return
        
        popup.destroy()
        try:
            subprocess.run([sys.executable, "script.py", "collect", user_id, user_name])
        except Exception as e:
            print("Error running script:", e)
    
    # Start Collection button
    button = tk.Button(popup, text="Start Collection", command=start_collection, 
                       bg="#4CAF50", fg="white", height=2, width=15)
    button.pack(pady=20)

root = tk.Tk()
root.title("Face Recognition Launcher")
root.geometry("300x200")
root.config(bg="#f0f0f0")

label = tk.Label(root, text="Select Mode", font=("Helvetica", 16), bg="#f0f0f0")
label.pack(pady=20)

collect_btn = tk.Button(root, text="👤 Add New Face", command=run_collect_mode, height=2, width=20, bg="#dff0d8")
collect_btn.pack(pady=5)

recognize_btn = tk.Button(root, text="🔍 Recognize Faces", command=run_recognize_mode, height=2, width=20, bg="#d9edf7")
recognize_btn.pack(pady=5)

quit_btn = tk.Button(root, text="❌ Quit", command=root.quit, height=1, width=10, bg="#f2dede")
quit_btn.pack(pady=15)

root.mainloop()