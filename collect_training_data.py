import cv2
import os
import sys
import json

def load_config():
    """Load configuration from config.json"""
    try:
        with open("config.json", "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️ Could not load config.json: {e}")
        # Return default config
        return {
            "face_detection": {
                "scaleFactor": 1.3,
                "minNeighbors": 5,
                "minSize": [30, 30]
            },
            "paths": {
                "data_dir": "data",
                "attendance_dir": "attendance",
                "names_file": "names.txt",
                "classifier_file": "classifier.yml"
            },
            "collection": {
                "max_images": 20,
                "image_size": [200, 200]
            },
            "recognition": {
                "confidence_threshold": 80
            }
        }

def save_name(user_id, name, file_path=None, roll="", email=""):
    """Save student name and optional details to file"""
    # Load config if file_path is not provided
    if file_path is None:
        config = load_config()
        file_path = config["paths"]["names_file"]
    
    # Format extra details if provided
    user_data = f"{user_id} {name}"
    if roll or email:
        if roll:
            user_data += f" [roll:{roll}]"
        if email:
            user_data += f" [email:{email}]"
    
    existing_ids = set()
    existing_lines = []
    try:
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                for line in f:
                    existing_lines.append(line)
                    parts = line.strip().split()
                    if len(parts) >= 1 and parts[0].isdigit():
                        existing_ids.add(int(parts[0]))
    except FileNotFoundError:
        pass

    # Update or add user
    try:
        with open(file_path, "w") as f:
            # Write existing lines except for the one with the same ID
            for line in existing_lines:
                parts = line.strip().split()
                if len(parts) >= 1 and parts[0].isdigit() and int(parts[0]) == user_id:
                    continue  # Skip this line as we'll add an updated version
                f.write(line)
            
            # Add the new entry
            f.write(user_data + "\n")
        
        if user_id in existing_ids:
            print(f"✅ Updated info for ID: {user_id}")
        else:
            print(f"✅ Added name: {name} with ID: {user_id}")
        return True
    except Exception as e:
        print(f"❌ Error updating names file: {e}")
        return False

def main():
    # Load configuration
    config = load_config()
    
    print("📸 Face Data Collection Tool")
    print("----------------------------")
    
    # Load the face classifier
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    if face_cascade.empty():
        print("❌ Error: Could not load face cascade classifier")
        sys.exit(1)

    # Create a dataset directory if it doesn't exist
    data_path = config["paths"]["data_dir"]
    if not os.path.exists(data_path):
        os.makedirs(data_path)
        print(f"✅ Created data directory: {data_path}")

    # Ask for user ID and name
    # Check if provided as command-line arguments
    if len(sys.argv) >= 3:
        try:
            user_id = int(sys.argv[1])
            name = " ".join(sys.argv[2:])
            
            # Check for optional arguments like --roll or --email
            roll = ""
            email = ""
            for i, arg in enumerate(sys.argv):
                if arg == "--roll" and i+1 < len(sys.argv):
                    roll = sys.argv[i+1]
                elif arg == "--email" and i+1 < len(sys.argv):
                    email = sys.argv[i+1]
            
            save_name(user_id, name, config["paths"]["names_file"], roll, email)
        except ValueError:
            print("❌ Error: User ID must be a number")
            sys.exit(1)
    else:
        try:
            user_id = int(input("Enter user ID (numeric): "))
            name = input("Enter name: ")
            roll = input("Enter roll number (optional): ")
            email = input("Enter email (optional): ")
            save_name(user_id, name, config["paths"]["names_file"], roll, email)
        except ValueError:
            print("❌ Error: User ID must be a number")
            sys.exit(1)
        
    print(f"👤 Collecting faces for ID: {user_id}, Name: {name}")
    print("🔍 Position your face in front of the camera")
    
    # Use max_images from config
    max_images = config["collection"]["max_images"]
    print(f"📊 Will capture {max_images} images automatically")
    print("⌨️ Press 'q' to quit early")

    # How many images to collect
    count = 0

    # Start capturing video
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("❌ Error: Could not open camera.")
        sys.exit(1)

    # Wait a bit for camera to initialize
    for i in range(5, 0, -1):
        ret, frame = cap.read()
        if ret:
            cv2.putText(frame, f"Starting capture in {i}...", (50, 50), 
                      cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.imshow("Face Capture", frame)
            cv2.waitKey(1000)  # Wait 1 second between countdown

    # Get parameters from config
    detection_params = config["face_detection"]
    image_size = tuple(config["collection"]["image_size"])
    
    while count < max_images:
        ret, frame = cap.read()
        
        if not ret or frame is None:
            print("⚠️ Could not read frame from camera. Retrying...")
            continue  # Skip this iteration and try again

        # Convert to grayscale for face detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(
            gray, 
            scaleFactor=detection_params["scaleFactor"],
            minNeighbors=detection_params["minNeighbors"],
            minSize=tuple(detection_params["minSize"])
        )

        # Draw rectangle around face and add text
        cv2.putText(frame, f"Capturing: {count}/{max_images}", (10, 30), 
                  cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                  
        if len(faces) == 0:
            cv2.putText(frame, "No face detected!", (10, 60), 
                      cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        for (x, y, w, h) in faces:
            count += 1
            
            # Extract the face region
            face = gray[y:y+h, x:x+w]
            # Use image size from config
            face_resized = cv2.resize(face, image_size)

            # Save the face images in the dataset folder
            # Change filename to match format expected by classifier.py
            file_name = f"{data_path}/user.{user_id}.{count}.jpg"
            cv2.imwrite(file_name, face_resized)

            # Draw a rectangle around the face
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(frame, f"Saving {count}/{max_images}", (x, y-10), 
                      cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            # Only capture one face at a time
            break

        cv2.imshow("Face Capture", frame)

        # Check for 'q' key press or if we've captured enough images
        key = cv2.waitKey(100) & 0xFF
        if key == ord('q') or count >= max_images:
            break

    cap.release()
    cv2.destroyAllWindows()

    print(f"✅ Completed! {count} images saved in {data_path} for user ID {user_id}.")
    print("ℹ️ Next step: Run the classifier training to update the model.")

if __name__ == "__main__":
    main()