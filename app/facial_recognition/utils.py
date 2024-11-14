# General utilities module to hold helper functions

import cv2
import face_recognition as fr
import os
import json
from datetime import datetime
import csv
import numpy as np
import serial
import serial.tools.list_ports
from threading import Event
from . import recognition_handler
import time

facial_path = os.path.dirname(os.path.abspath(__file__))                            # Path to facial_recognition/
app_path = os.path.dirname(facial_path)                                             # Path to app/ 
attendance_path = os.path.join(app_path, 'attendance')                              # Path to attendance/

supported_extensions = ('.jpg', '.jpeg', '.png')


# Event to control RFID polling and facial recognition
rfid_event = Event()
rfid_event.set()  # Start with RFID scanning enabled

# Event to control when to end attendance
end_event = Event()
end_event.clear()   # start with end_event cleared


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
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        # Mirrored camera
        frame = cv2.flip(frame, 1)
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    

'''
Scan for RFID tag

Parameters:
    - users: a list of all users that are part of the event
    - cap: instance of OpenCV video capture
'''
def poll_rfid(users, cap):
    ser = connect_serial()

    while not end_event.is_set():
        rfid_event.wait()  # Only proceed if rfid_event is set

        if ser.in_waiting > 0:
            rfid_data = ser.readline().decode('utf-8').strip()
            print(f"RFID Tag: {rfid_data}")
            rfid_event.clear()

            # check if this RFID is valid for the event
            if is_valid_for_event(rfid_data, users):
                print('Valid RFID for event')
                verified_user = recognition_handler.start_facial_recognition(cap, rfid_data, users)

                if verified_user:
                    print('Verified user! Marking attendance...')
                    mark_attendance(verified_user)
                else:
                    print('Face not recognized or timed out. Please rescan RFID and try again.')

            else:
                print('RFID is not associated with this event.')
            
            rfid_event.set()
            
        time.sleep(0.1)


'''
Attempt to make serial connection

Returns:
    - ser: serial port connection
'''
def connect_serial():
    try:
        ser = serial.Serial('/dev/tty.usbserial-1410', 9600, timeout=1) # make it dynamically choose the serial port depending on the OS
        time.sleep(2)  # Allow time for the connection to establish
        print(f"Connected to /dev/tty.usbserial-1410")
        return ser

    except serial.SerialException as e:
        print(f"Serial Error: {e}")
    except PermissionError as e:
        print(f"Permission Error: {e}")
    except Exception as e:
        print(f"Unexpected Error: {e}")
    finally:
        ser.close()
        end_event.set()
        print("Serial port closed.")


'''
Verify if the scanned RFID is part of the event

Parameters:
    - rfid_data: the scanned RFID
    - users: a list of all users that are part of the event

Returns:
    - TRUE if user is in event, else FALSE
'''
def is_valid_for_event(rfid_data, users):
    rfid_list = [user.rfid for user in users]
    return rfid_data in rfid_list


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
