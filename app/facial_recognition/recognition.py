# facial recognition implemented with dlib's face-recognition library

import cv2
import face_recognition as fr
import numpy as np
import time

import utils


'''
Start video capture and facial recognition

@params:
    - encoded_images: list of encoded images
'''
def start_video(encoded_images):
    # track frame count
    frame_count = 0

    # identity will be confirmed when this value is incremented to a certain amount
    confirm_face = 0

    # This is temp. There will be something similar to this to target whatever RFID tag was scanned.
    target = 'charlotte_ying'
    
    # Set up video camera capture
    cap = cv2.VideoCapture(0)
    print('Setting up camera. Press "Q" to quit.\n')

    while True:
        ret, frame = cap.read()

        if not ret:
            break
        else:

            # Mirrored camera
            frame = cv2.flip(frame, 1)
            
            # Only process faces every few frames to improve camera performance
            if frame_count % 10 == 0:
                face_location = fr.face_locations(frame)
                if len(face_location) > 1:
                    print('Please have only 1 face in frame at a time.')
                else:
                    face_encoded = fr.face_encodings(frame, face_location)
            frame_count += 1

            for encoded, location in zip(face_encoded, face_location):
                
                matches = fr.compare_faces(list(encoded_images.values()), encoded, 0.5)
                face_distances = fr.face_distance(list(encoded_images.values()), encoded)

                print(face_distances)

                # Try to identify the face
                name = 'Unknown'
                best_match_idx = np.argmin(face_distances)
                if matches[best_match_idx]:
                    name = list(encoded_images.keys())[best_match_idx]
                    if name == target:
                        confirm_face += 1
                    else:
                        confirm_face = 0
                else:
                    name = 'Unknown'
                    confirm_face = 0

                # Draw rectangle around the face and label with the name of the identified person
                top, right, bottom, left = location
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 3)
                cv2.putText(frame, name, (left, bottom + 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (190, 200, 50), 2)

            cv2.imshow('Frame', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print('Exit Success')
                break
            elif confirm_face == 11:
                print(f'Identified {name}')
                utils.mark_attendance(name)
                break

    cap.release()
    cv2.destroyAllWindows()

def main():
    start = time.time()

    try:
        images, names = utils.get_images_and_names(utils.assets_path)
    except ValueError as e:
        print(e)
        exit()

    try:
        encoded_images = utils.get_encoded_images(images, names)
    except ValueError as e:
        print(e)
        exit()

    end = time.time()

    elapsed_time = end - start
    print(f"Execution time: {elapsed_time:.4f} seconds\n")

    start_video(encoded_images)


if __name__ == "__main__":
    main()
