import face_recognition
import pickle
import cv2
import sqlite3
from datetime import datetime
import pandas as pd
import os
import time # Added for potential future timing/debugging

# --- Configuration for Performance Improvement ---
# Process every Nth frame. N=3 is a good balance of speed and smoothness.
FRAME_SKIP = 3
# Scale factor for processing. 0.25 means 1/4 the height and 1/4 the width.
# This results in processing 1/16th the number of pixels.
SCALE_FACTOR = 0.25 


def mark_attendance():
    """Main function to run the attendance system using face recognition."""
    
    # Load the known faces and embeddings
    print("Loading facial encodings...")
    try:
        data = pickle.loads(open("encodings.pickle", "rb").read())
    except FileNotFoundError:
        print("🔴 ERROR: 'encodings.pickle' file not found. Please run an encoding script first.")
        return
        
    # Connect to database
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()

    # Initialize video stream
    print("Starting video stream...")
    vs = cv2.VideoCapture(0)
    if not vs.isOpened():
        print("🔴 ERROR: Could not open video stream. Check camera connection/permissions.")
        return

    # Keep track of who has been marked present
    present_today = set()
    
    # Variables for intermittent processing and drawing
    frame_count = 0
    names = [] # List to hold names from the last processed frame
    boxes = [] # List to hold box locations from the last processed frame
    
    print("System running. Press 'q' to quit.")

    while True:
        ret, frame = vs.read()
        if not ret:
            print("🔴 ERROR: Failed to grab frame.")
            break
            
        frame_count += 1
        
        # --- Intermittent Processing and Downscaling for Performance ---
        if frame_count % FRAME_SKIP == 0:
            # Reset lists for the new process cycle
            names = []
            boxes = []
            
            # 1. Downscale the frame (e.g., to 1/4 size)
            small_frame = cv2.resize(frame, (0, 0), fx=SCALE_FACTOR, fy=SCALE_FACTOR)
            rgb = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
            
            # 2. Find faces and embeddings on the small frame (faster)
            current_boxes = face_recognition.face_locations(rgb, model='hog')
            current_encodings = face_recognition.face_encodings(rgb, current_boxes)

            # Loop over the facial embeddings
            for encoding in current_encodings:
                matches = face_recognition.compare_faces(data["encodings"], encoding)
                name = "Unknown"

                if True in matches:
                    # Find the best match
                    matched_idxs = [i for (i, b) in enumerate(matches) if b]
                    counts = {}
                    for i in matched_idxs:
                        match_name = data["names"][i]
                        counts[match_name] = counts.get(match_name, 0) + 1
                    name = max(counts, key=counts.get)
                
                # If the person is known and hasn't been marked present yet today
                if name != "Unknown" and name not in present_today:
                    timestamp = datetime.now()
                    
                    # Get student ID from name
                    cursor.execute("SELECT id FROM students WHERE name = ?", (name,))
                    student_id_result = cursor.fetchone()
                    
                    if student_id_result:
                        student_id = student_id_result[0]
                        
                        # Check if the person was already marked today (optional check, though the set should handle it)
                        today_date = timestamp.strftime("%Y-%m-%d")
                        cursor.execute("SELECT 1 FROM attendance WHERE student_id = ? AND date(timestamp) = ?", 
                                       (student_id, today_date))
                        if cursor.fetchone() is None:
                            # Mark attendance in the database
                            cursor.execute("INSERT INTO attendance (student_id, timestamp, status) VALUES (?, ?, ?)",
                                        (student_id, timestamp.strftime("%Y-%m-%d %H:%M:%S"), "Present"))
                            conn.commit()
                            print(f"✅ Attendance marked for {name} at {timestamp.strftime('%H:%M:%S')}")
                            present_today.add(name) # Add to the set for today

                names.append(name)

            # 3. Scale the box locations back up to the original frame size
            # This ensures the drawing is correct on the full-size 'frame'
            boxes = []
            scale_factor_inv = int(1/SCALE_FACTOR) # e.g., 4 if SCALE_FACTOR is 0.25
            for (top, right, bottom, left) in current_boxes:
                top *= scale_factor_inv
                right *= scale_factor_inv
                bottom *= scale_factor_inv
                left *= scale_factor_inv
                boxes.append((top, right, bottom, left)) 

        # --- Drawing Loop (Always runs for smooth display) ---
        # Draw rectangles and names using the results from the last processed frame
        for ((top, right, bottom, left), name) in zip(boxes, names):
            color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
            # Draw rectangle
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            # Draw name background
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
            # Draw name text
            y = bottom - 10
            cv2.putText(frame, name, (left + 6, y), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)

        # Display the frame
        cv2.imshow("Attendance System", frame)
        
        # Check for 'q' press to quit
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break

    # --- Save to CSV at the end of the session ---
    print("\nSession ended. Generating final report...")
    today_str = datetime.now().strftime('%Y-%m-%d')
    try:
        df = pd.read_sql_query(f"""
            SELECT s.name, s.enrollment_number, a.timestamp, a.status
            FROM attendance a
            JOIN students s ON s.id = a.student_id
            WHERE date(a.timestamp) = '{today_str}'
            ORDER BY a.timestamp
        """, conn)
        
        if not df.empty:
            csv_filename = f"Attendance_Report_{today_str}.csv"
            df.to_csv(csv_filename, index=False)
            print(f"✅ Attendance report saved to {csv_filename} (Rows: {len(df)})")
        else:
             print("ℹ️ No attendance records were marked in this session for today.")

    except pd.io.sql.DatabaseError as e:
        print(f"🔴 ERROR: Could not query the database. Ensure 'students' and 'attendance' tables exist. Details: {e}")
        
    # Cleanup
    cv2.destroyAllWindows()
    vs.release()
    conn.close()
    print("Cleanup complete. Exiting.")

if __name__ == "__main__":
    mark_attendance()