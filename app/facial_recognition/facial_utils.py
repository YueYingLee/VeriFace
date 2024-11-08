# Utilities module to hold helper functions for recognition.py

import cv2
import face_recognition as fr
import os
import json
from datetime import datetime
import csv
import numpy as np

# Useful global variables

facial_path = os.path.dirname(os.path.abspath(__file__))                            # Path to facial_recognition/
# assets_path = os.path.join(facial_path, 'assets')                                   # Path to assets/
# encoded_file_path = os.path.join(assets_path, 'encoded.json')                       # Path to the cached encodings
app_path = os.path.dirname(facial_path)                                             # Path to app/ 
attendance_path = os.path.join(app_path, 'attendance')                              # Path to attendance/

supported_extensions = ('.jpg', '.jpeg', '.png')


# '''
# Function to gather images and names from a given path to the directory containing facial images

# @params:
#     - path: the path to the directory containg facial images
# @returns:
#     - images: a list of identified facial images 
#     - names: a list of the names of the files in the directory
# '''
# def get_images_and_names(path):
#     image_files = [file for file in os.listdir(path) if file.lower().endswith(supported_extensions)]

#     images = []
#     names = []

#     for file in image_files:
#         img = cv2.imread(f'{os.path.join(path, file)}')
#         images.append(img)
        
#         name = file.split('.')[0]
#         names.append(name)

#     if len(images) == 0:
#         raise ValueError(f'ERROR: No valid images found in {assets_path}')

#     return images, names


# '''
# Function to encode images

# @params:
#     - images: a list of images read by cv2
#     - names: a list of names associated with the images
# @returns:
#     - a map of names and their associated encodings, {names: encoding}
# '''
# def get_encoded_images(images, names):

#     '''
#     Let's check for cached encodings to speed up the process because encoding is slow ;(
    
#     The logic is:
#         - if there is no exisiting cached encoding              --> create new encodings
#         - else cache exists but assets/ folder was modified     --> create new encodings
#         - else cache exists and there were no modifications     --> reuse cached encodings
#     '''

#     # If no cache exists
#     if not os.path.exists(encoded_file_path):
#         print('Cached encodings not found. Creating new encodings...')
    
#     # If assets directory was modified i.e modified datetimes do not match between assets/ and encoded.json
#     elif os.path.getmtime(assets_path) - os.path.getmtime(encoded_file_path) > 1:
#         print('Assets directory has been modified. Regenerating encodings...')
    
#     # Reuse cache! :D
#     else:
#         print('Found cached encodings! Loading existing encodings...')

#         with open(encoded_file_path, 'r') as f:
#             encode_map = json.load(f)

#         if not encode_map:
#             raise ValueError('ERROR: Cached encodings are empty.')
#         return encode_map
    
#     print('This may take a moment...\n')
#     encode_map = {}

#     for img, name in zip(images, names):
#         encode = fr.face_encodings(img)
#         if encode:
#             encode_map[name] = list(encode[0])
#         else:
#             print(f'ERROR: No faces found in image for {name}. Skipping...')

#     with open(encoded_file_path, 'w') as f:
#         json.dump(encode_map, f, indent=4)

#     if not encode_map:
#         raise ValueError('ERROR: Encoding failed.')
    
#     print('Encoding finished!')
#     return encode_map


def encode_image(file):
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
    

def mark_attendance(name):
    current_datetime = datetime.now().strftime("%B %d, %Y %I:%M:%S %p")
    current_date = datetime.now().strftime("%m-%d-%Y")
    filename = os.path.join(attendance_path, current_date) + '.csv'

    with open(filename, 'a') as f:
        fieldnames = ['Name', 'Datetime']
        row = {
            'Name': name,
            'Datetime': current_datetime
        }

        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if os.stat(filename).st_size == 0:
            writer.writeheader()
        writer.writerow(row)

        print(f'Marked attendance for {name}')
