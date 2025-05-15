import numpy as np
from PIL import Image
import os
import cv2
import sys

def train_classifier(data_dir):
    # Ensure data directory exists
    if not os.path.exists(data_dir):
        print(f"❌ Error: Data directory '{data_dir}' does not exist!")
        os.makedirs(data_dir)
        print(f"✅ Created data directory: {data_dir}")
        return

    # Check if there are any images in the directory
    image_paths = [os.path.join(data_dir, f) for f in os.listdir(data_dir) if f.endswith(('.jpg', '.png', '.jpeg'))]
    if not image_paths:
        print(f"❌ Error: No images found in '{data_dir}' directory!")
        return

    # Ensure OpenCV's LBPHFaceRecognizer is available
    try:
        clf = cv2.face.LBPHFaceRecognizer_create()
    except AttributeError:
        print("❌ Error: OpenCV is missing face recognizer module!")
        print("Please install opencv-contrib-python: pip install opencv-contrib-python")
        return

    # Load face detector
    detector = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    if detector.empty():
        print("❌ Error: Could not load face cascade classifier!")
        return
    
    faces = []
    ids = []

    print(f"🔍 Processing {len(image_paths)} images...")

    for image_path in image_paths:
        try:
            # Convert image to grayscale
            gray_image = Image.open(image_path).convert('L')
            image_np = np.array(gray_image, "uint8")

            # Extract numeric ID from filename
            # Format is user.{id}.{count}.jpg as per script.py and collect_training_data.py
            filename = os.path.basename(image_path)
            parts = filename.split(".")
            
            if len(parts) < 3 or not parts[0] == "user" or not parts[1].isdigit():
                print(f"⚠️ Skipping {filename}: Invalid filename format. Expected: user.{id}.{count}.jpg")
                continue

            user_id = int(parts[1])

            # Detect faces in the image
            detected_faces = detector.detectMultiScale(image_np, scaleFactor=1.1, minNeighbors=5)
            
            if len(detected_faces) == 0:
                print(f"⚠️ No face detected in {filename}")
                continue
                
            for (x, y, w, h) in detected_faces:
                # Resize to standard size for better recognition
                face = cv2.resize(image_np[y:y+h, x:x+w], (200, 200))
                faces.append(face)
                ids.append(user_id)
                print(f"✅ Processed {filename} for user ID {user_id}")
                break  # Use only the first face detected as in script.py

        except Exception as e:
            print(f"❌ Error processing {image_path}: {e}")

    # Ensure faces were detected before training
    if len(faces) > 0:
        print(f"🧠 Training classifier with {len(faces)} faces...")
        clf.train(faces, np.array(ids, dtype=np.int32))
        clf.write("classifier.yml")
        print(f"✅ Training complete! classifier.yml saved with {len(faces)} faces for {len(set(ids))} users.")
    else:
        print("❌ No faces detected. Check your dataset.")

# Run the training function
if __name__ == "__main__":
    # Accept command line argument for data directory
    data_dir = "data"
    if len(sys.argv) > 1:
        data_dir = sys.argv[1]
    
    train_classifier(data_dir)