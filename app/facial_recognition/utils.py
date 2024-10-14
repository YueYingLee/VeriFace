# Utilities module to hold helper functions for recognition.py

import cv2
import face_recognition as fr
import os
import pickle

current_dir = os.path.dirname(os.path.abspath(__file__))                            # directory of current file
assets_path = os.path.join(current_dir, 'assets')                                   # Path to assets/ 
encoded_file_path = os.path.join(assets_path, 'encoded.pkl')                        # Path to the cached encodings


'''
Function to gather images and names from a given path to the directory containing facial images

@params:
    - path: the path to the directory containg facial images
@returns:
    - images: a list of identified facial images 
    - names: a list of the names of the files in the directory
'''
def get_images_and_names(path):
    supported_extensions = ('.jpg', '.jpeg', '.png')
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

    # Check for cached encodings
    if os.path.exists(encoded_file_path):
        print('Found cached encodings.')
        print('Loading existing encodings...')

        with open(encoded_file_path, 'rb') as f:
            encode_map = pickle.load(f)

        if not encode_map:
            raise ValueError('ERROR: Cached encodings are empty.')
        return encode_map
    
    # if no cache exists, create new encodings
    print('Cached encodings not found.')
    print('Creating encodings for all images... This may take a moment...')

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
