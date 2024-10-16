# Utilities module to hold helper functions for recognition.py

import cv2
import face_recognition as fr
import os
import pickle
from datetime import datetime
import csv

# Useful global variables

facial_path = os.path.dirname(os.path.abspath(__file__))                            # Path to facial_recognition/
assets_path = os.path.join(facial_path, 'assets')                                   # Path to assets/
encoded_file_path = os.path.join(assets_path, 'encoded.pkl')                        # Path to the cached encodings
app_path = os.path.dirname(facial_path)                                             # Path to app/ 
attendance_path = os.path.join(app_path, 'attendance')                              # Path to attendance/

supported_extensions = ('.jpg', '.jpeg', '.png')


'''
Function to gather images and names from a given path to the directory containing facial images

@params:
    - path: the path to the directory containg facial images
@returns:
    - images: a list of identified facial images 
    - names: a list of the names of the files in the directory
'''
def get_images_and_names(path):
    image_files = [file for file in os.listdir(path) if file.lower().endswith(supported_extensions)]

    images = []
    names = []

    for file in image_files:
        img = cv2.imread(f'{os.path.join(path, file)}')
        images.append(img)
        
        name = file.split('.')[0]
        names.append(name)

    if len(images) == 0:
        raise ValueError(f'ERROR: No valid images found in {assets_path}')

    return images, names


'''
Function to encode images

@params:
    - images: a list of images read by cv2
    - names: a list of names associated with the images
@returns:
    - a map of names and their associated encodings, {names: encoding}
'''
def get_encoded_images(images, names):

    '''
    Let's check for cached encodings to speed up the process because encoding is slow ;(
    
    The logic is:
        - if there is no exisiting cached encoding              --> create new encodings
        - else cache exists but assets/ folder was modified     --> create new encodings
        - else cache exists and there were no modifications     --> reuse cached encodings
    '''

    # If no cache exists
    if not os.path.exists(encoded_file_path):
        print('Cached encodings not found. Creating new encodings...')
    
    # If assets directory was modified i.e modified datetimes do not match between assets/ and encoded.pkl
    elif os.path.getmtime(assets_path) - os.path.getmtime(encoded_file_path) > 1:
        print('Assets directory has been modified. Regenerating encodings...')
    
    # Reuse cache! :D
    else:
        print('Found cached encodings! Loading existing encodings...')

        with open(encoded_file_path, 'rb') as f:
            encode_map = pickle.load(f)

        if not encode_map:
            raise ValueError('ERROR: Cached encodings are empty.')
        return encode_map
    
    print('This may take a moment...\n')
    encode_map = {}

    for img, name in zip(images, names):
        encode = fr.face_encodings(img)
        if encode:
            encode_map[name] = encode[0]
        else:
            print(f'ERROR: No faces found in image for {name}. Skipping...')

    with open(encoded_file_path, 'wb') as f:
        pickle.dump(encode_map, f)

    if not encode_map:
        raise ValueError('ERROR: Encoding failed.')
    
    print('Encoding finished!')
    return encode_map


def mark_attendance(name):
    current_datetime = datetime.now().strftime("%B %d, %Y %I:%M:%S %p")
    current_date = datetime.now().strftime("%m-%d-%Y")

    with open(f'{os.path.join(attendance_path, str(current_date))}.csv', 'a') as f:
        pass
