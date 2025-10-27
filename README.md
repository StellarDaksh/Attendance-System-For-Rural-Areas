# 🧑‍💻 Face Recognition Attendance System

This project is a sophisticated attendance management system that uses **real-time face recognition** to automatically detect registered individuals and record their attendance in a database. It's built entirely in **Python** and is suitable for use in classrooms, offices, or small organizations.

## ✨ Features

* **Student Registration (`register_student.py`):** Captures images of new individuals using a webcam and stores their name, ID, and face encodings.
* **Model Training (`train_model.py`):** Processes the captured images to generate optimized face encodings, which are saved for fast, accurate recognition.
* **Automatic Attendance Marking (`mark_attendance.py`):** Uses the trained model and a webcam to recognize faces in real-time and automatically logs the entry time into an SQLite database.
* **Database Management (`database_setup.py`):** Initializes and manages the SQLite database (`attendance.db`) to store student information and attendance records.
* **Data Reporting:** Generates a CSV report (`Attendance_Report_*.csv`) of the recorded attendance data.

---

## ⚙️ Technologies Used

This system relies on powerful Python libraries for computer vision and data management:

* **Python 3.x:** The core programming language.
* **OpenCV (`cv2`):** For webcam access, image manipulation, and real-time video processing.
* **`face_recognition`:** A high-level library built on dlib's state-of-the-art face recognition models for accurate face detection and encoding.
* **`sqlite3`:** The lightweight, file-based database used for persistent storage of student data and attendance logs.
* **`pandas` (Likely used):** For reading, processing, and generating the attendance reports in CSV format.

---

## 🚀 Getting Started

Follow these instructions to set up and run the attendance system on your local machine.

### Prerequisites

1.  **Python 3.x** installed.
2.  A functioning **webcam** connected to your system.

### Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/YOUR_USERNAME/face-recognition-attendance-system.git](https://github.com/YOUR_USERNAME/face-recognition-attendance-system.git)
    cd face-recognition-attendance-system
    ```

2.  **Install the required Python packages:**
    *Note: Installing `dlib` (a dependency of `face_recognition`) can sometimes be tricky. You might need to install CMake and Visual Studio C++ build tools (on Windows) before installing `dlib` or `face_recognition`.*

    ```bash
    # You will need to create a requirements.txt file with all dependencies
    pip install -r requirements.txt
    ```

### Recommended `requirements.txt`





opencv-pythonface-recognitionnumpypandas
---

## 🛠️ Usage Guide

You must run the setup, registration, and training steps *before* marking attendance.

### 1. Database Setup

Initialize the SQLite database (`attendance.db`) and create the necessary tables.

```bash
python database_setup.py



2. Register Students
Run this script to register new students. It will open your webcam to capture their face data. Follow the on-screen prompts to enter the student's name and ID.

Bash

python register_student.py
The captured images and their encodings will be stored in designated folders/files (e.g., encodings.pickle).

3. Train the Model
After registering one or more students, you must run the training script to optimize the face encodings for recognition.

Bash

python train_model.py
This script processes the images and saves the final encodings to a file (like encodings.pickle) which mark_attendance.py will use.

4. Mark Attendance
Run the main attendance script. It will open a live webcam feed, recognize registered faces, and log the attendance time in the attendance.db file.

Bash

python mark_attendance.py
To stop the script, press the 'q' key.

📂 Project Structure
File/Folder	Description
database_setup.py	Sets up the SQLite database structure.
register_student.py	Handles new user registration via webcam.
train_model.py	Script to train the face recognition model.
mark_attendance.py	The main script for live attendance marking.
attendance.db	The SQLite database file (created after setup).
encodings.pickle	Stores the final trained face encodings.
Attendance_Report_*.csv	Generated attendance report files.
(Image Directory)	Likely a folder containing captured face images.

🤝 Contributing
This project was initially created to learn concepts related to computer vision and database management. Feel free to fork the repository, suggest improvements, or fix bugs!

1.Fork the Project

2.Create your Feature Branch (git checkout -b feature/AmazingFeature)

3.Commit your Changes (git commit -m 'Add some AmazingFeature')

4.Push to the Branch (git push origin feature/AmazingFeature)

5.Open a Pull Request

🤝 Contributing
This project was initially created to learn concepts related to computer vision and database management. Feel free to fork the repository, suggest improvements, or fix bugs!

Fork the Project

Create your Feature Branch (git checkout -b feature/AmazingFeature)

Commit your Changes (git commit -m 'Add some AmazingFeature')

Push to the Branch (git push origin feature/AmazingFeature)

Open a Pull Request
📜 License
Distributed under the MIT License. See the LICENSE file for more information.

👤 Contact
Project Link: https://github.com/StellarDaksh/Attendance-System-For-Rural-Areas
