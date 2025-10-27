import cv2
import os
import sqlite3
import time

def register_student():
    """
    Captures facial images using a guided UI (head outline) and saves student info to the database.
    Images are only captured when the face is centered within the guide.
    """
    name = input("Enter student's full name: ")
    enrollment = input("Enter student's enrollment number: ")

    # --- Database Interaction (Unchanged) ---
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()
    student_id = None
    try:
        cursor.execute("SELECT id FROM students WHERE enrollment_number = ?", (enrollment,))
        if cursor.fetchone():
            print(f"Error: A student with enrollment number {enrollment} already exists.")
            conn.close()
            return

        cursor.execute("INSERT INTO students (name, enrollment_number) VALUES (?, ?)", (name, enrollment))
        student_id = cursor.lastrowid
        conn.commit()
        print(f"✅ Student '{name}' added to database with ID: {student_id}")
    except Exception as e:
        print(f"🔴 Database Error: {e}")
        conn.close()
        return
    finally:
        conn.close()

    # --- Image Capture Setup ---
    dataset_path = 'dataset'
    if not os.path.exists(dataset_path):
        os.makedirs(dataset_path)

    cam = cv2.VideoCapture(0)
    # Set a common frame size and check for window visibility
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    face_detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    # --- UI Guide Parameters ---
    frame_w = int(cam.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_h = int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    # Define the target area for the face (a centered box)
    guide_size = int(frame_w * 0.4)  # Guide box is 40% of the frame width
    guide_center = (frame_w // 2, frame_h // 2)
    
    # Coordinates for the guide rectangle
    guide_left = guide_center[0] - guide_size // 2
    guide_right = guide_center[0] + guide_size // 2
    guide_top = guide_center[1] - guide_size // 2
    guide_bottom = guide_center[1] + guide_size // 2
    
    # Threshold for centering (allow the detected face to be slightly outside the guide)
    CENTER_THRESHOLD = 30 # pixels

    print("\n📸 START: Center your face within the guide outline to capture images.")
    
    count = 0
    REQUIRED_IMAGES = 20
    last_capture_time = time.time()
    CAPTURE_DELAY = 0.75 # Wait 0.75 seconds between captures

    # Loop to run the camera feed
    while count < REQUIRED_IMAGES: 
        ret, img = cam.read()
        if not ret:
            print("🔴 Failed to grab frame. Exiting.")
            break

        img = cv2.flip(img, 1) # Mirror effect
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Detect faces (small size for efficiency, but not too small)
        faces = face_detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(100, 100))

        # --- UI Drawing ---
        is_centered = False
        
        # 1. Draw the Centering Guide (Static outline)
        cv2.rectangle(img, (guide_left, guide_top), (guide_right, guide_bottom), (255, 255, 0), 2)
        cv2.putText(img, "GUIDE", (guide_left, guide_top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

        if len(faces) > 0:
            # Sort faces by size (area) and pick the largest one
            faces = sorted(faces, key=lambda x: x[2] * x[3], reverse=True)
            x, y, w, h = faces[0]
            
            # Calculate the center of the detected face
            face_center_x = x + w // 2
            face_center_y = y + h // 2
            
            # 2. Check Centering Condition
            # The face is centered if its center point is close to the guide center
            if (abs(face_center_x - guide_center[0]) < CENTER_THRESHOLD) and \
               (abs(face_center_y - guide_center[1]) < CENTER_THRESHOLD):
                
                is_centered = True
                rect_color = (0, 255, 0) # Green if centered
                status_message = "PERFECT! HOLD STILL"
            else:
                rect_color = (0, 0, 255) # Red if not centered
                status_message = "MOVE TO CENTER"
            
            # 3. Draw Bounding Box and Status
            cv2.rectangle(img, (x, y), (x+w, y+h), rect_color, 2)
            cv2.putText(img, f"FACE DETECTED", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, rect_color, 2)
        
        else:
            status_message = "NO FACE DETECTED"
            rect_color = (0, 0, 255)

        # 4. Draw main status and progress
        progress_text = f"Capturing: {count}/{REQUIRED_IMAGES} | Status: {status_message}"
        cv2.putText(img, progress_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)


        # --- Image Capturing Logic ---
        if is_centered and (time.time() - last_capture_time) > CAPTURE_DELAY:
            # Capture only when centered AND the delay has passed
            count += 1
            
            # Crop the face from the grayscale image
            face_crop = gray[y:y+h, x:x+w]
            
            # Save the captured image with the naming format: Name.ID.Count.jpg
            cv2.imwrite(f"{dataset_path}/{name}.{student_id}.{count}.jpg", face_crop)
            
            print(f"Captured image {count}/{REQUIRED_IMAGES}")
            last_capture_time = time.time()
            
            # Flash visual feedback (briefly change guide to white)
            cv2.rectangle(img, (guide_left, guide_top), (guide_right, guide_bottom), (255, 255, 255), -1)


        # Show the frame
        cv2.imshow('Registration - Center Face (Press ESC to exit)', img)
        
        # Exit condition: Press 'ESC' or count is complete
        if cv2.waitKey(1) & 0xFF == 27:
            print("\nRegistration interrupted by user.")
            break
            
    # Cleanup
    print("\nRegistration complete. Images saved successfully!")
    cam.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    register_student()