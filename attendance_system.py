import cv2
import os
import sys
import datetime
import csv
import pandas as pd
from pathlib import Path

class AttendanceSystem:
    def __init__(self):
        # Create necessary folders
        if not os.path.exists("data"):
            os.makedirs("data")
        if not os.path.exists("attendance"):
            os.makedirs("attendance")
            
        # Initialize face detection and recognition components
        try:
            self.faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            if self.faceCascade.empty():
                print("❌ Error: Could not load face cascade classifier")
                sys.exit(1)
        except Exception as e:
            print(f"❌ Error loading cascade files: {e}")
            sys.exit(1)
            
        self.name_dict = self.load_names()
        
        # Check if names.txt exists and has content
        if not self.name_dict:
            print("❌ Error: No students registered. Please register students first.")
            print("Create a names.txt file with format: 'ID Name' on each line (e.g., '1 John Smith')")
            sys.exit(1)
            
        # Load classifier if it exists
        self.clf = None
        classifier_path = "classifier.yml"
        if os.path.exists(classifier_path):
            try:
                # Check if opencv-contrib-python is installed
                if not hasattr(cv2, 'face') or not hasattr(cv2.face, 'LBPHFaceRecognizer_create'):
                    print("❌ Error: OpenCV face recognition module not available")
                    print("Please install opencv-contrib-python: pip install opencv-contrib-python")
                    sys.exit(1)
                    
                self.clf = cv2.face.LBPHFaceRecognizer_create()
                self.clf.read(classifier_path)
                print(f"✅ Classifier loaded successfully from {classifier_path}")
            except Exception as e:
                print(f"❌ Error loading classifier from {classifier_path}: {e}")
                print("Please ensure the classifier file is valid or train a new model.")
                sys.exit(1)
        else:
            print(f"❌ Error: Classifier file '{classifier_path}' not found.")
            print("Please train the model first to generate the classifier file.")
            sys.exit(1)
        
        # Store today's date and track recorded attendances to avoid duplicates
        self.today = datetime.datetime.now().strftime("%Y-%m-%d")
        self.attendance_file = os.path.join("attendance", f"{self.today}.csv")
        self.marked_attendance = self.load_today_attendance()
    
    def load_names(self, file_path="names.txt"):
        """Load student names from file"""
        name_dict = {}
        try:
            if not os.path.exists(file_path):
                print(f"❌ Names file not found: {file_path}")
                return name_dict
                
            with open(file_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line:  # Skip empty lines
                        continue
                        
                    parts = line.split()
                    if len(parts) >= 2:
                        try:
                            id = int(parts[0])
                            name = " ".join(parts[1:])
                            name_dict[id] = name
                        except ValueError:
                            print(f"⚠️ Warning: Invalid ID format in line: '{line}'. Skipping.")
                            continue
            
            if not name_dict:
                print(f"⚠️ Warning: No valid student entries found in {file_path}")
                
        except Exception as e:
            print(f"❌ Error loading names file: {e}")
        
        print(f"✅ Loaded {len(name_dict)} student records")
        return name_dict
    
    def load_today_attendance(self):
        """Load today's attendance records to prevent duplicates"""
        marked = set()
        if os.path.exists(self.attendance_file):
            try:
                df = pd.read_csv(self.attendance_file)
                for _, row in df.iterrows():
                    # Handle potential data type issues
                    try:
                        marked.add(int(row['ID']))
                    except (ValueError, TypeError) as e:
                        print(f"⚠️ Warning: Invalid ID in attendance file: {row['ID']}")
                print(f"✅ Loaded {len(marked)} existing attendance records for today")
            except Exception as e:
                print(f"⚠️ Error loading today's attendance: {e}")
        return marked
    
    def create_attendance_file(self):
        """Create attendance CSV file with headers if it doesn't exist"""
        if not os.path.exists(self.attendance_file):
            try:
                os.makedirs(os.path.dirname(self.attendance_file), exist_ok=True)
                with open(self.attendance_file, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['ID', 'Name', 'Date', 'Time'])
                print(f"✅ Created new attendance file: {self.attendance_file}")
            except Exception as e:
                print(f"❌ Error creating attendance file: {e}")
    
    def mark_attendance(self, student_id):
        """Record student attendance if not already marked today"""
        if student_id in self.marked_attendance:
            return False  # Already marked
        
        # Get current time
        now = datetime.datetime.now()
        current_date = now.strftime("%Y-%m-%d")
        current_time = now.strftime("%H:%M:%S")
        
        # Get student name
        student_name = self.name_dict.get(student_id, "Unknown")
        
        try:
            # Create file if it doesn't exist
            self.create_attendance_file()
            
            # Record attendance
            with open(self.attendance_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([student_id, student_name, current_date, current_time])
            
            # Add to marked set to prevent duplicates
            self.marked_attendance.add(student_id)
            return True
        except Exception as e:
            print(f"❌ Error marking attendance for {student_name} (ID: {student_id}): {e}")
            return False
    
    def draw_boundary(self, img, scaleFactor=1.1, minNeighbors=5):
        """Detect faces and identify students"""
        if img is None:
            return img
            
        try:
            gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = self.faceCascade.detectMultiScale(gray_img, scaleFactor, minNeighbors)
            
            for (x, y, w, h) in faces:
                # Draw rectangle around face
                cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
                
                if self.clf is not None:
                    try:
                        # Get face region
                        face_region = gray_img[y:y + h, x:x + w]
                        
                        # Skip if face region is empty
                        if face_region.size == 0:
                            continue
                            
                        # Predict who this face belongs to
                        id, confidence = self.clf.predict(face_region)
                        
                        # Lower confidence value means better match (in LBPH)
                        if confidence < 80:
                            name = self.name_dict.get(id, "Unknown")
                            
                            # Mark attendance
                            just_marked = self.mark_attendance(id)
                            
                            # Display name and attendance status
                            status = "✅ Marked!" if just_marked else "Already Recorded"
                            cv2.putText(img, f"{name} ({status})", (x, y - 10), 
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)
                        else:
                            # Unknown face
                            cv2.putText(img, f"Unknown ({confidence:.1f})", (x, y - 10), 
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)
                    except Exception as e:
                        print(f"⚠️ Error processing face: {e}")
                        cv2.putText(img, "Error", (x, y - 10), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)
        except Exception as e:
            print(f"❌ Error in face detection: {e}")
            
        return img
    
    def run(self):
        """Run the attendance system"""
        video_capture = None
        try:
            # Access webcam
            video_capture = cv2.VideoCapture(0)
            
            if not video_capture.isOpened():
                print("❌ Error: Could not open camera.")
                return
            
            # Display current date and attendance count
            print(f"✅ Attendance System running for: {self.today}")
            print(f"✅ Recording to: {self.attendance_file}")
            print("Press 'q' to quit")
            
            while True:
                ret, frame = video_capture.read()
                
                if not ret:
                    print("⚠️ Warning: Could not read frame from camera. Retrying...")
                    # Try to reopen the camera if frame reading fails
                    video_capture.release()
                    video_capture = cv2.VideoCapture(0)
                    if not video_capture.isOpened():
                        print("❌ Error: Could not reopen camera.")
                        break
                    continue
                    
                # Process frame for face detection and attendance marking
                frame = self.draw_boundary(frame)
                
                # Show stats on the frame
                cv2.putText(frame, f"Date: {self.today}", (10, 30), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, f"Students Present: {len(self.marked_attendance)}", (10, 60), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                # Display the frame
                cv2.imshow("Attendance System", frame)
                
                # Press 'q' to quit
                if cv2.waitKey(10) & 0xFF == ord('q'):
                    break
                
        except KeyboardInterrupt:
            print("\n✅ Program stopped by user.")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
        finally:
            # Clean up
            if video_capture is not None:
                video_capture.release()
            cv2.destroyAllWindows()
            
            print(f"\n📊 Today's Attendance Summary:")
            print(f"- Date: {self.today}")
            print(f"- Students Present: {len(self.marked_attendance)}")
            print(f"- Attendance recorded in: {self.attendance_file}")


if __name__ == "__main__":
    try:
        # Check if opencv-contrib-python is installed before creating the system
        if not hasattr(cv2, 'face') or not hasattr(cv2.face, 'LBPHFaceRecognizer_create'):
            print("❌ Error: OpenCV face recognition module not available")
            print("Please install opencv-contrib-python: pip install opencv-contrib-python")
            sys.exit(1)
            
        # Create and run attendance system
        attendance_system = AttendanceSystem()
        attendance_system.run()
    except ImportError as e:
        print(f"❌ Error: Missing required libraries: {e}")
        print("Please install the required libraries:")
        print("pip install opencv-python opencv-contrib-python pandas")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)