import face_recognition
import pickle
import cv2
import os

def train_model():
    """Trains the face recognition model and saves encodings."""
    dataset_path = 'dataset'
    print("Starting training process... 🧠")

    known_encodings = []
    known_names = []

    # Loop over the image paths
    for image_name in os.listdir(dataset_path):
        if image_name.endswith(('.jpg', '.png', '.jpeg')):
            # Extract the person name from the image path
            name = image_name.split(".")[0]
            
            # Load the image and convert it from BGR to RGB
            image_path = os.path.join(dataset_path, image_name)
            image = cv2.imread(image_path)
            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Detect the (x, y)-coordinates of the bounding boxes
            boxes = face_recognition.face_locations(rgb, model='hog')
            
            # Compute the facial embedding for the face
            encodings = face_recognition.face_encodings(rgb, boxes)
            
            # Use the first encoding
            if encodings:
                known_encodings.append(encodings[0])
                known_names.append(name)

    # Save the facial encodings and names to disk
    data = {"encodings": known_encodings, "names": known_names}
    with open("encodings.pickle", "wb") as f:
        f.write(pickle.dumps(data))
        
    print("Training complete. Encodings saved to 'encodings.pickle'.")

if __name__ == "__main__":
    train_model()