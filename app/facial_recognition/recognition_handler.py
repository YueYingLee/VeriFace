# app/facial_recognition/utils.py
import cv2
import face_recognition as fr
import numpy as np
import time

RECOGNITION_THRESHOLD = 0.5     # if the difference in comparision is under this threshold --> face is a match
CONFIRM_FACE = 10               # must verify face for this many frames prevent a false match
FRAME_INTERVAL = 2              # run encoding algorithm in intervals to prevent camera lag
IMAGE_SCALE_FACTOR = 0.33       # scale image down by this factor to improve encoding performance
TIMEOUT_SECONDS = 10            # timeout in seconds to prevent infinite scanning

def start_facial_recognition(cap, target_rfid, users):
    frame_count = 0
    confirm_face = 0
    name = None
    target_user = [user for user in users if user.rfid == target_rfid]
    timeout = time.time() + TIMEOUT_SECONDS
    print("Starting facial recognition...")

    while time.time() < timeout:
        ret, frame = cap.read()
        if not ret:
            break

        # Scale down frame for faster processing
        small_frame = cv2.resize(frame, (0, 0), fx=IMAGE_SCALE_FACTOR, fy=IMAGE_SCALE_FACTOR)
        
        # Process every few frames
        if frame_count % FRAME_INTERVAL == 0:
            face_location = fr.face_locations(small_frame)
            if len(face_location) > 1:
                print('Please have only 1 face in frame at a time.')
                continue
            
            if confirm_face == CONFIRM_FACE:
                print('face confirmed')
                break

            face_encoded = fr.face_encodings(small_frame, face_location)
            for encoded, location in zip(face_encoded, face_location):
                matches = fr.compare_faces([np.frombuffer(target_user[0].data, dtype=np.float64)], encoded, RECOGNITION_THRESHOLD)
                face_distances = fr.face_distance([np.frombuffer(target_user[0].data, dtype=np.float64)], encoded)
                
                name = 'Unknown'
                if matches[0]:
                    name = f'{target_user[0].fname} {target_user[0].lname}'
                    confirm_face += 1
                else:
                    confirm_face = 0
                    name = 'Unknown'

                multiply_factor = int(1/IMAGE_SCALE_FACTOR)
                top, right, bottom, left = location
                top *= multiply_factor
                right *= multiply_factor
                bottom *= multiply_factor
                left *= multiply_factor
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 3)
                cv2.putText(frame, name, (left, bottom + 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (190, 200, 50), 2)
        
        frame_count += 1

    if (confirm_face >= CONFIRM_FACE):
        return target_user[0]
    else:
        return None
