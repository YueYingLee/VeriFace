# facial recognition implemented with dlib's face-recognition library

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
    # track frame count
    frame_count = 0

    # identity will be confirmed when this value is incremented to a certain amount
    confirm_face = 0
    name = None

    target_user = [user for user in users if user.rfid == target_rfid]

    timeout = time.time() + TIMEOUT_SECONDS
    print("Starting facial recognition...")

    while time.time() < timeout:
        ret, frame = cap.read()
        if not ret:
            break
        
        while confirm_face < CONFIRM_FACE:

            # Scale down frame to process encodings faster
            scale_factor = IMAGE_SCALE_FACTOR
            small_frame = cv2.resize(frame, (0, 0), fx=scale_factor, fy=scale_factor)

            # Only process faces every few frames to improve camera performance
            if frame_count % FRAME_INTERVAL == 0:
                face_location = fr.face_locations(small_frame)
                if len(face_location) > 1:
                    print('Please have only 1 face in frame at a time.')
                else:
                    face_encoded = fr.face_encodings(small_frame, face_location)
            frame_count += 1

            for encoded, location in zip(face_encoded, face_location):
                
                matches = fr.compare_faces([np.frombuffer(target_user[0].data)], encoded, RECOGNITION_THRESHOLD)
                face_distances = fr.face_distance([np.frombuffer(target_user[0].data)], encoded)

                print(face_distances)

                # Try to identify the face
                name = 'Unknown'
                best_match_idx = np.argmin(face_distances)
                if matches[best_match_idx]:
                    name = f'{target_user.fname} {target_user.lname}'
                    confirm_face += 1
                else:
                    confirm_face = 0
                    name = 'Unknown'

                # Draw rectangle around the face and label with the name of the identified person
                multiply_factor = int(1/scale_factor)
                top, right, bottom, left = location
                top *= multiply_factor
                right *= multiply_factor
                bottom *= multiply_factor
                left *= multiply_factor
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 3)
                cv2.putText(frame, name, (left, bottom + 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (190, 200, 50), 2)

        if confirm_face >= 10:
            print('face found')
            print('Return to idling camera...')
            return name

        cv2.imshow('Camera Feed', frame)
    
    return None


def main():
    pass


if __name__ == "__main__":
    main()
