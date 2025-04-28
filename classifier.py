import numpy as np
from PIL import Image
import os
import cv2

def train_classifier(data_dir):
    # Ensure OpenCV's LBPHFaceRecognizer is available
    if not hasattr(cv2.face, "LBPHFaceRecognizer_create"):
        print("❌ Error: OpenCV is missing face recognizer module!")
        return

    clf = cv2.face.LBPHFaceRecognizer_create()
    detector = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    # Read all images in dataset
    image_paths = [os.path.join(data_dir, f) for f in os.listdir(data_dir) if f.endswith(('.jpg', '.png', '.jpeg'))]
    
    faces = []
    ids = []

    for image_path in image_paths:
        try:
            # Convert image to grayscale
            gray_image = Image.open(image_path).convert('L')
            image_np = np.array(gray_image, "uint8")

            # Extract numeric ID from filename
            filename = os.path.basename(image_path)
            id_str = filename.split("_")[-1].split(".")[0]  # Extracts number at the end


            # Ensure ID is a number
            if not id_str.isdigit():
                print(f"⚠️ Skipping {filename}: ID must be a number")
                continue

            user_id = int(id_str)

            # Detect faces in the image
            detected_faces = detector.detectMultiScale(image_np)
            for (x, y, w, h) in detected_faces:
                faces.append(image_np[y:y+h, x:x+w])
                ids.append(user_id)

        except Exception as e:
            print(f"❌ Error processing {image_path}: {e}")

    # Ensure faces were detected before training
    if len(faces) > 0:
        clf.train(faces, np.array(ids, dtype=np.int32))  # ✅ Fixed ID issue
        clf.write("classifier.yml")
        print("✅ Training complete! classifier.yml saved.")
    else:
        print("❌ No faces detected. Check your dataset.")

# Run the training function
train_classifier("data")
