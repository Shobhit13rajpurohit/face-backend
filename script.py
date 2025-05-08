import cv2
import os
import glob
import sys
import json
import subprocess

subprocess.call(['python', 'collect_training_data.py'])

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

def load_names(file_path="names.txt"):
    """Load student names from file"""
    name_dict = {}
    try:
        with open(file_path, "r") as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 2:
                    id = int(parts[0])
                    
                    # Extract name (everything before first [tag])
                    name_parts = []
                    for part in parts[1:]:
                        if part.startswith("["):
                            break
                        name_parts.append(part)
                    name = " ".join(name_parts)
                    
                    name_dict[id] = name
    except Exception as e:
        print("⚠️ Could not load names:", e)
    return name_dict

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

def delete_user_data(user_id, folder="data"):
    """Delete user data from folder"""
    files = glob.glob(f"{folder}/user.{user_id}.*.jpg")
    for f in files:
        os.remove(f)
    print(f"✅ Deleted {len(files)} images for user ID {user_id}")

def generate_dataset(img, id, img_id, config):
    """Save face image to dataset"""
    data_dir = config["paths"]["data_dir"]
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        
    filename = f"{data_dir}/user.{id}.{img_id}.jpg"
    cv2.imwrite(filename, img)
    print(f"✅ Saved image: {filename}")

def draw_boundary(img, classifier, color, text, clf, name_dict, config):
    """Draw boundary around detected faces and identify them"""
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Use parameters from config
    detection_params = config["face_detection"]
    confidence_threshold = config["recognition"]["confidence_threshold"]
    
    features = classifier.detectMultiScale(
        gray_img, 
        scaleFactor=detection_params["scaleFactor"],
        minNeighbors=detection_params["minNeighbors"],
        minSize=tuple(detection_params["minSize"])
    )
    
    coords = []

    for (x, y, w, h) in features:
        cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
        if clf is not None:
            try:
                id, confidence = clf.predict(gray_img[y:y + h, x:x + w])
                name = name_dict.get(id, "Unknown") if confidence < confidence_threshold else "Unknown"
                cv2.putText(img, f"{name} ({confidence:.1f})", (x, y - 4), 
                          cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 1, cv2.LINE_AA)
            except Exception as e:
                cv2.putText(img, f"Error: {str(e)[:10]}", (x, y - 4), 
                          cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 1, cv2.LINE_AA)
        coords = [x, y, w, h]
    return coords

def recognize(img, clf, faceCascade, name_dict, config):
    """Recognize faces in image"""
    color = {"blue": (255, 0, 0), "red": (0, 0, 255), "green": (0, 255, 0), "white": (255, 255, 255)}
    coords = draw_boundary(img, faceCascade, color["white"], "Face", clf, name_dict, config)
    return img

def detect(img, faceCascade, img_id, user_id, config):
    """Detect faces for dataset creation"""
    color = {"blue": (255, 0, 0), "red": (0, 0, 255), "green": (0, 255, 0), "white": (255, 255, 255)}
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    detection_params = config["face_detection"]
    max_images = config["collection"]["max_images"]
    image_size = tuple(config["collection"]["image_size"])
    
    faces = faceCascade.detectMultiScale(
        gray_img, 
        scaleFactor=detection_params["scaleFactor"],
        minNeighbors=detection_params["minNeighbors"],
        minSize=tuple(detection_params["minSize"])
    )
    
    coords = []
    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x + w, y + h), color["blue"], 2)
        roi_img = gray_img[y:y+h, x:x+w]
        # Resize to a standard size for better training
        roi_img = cv2.resize(roi_img, image_size)
        generate_dataset(roi_img, user_id, img_id, config)
        cv2.putText(img, f"Img: {img_id+1}/{max_images}", 
                  (x, y - 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color["green"], 2)
        coords = [x, y, w, h]
        break  # Just take the first face
        
    return img, len(coords) > 0

if __name__ == "__main__":
    # Load configuration
    config = load_config()
    
    # === MODE: from command line argument ===
    if len(sys.argv) < 2:
        print("Usage: python script.py [recognize|collect] [user_id] [user_name]")
        sys.exit(1)
        
    MODE = sys.argv[1]
    MAX_IMAGES = config["collection"]["max_images"]

    # Handle collection mode
    if MODE == "collect":
        if len(sys.argv) >= 4:
            # Get user_id and user_name from command line
            try:
                user_id = int(sys.argv[2])
                user_name = " ".join(sys.argv[3:])
                save_name(user_id, user_name)
            except ValueError:
                print("❌ Error: User ID must be a number")
                sys.exit(1)
        else:
            # Fallback to manual input if not provided via command line
            try:
                user_id = int(input("Enter numeric User ID: "))
                user_name = input("Enter name for this user: ")
                save_name(user_id, user_name)
            except ValueError:
                print("❌ Error: User ID must be a number")
                sys.exit(1)
    else:
        user_id = None

    # Load names dictionary
    name_dict = load_names(config["paths"]["names_file"])

    # Initialize cascades - use cv2.data.haarcascades path and handle missing files
    try:
        faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        if faceCascade.empty():
            print("❌ Error: Could not load face cascade classifier")
            sys.exit(1)
            
        # These are optional, only used in specialized detection modes
        # Check if the optional files exist before trying to load them
        eyesCascade = None
        MouthCascade = None
        noseCascade = None
        
        if os.path.exists(cv2.data.haarcascades + 'haarcascade_eye.xml'):
            eyesCascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        
        if os.path.exists('Mouth.xml'):
            MouthCascade = cv2.CascadeClassifier('Mouth.xml')
        
        if os.path.exists('nose.xml'):
            noseCascade = cv2.CascadeClassifier('nose.xml')
            
    except Exception as e:
        print(f"❌ Error loading cascade files: {e}")
        sys.exit(1)

    # Load classifier if it exists
    clf = None
    if MODE == "recognize":
        classifier_file = config["paths"]["classifier_file"]
        if os.path.exists(classifier_file):
            try:
                # Check if opencv-contrib-python is installed
                if hasattr(cv2, 'face') and hasattr(cv2.face, 'LBPHFaceRecognizer_create'):
                    clf = cv2.face.LBPHFaceRecognizer_create()
                    clf.read(classifier_file)
                else:
                    print("❌ Error: OpenCV face recognition module not available")
                    print("Please install opencv-contrib-python: pip install opencv-contrib-python")
                    sys.exit(1)
            except Exception as e:
                print(f"❌ Error loading classifier: {e}")
                sys.exit(1)
        else:
            print(f"⚠️ Warning: {classifier_file} not found. Recognition will not work properly.")

    # Create attendance directory if it doesn't exist
    attendance_dir = config["paths"]["attendance_dir"]
    if not os.path.exists(attendance_dir):
        os.makedirs(attendance_dir)
        print(f"✅ Created attendance directory: {attendance_dir}")

    # Start video capture
    video_capture = cv2.VideoCapture(0)
    img_id = 0
    face_detected = False

    if not video_capture.isOpened():
        print("❌ Error: Could not open camera.")
        sys.exit(1)

    print(f"🎥 Camera opened successfully. Mode: {MODE}")
    if MODE == "collect":
        print(f"👤 Collecting data for user ID: {user_id}, Name: {name_dict.get(user_id, 'Unknown')}")
    
    while True:
        ret, img = video_capture.read()
        if not ret:
            print("❌ Error: Could not read frame")
            break
            
        # Handle different modes
        if MODE == "collect" and img_id < MAX_IMAGES:
            img, face_detected = detect(img, faceCascade, img_id, user_id, config)
            if face_detected:
                img_id += 1
                
        elif MODE == "recognize":
            if clf is not None:
                img = recognize(img, clf, faceCascade, name_dict, config)
            else:
                cv2.putText(img, "No classifier found", (10, 30), 
                          cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        else:
            # If we've collected enough images or in an unknown mode
            cv2.putText(img, f"✅ Collected {min(img_id, MAX_IMAGES)} images. Press 'q' to quit.", 
                      (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # Show status in collect mode
        if MODE == "collect" and img_id < MAX_IMAGES:
            cv2.putText(img, f"Images: {img_id}/{MAX_IMAGES}", (10, 30), 
                      cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            if not face_detected:
                cv2.putText(img, "No face detected!", (10, 60), 
                          cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        cv2.imshow("Face Detection", img)

        # Exit on 'q' press or when finished collecting
        if cv2.waitKey(10) & 0xFF == ord('q') or (MODE == "collect" and img_id >= MAX_IMAGES):
            break

    video_capture.release()
    cv2.destroyAllWindows()
    
    if MODE == "collect":
        print(f"✅ Collection complete! {img_id} images saved.")
        print("ℹ️ Please run the classifier training to update the model.")