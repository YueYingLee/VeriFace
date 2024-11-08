# Utilities module to hold helper functions for recognition.py

import cv2
import face_recognition as fr
import os
import json
from datetime import datetime
import csv
import numpy as np
from event_controller import end_event

facial_path = os.path.dirname(os.path.abspath(__file__))                            # Path to facial_recognition/
app_path = os.path.dirname(facial_path)                                             # Path to app/ 
attendance_path = os.path.join(app_path, 'attendance')                              # Path to attendance/

supported_extensions = ('.jpg', '.jpeg', '.png')

def encode_image(file):

    # if invalid extension type
    if not file.filename.endswith(supported_extensions):
        raise ValueError(f'Invalid file type! Supported types are {supported_extensions}')
    
    # process file and encode it
    np_data = np.frombuffer(file.read(), np.uint8)
    image = cv2.imdecode(np_data, cv2.IMREAD_COLOR)
    colored_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # gives a list of encodings of all faces found in image
    face_encodings = fr.face_encodings(colored_image)

    # if no faces found
    if not face_encodings:
        raise ValueError('No faces found in this image! Please upload a clear portrait of your face.')

    # if more than one face found
    if len(face_encodings) > 1:
        raise ValueError('Multiple faces detected in this image! Please upload a clear portrait containing only one face.')

    return face_encodings[0]


def initialize_camera():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return None
    return cap

def display_camera(cap):
    while not end_event.is_set():
        ret, frame = cap.read()
        if not ret:
            break
            
        # Mirrored camera
        frame = cv2.flip(frame, 1)
        cv2.imshow('Camera Feed', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    

def mark_attendance(user):
    current_datetime = datetime.now().strftime("%B %d, %Y %I:%M:%S %p")
    current_date = datetime.now().strftime("%m-%d-%Y")
    filename = os.path.join(attendance_path, current_date) + '.csv'

    with open(filename, 'a') as f:
        fieldnames = ['Name', 'Datetime']
        row = {
            'Name': f'{user.fname} {user.lname}',
            'Datetime': current_datetime
        }

        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if os.stat(filename).st_size == 0:
            writer.writeheader()
        writer.writerow(row)

        print(f'Marked attendance for {row["Name"]}')
