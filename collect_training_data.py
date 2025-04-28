import cv2
import os

# Load the face classifier
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Create a dataset directory if it doesn't exist
data_path = "data/"
if not os.path.exists(data_path):
    os.makedirs(data_path)

# Ask for user ID (used to differentiate different people)
user_id = input("Enter user ID: ")
count = 0

# Start capturing video
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    
    if not ret or frame is None:
        print("Error: Could not read frame from camera. Retrying...")
        continue  # Skip this iteration and try again

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        count += 1
        face = gray[y:y+h, x:x+w]
        face_resized = cv2.resize(face, (200, 200))

        # Save the face images in the dataset folder
        file_name = f"{data_path}{user_id}_{count}.jpg"
        cv2.imwrite(file_name, face_resized)

        # Draw a rectangle around the face
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        cv2.putText(frame, f"Saving {count}/100", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    cv2.imshow("Face Capture", frame)

    # Stop after capturing 100 images or press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q') or count == 10:
        break


cap.release()
cv2.destroyAllWindows()

print(f"Images saved in {data_path} for user ID {user_id}.")
