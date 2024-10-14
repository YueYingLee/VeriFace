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
    
    # Set up video camera capture
    cap = cv2.VideoCapture(0)
    print('Setting up camera. Press "Q" to quit.')

    while True:
        ret, frame = cap.read()

        if not ret:
            break
        else:
            
            # Only process faces every 5 frames to improve camera performance
            if frame_count % 5 == 0:
                face_location = fr.face_locations(frame)
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
                else:
                    name = 'Unknown'

                # Draw rectangle around the face and label with the name of the identified person
                top, right, bottom, left = location
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 3)
                cv2.putText(frame, name, (left, bottom + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)

            cv2.imshow('Frame', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
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
    print(f"Execution time: {elapsed_time:.4f} seconds")

    start_video(encoded_images)


if __name__ == "__main__":
    main()