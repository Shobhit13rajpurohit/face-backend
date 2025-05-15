import cv2
import os
import glob
import sys

def load_names(file_path="names.txt"):
    """Load student names from file"""
    name_dict = {}
    try:
        with open(file_path, "r") as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 2:
                    id = int(parts[0])
                    name = " ".join(parts[1:])
                    name_dict[id] = name
    except FileNotFoundError:
        print("⚠️ Names file not found. Creating a new one.")
        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path) if os.path.dirname(file_path) else '.', exist_ok=True)
        # Create an empty file
        open(file_path, 'a').close()
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
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path) if os.path.dirname(file_path) else '.', exist_ok=True)
        with open(file_path, "a") as f:
            f.write(f"{user_id} {name}\n")
        print(f"✅ Added user: {user_id} - {name}")

def delete_user_data(user_id, folder="data"):
    """Delete user data from folder"""
    files = glob.glob(os.path.join(folder, f"user.{user_id}.*.jpg"))
    for f in files:
        os.remove(f)
    print(f"✅ Deleted {len(files)} images for user ID {user_id}")

def generate_dataset(img, id, img_id):
    """Save face image to dataset"""
    if not os.path.exists("data"):
        os.makedirs("data")
        
    filename = os.path.join("data", f"user.{id}.{img_id}.jpg")
    cv2.imwrite(filename, img)
    print(f"✅ Saved image: {filename}")

def draw_boundary(img, classifier, scaleFactor, minNeighbors, color, text, clf, name_dict):
    """Draw boundary around detected faces and identify them"""
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    features = classifier.detectMultiScale(gray_img, scaleFactor, minNeighbors)
    coords = []

    for (x, y, w, h) in features:
        cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
        if clf is not None:
            try:
                id, confidence = clf.predict(gray_img[y:y + h, x:x + w])
                # LBPH confidence works opposite - lower means better match
                # Typical threshold is around 70-80
                name = name_dict.get(id, "Unknown") if confidence < 70 else "Unknown"
                cv2.putText(img, f"{name} ({confidence:.1f})", (x, y - 4), 
                          cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 1, cv2.LINE_AA)
            except Exception as e:
                cv2.putText(img, f"Error: {str(e)[:10]}", (x, y - 4), 
                          cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 1, cv2.LINE_AA)
        coords = [x, y, w, h]
    return coords

def recognize(img, clf, faceCascade, name_dict):
    """Recognize faces in image"""
    color = {"blue": (255, 0, 0), "red": (0, 0, 255), "green": (0, 255, 0), "white": (255, 255, 255)}
    coords = draw_boundary(img, faceCascade, 1.1, 5, color["white"], "Face", clf, name_dict)
    return img

def detect(img, faceCascade, img_id, user_id, max_images=20):
    """Detect faces for dataset creation"""
    color = {"blue": (255, 0, 0), "red": (0, 0, 255), "green": (0, 255, 0), "white": (255, 255, 255)}
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(gray_img, 1.1, 5)
    
    coords = []
    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x + w, y + h), color["blue"], 2)
        roi_img = gray_img[y:y+h, x:x+w]
        # Resize to a standard size for better training
        roi_img = cv2.resize(roi_img, (200, 200))
        generate_dataset(roi_img, user_id, img_id)
        cv2.putText(img, f"Img: {img_id+1}/{max_images}", 
                  (x, y - 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color["green"], 2)
        coords = [x, y, w, h]
        break  # Just take the first face
        
    return img, len(coords) > 0

if __name__ == "__main__":
    # === MODE: from command line argument ===
    if len(sys.argv) < 2:
        print("Usage: python script.py [recognize|collect|delete] [user_id] [user_name]")
        sys.exit(1)
        
    MODE = sys.argv[1].lower()  # Normalize mode input
    MAX_IMAGES = 20
    user_id = None

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
    # Handle delete mode
    elif MODE == "delete":
        if len(sys.argv) >= 3:
            try:
                user_id = int(sys.argv[2])
                delete_user_data(user_id)
                print(f"✅ Deleted data for user ID: {user_id}")
                sys.exit(0)
            except ValueError:
                print("❌ Error: User ID must be a number")
                sys.exit(1)
        else:
            print("❌ Error: User ID required for delete mode")
            print("Usage: python script.py delete [user_id]")
            sys.exit(1)
    elif MODE != "recognize":
        print(f"❌ Error: Unknown mode '{MODE}'")
        print("Usage: python script.py [recognize|collect|delete] [user_id] [user_name]")
        sys.exit(1)

    # Load names dictionary
    name_dict = load_names()

    # Initialize cascades - use cv2.data.haarcascades path and handle missing files
    try:
        cascade_path = os.path.join(cv2.data.haarcascades, 'haarcascade_frontalface_default.xml')
        faceCascade = cv2.CascadeClassifier(cascade_path)
        if faceCascade.empty():
            print(f"❌ Error: Could not load face cascade classifier from {cascade_path}")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Error loading cascade files: {e}")
        sys.exit(1)

    # Load classifier if it exists
    clf = None
    if MODE == "recognize":
        if os.path.exists("classifier.yml"):
            try:
                # Check if opencv-contrib-python is installed
                if hasattr(cv2, 'face') and hasattr(cv2.face, 'LBPHFaceRecognizer_create'):
                    clf = cv2.face.LBPHFaceRecognizer_create()
                    clf.read("classifier.yml")
                else:
                    print("❌ Error: OpenCV face recognition module not available")
                    print("Please install opencv-contrib-python: pip install opencv-contrib-python")
                    sys.exit(1)
            except Exception as e:
                print(f"❌ Error loading classifier: {e}")
                sys.exit(1)
        else:
            print("⚠️ Warning: classifier.yml not found. Recognition will not work properly.")
            print("Run the classifier training script first to enable recognition.")

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
    
    # Main loop
    try:
        while True:
            ret, img = video_capture.read()
            if not ret:
                print("❌ Error: Could not read frame. Camera disconnected?")
                break
                
            # Handle different modes
            if MODE == "collect" and img_id < MAX_IMAGES:
                img, face_detected = detect(img, faceCascade, img_id, user_id, MAX_IMAGES)
                if face_detected:
                    img_id += 1
                    
            elif MODE == "recognize":
                if clf is not None:
                    img = recognize(img, clf, faceCascade, name_dict)
                else:
                    cv2.putText(img, "No classifier found", (10, 30), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            else:
                # If we've collected enough images or in an unknown mode
                if img_id >= MAX_IMAGES:
                    cv2.putText(img, f"✅ Collected {img_id} images. Press 'q' to quit.", 
                              (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            # Show status in collect mode
            if MODE == "collect":
                cv2.putText(img, f"Images: {img_id}/{MAX_IMAGES}", (10, 30), 
                          cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                if not face_detected:
                    cv2.putText(img, "No face detected!", (10, 60), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            cv2.imshow("Face Recognition", img)

            # Exit on 'q' press or when finished collecting
            key = cv2.waitKey(10) & 0xFF
            if key == ord('q') or (MODE == "collect" and img_id >= MAX_IMAGES):
                break
    except KeyboardInterrupt:
        print("\n✅ Program terminated by user")
    except Exception as e:
        print(f"❌ Error during processing: {e}")
    finally:
        # Clean up resources
        video_capture.release()
        cv2.destroyAllWindows()
        
        if MODE == "collect":
            print(f"✅ Collection complete! {img_id} images saved.")
            print("ℹ️ Please run the classifier training to update the model.")