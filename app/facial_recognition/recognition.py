# facial recognition implemented with dlib's face-recognition library

import cv2
import face_recognition as fr
import numpy as np

RECOGNITION_THRESHOLD = 0.5
CONFIRM_FACE = 10
FRAME_INTERVAL = 2
IMAGE_SCALE_FACTOR = 0.33


def start_attendance():
    # track frame count
    frame_count = 0

    # identity will be confirmed when this value is incremented to a certain amount
    confirm_face = 0

    # This is temp. There will be something similar to this to target whatever RFID tag was scanned.
    target = 'kenneth_nguyen'

    cap = cv2.VideoCapture(0)
    print("Camera initialized. Waiting for RFID scan...")

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Mirrored camera
        frame = cv2.flip(frame, 1)

        # Wait for the RFID scan event (simulate with key press here)
        if cv2.waitKey(1) & 0xFF == ord('r'):  # replace with RFID scan trigger in actual implementation
            print("RFID scanned! Starting facial recognition.")

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
                    
                    matches = fr.compare_faces(list(encoding.values()), encoded, RECOGNITION_THRESHOLD)
                    face_distances = fr.face_distance(list(encoding.values()), encoded)

                    print(face_distances)

                    # Try to identify the face
                    name = 'Unknown'
                    best_match_idx = np.argmin(face_distances)
                    if matches[best_match_idx]:
                        name = list(encoding.keys())[best_match_idx]
                        if name == target:
                            confirm_face += 1
                        else:
                            confirm_face = 0
                    else:
                        name = 'Unknown'
                        confirm_face = 0

                    # Draw rectangle around the face and label with the name of the identified person
                    multiply_factor = int(1/scale_factor)
                    top, right, bottom, left = location
                    top *= multiply_factor
                    right *= multiply_factor
                    bottom *= multiply_factor
                    left *= multiply_factor
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 3)
                    cv2.putText(frame, name, (left, bottom + 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (190, 200, 50), 2)

            print('face found')
            print('Return to idling camera...')
            confirm_face = 0


        cv2.imshow('Camera Feed', frame)

        # Press 'q' to exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Exiting camera.")
            break


    cap.release()
    cv2.destroyAllWindows()

def main():
    # run this file script for testing
    start_attendance()


if __name__ == "__main__":
    main()
