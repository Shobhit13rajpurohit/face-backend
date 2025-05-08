import cv2
import os
import sys

def save_name(user_id, name, file_path="names.txt"):
    """Save student name to file"""
    existing_ids = set()
    try:
        with open(file_path, "r") as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 1:
                    existing_ids.add(int(parts[0]))
    except FileNotFoundError:
        pass

    if user_id not in existing_ids:
        with open(file_path, "a") as f:
            f.write(f"{user_id} {name}\n")
        print(f"✅ Added name: {name} with ID: {user_id}")
    else:
        print(f"⚠️ ID {user_id} already exists in names.txt")

def main():
    print("📸 Face Data Collection Tool")
    print("----------------------------")
    
    # Load the face classifier
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    if face_cascade.empty():
        print("❌ Error: Could not load face cascade classifier")
        sys.exit(1)

    # Create a dataset directory if it doesn't exist
    data_path = "data/"
    if not os.path.exists(data_path):
        os.makedirs(data_path)
        print(f"✅ Created data directory: {data_path}")

    # Ask for user ID and name
    # Check if provided as command-line arguments
    if len(sys.argv) >= 3:
        try:
            user_id = int(sys.argv[1])
            name = " ".join(sys.argv[2:])
            save_name(user_id, name)
        except ValueError:
            print("❌ Error: User ID must be a number")
            sys.exit(1)
    else:
        try:
            user_id = int(input("Enter user ID (numeric): "))
            name = input("Enter name: ")
            save_name(user_id, name)
        except ValueError:
            print("❌ Error: User ID must be a number")
            sys.exit(1)
        
    print(f"👤 Collecting faces for ID: {user_id}, Name: {name}")
    print("🔍 Position your face in front of the camera")
    
    # Set max_images to 20 for consistency with script.py
    max_images = 20
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

    while count < max_images:
        ret, frame = cap.read()
        
        if not ret or frame is None:
            print("⚠️ Could not read frame from camera. Retrying...")
            continue  # Skip this iteration and try again

        # Convert to grayscale for face detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

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
            face_resized = cv2.resize(face, (200, 200))

            # Save the face images in the dataset folder
            # Change filename to match format expected by classifier.py
            file_name = f"{data_path}user.{user_id}.{count}.jpg"
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