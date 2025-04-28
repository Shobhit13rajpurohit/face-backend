import cv2
import os
import glob
import sys

# === MODE: from command line argument ===
MODE = sys.argv[1] if len(sys.argv) > 1 else "recognize"

# === Auto Name Saving and Loading ===
def load_names(file_path="names.txt"):
    name_dict = {}
    try:
        with open(file_path, "r") as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 2:
                    id = int(parts[0])
                    name = " ".join(parts[1:])
                    name_dict[id] = name
    except Exception as e:
        print("⚠️ Could not load names:", e)
    return name_dict

def save_name(user_id, name, file_path="names.txt"):
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
    files = glob.glob(f"{folder}/user.{user_id}.*.jpg")
    for f in files:
        os.remove(f)
    print(f"✅ Deleted {len(files)} images for user ID {user_id}")

if MODE == "collect":
    if len(sys.argv) >= 4:
        # Get user_id and user_name from command line
        user_id = int(sys.argv[2])
        user_name = " ".join(sys.argv[3:])
        save_name(user_id, user_name)
    else:
        # Fallback to manual input if not provided via command line
        user_id = int(input("Enter numeric User ID: "))
        user_name = input("Enter name for this user: ")
        save_name(user_id, user_name)
else:
    user_id = None

name_dict = load_names()
MAX_IMAGES = 20


if not os.path.exists("data"):
    os.makedirs("data")

def generate_dataset(img, id, img_id):
    filename = f"data/user.{id}.{img_id}.jpg"
    cv2.imwrite(filename, img)
    print(f"✅ Saved image: {filename}")

def draw_boundary(img, classifier, scaleFactor, minNeighbors, color, text ,clf, name_dict):
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    features = classifier.detectMultiScale(gray_img, scaleFactor, minNeighbors)
    coords = []

    for (x, y, w, h) in features:
        cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
        if clf is not None:
            id, confidence = clf.predict(gray_img[y:y + h, x:x + w])
            name = name_dict.get(id, "Unknown") if confidence < 80 else "Unknown"
            cv2.putText(img, name, (x, y - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 1, cv2.LINE_AA)
        coords = [x, y, w, h]
    return coords

def recognize(img, clf, faceCascade, name_dict):
    color = {"blue": (255, 0, 0), "red": (0, 0, 255), "green": (0, 255, 0), "white": (255, 255, 255)}
    coords = draw_boundary(img, faceCascade, 1.1, 10, color["white"], "Face", clf, name_dict)
    return img

def detect(img, faceCascade, eyesCascade, MouthCascade, noseCascade, img_id, user_id):
    color = {"blue": (255, 0, 0), "red": (0, 0, 255), "green": (0, 255, 0), "white": (255, 255, 255)}
    coords = draw_boundary(img, faceCascade, 1.1, 10, color["blue"], "Face", clf=None, name_dict={})
    if len(coords) == 4:
        roi_img = img[coords[1]: coords[1]+coords[3], coords[0]: coords[0]+coords[2]]
        generate_dataset(roi_img, user_id, img_id)
        cv2.putText(img, f"Img: {img_id+1}/{MAX_IMAGES}", (coords[0], coords[1] - 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color["green"], 2)
    return img

faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
eyesCascade = cv2.CascadeClassifier('haarcascade_eye.xml')
MouthCascade = cv2.CascadeClassifier('Mouth.xml')
noseCascade = cv2.CascadeClassifier('nose.xml')

clf = cv2.face.LBPHFaceRecognizer_create()
clf.read("classifier.yml")

video_capture = cv2.VideoCapture(0)
img_id = 0

if not video_capture.isOpened():
    print("Error: Could not open camera.")
    exit()

while True:
    _, img = video_capture.read()

    if MODE == "collect" and img_id < MAX_IMAGES:
        img = detect(img, faceCascade, eyesCascade, MouthCascade, noseCascade, img_id, user_id)
        img_id += 1
    elif MODE == "recognize":
        img = recognize(img, clf, faceCascade, name_dict)
    else:
        cv2.putText(img, f"✅ Collected {MAX_IMAGES} images. Press 'q' to quit.", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    cv2.imshow("Face Detection", img)

    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

video_capture.release()
cv2.destroyAllWindows()