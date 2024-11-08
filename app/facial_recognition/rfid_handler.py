import serial
import serial.tools.list_ports
import time
from attendance_controller import rfid_event, end_event
from recognition_handler import start_facial_recognition
from recognition_utils import mark_attendance

def poll_rfid(cap, users):
    try:
        ser = serial.Serial('/dev/tty.usbserial-1410', 9600, timeout=1)
        time.sleep(2)  # Allow time for the connection to establish
        print(f"Connected to /dev/tty.usbserial-1410")

        while not end_event.is_set():
            rfid_event.wait()  # Only proceed if rfid_event is set

            if ser.in_waiting > 0:
                rfid_data = ser.readline().decode('utf-8').strip()
                print(f"RFID Tag: {rfid_data}")

                # check if this RFID is valid for the event
                if is_valid_for_event(rfid_data, users):
                    print('Valid RFID for event')
                    rfid_event.clear()
                    success = start_facial_recognition(cap, rfid_data, users)

                    if success:
                        print('Verified user! Marking attendance...')
                        mark_attendance(success)
                    else:
                        print('Face not recognized or timed out. Please rescan RFID and try again.')

                else:
                    print('RFID is not associated with this event.')

    except serial.SerialException as e:
        print(f"Serial Error: {e}")
    except PermissionError as e:
        print(f"Permission Error: {e}")
    except Exception as e:
        print(f"Unexpected Error: {e}")
    finally:
        ser.close()
        print("Serial port closed.")


def is_valid_for_event(rfid_data, users):
    rfid_list = [user.rfid for user in users]
    return rfid_data in rfid_list
