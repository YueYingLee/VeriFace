import serial
import time
from . import global_vars

def read_rfid(timeout=10):
    """
    Reads RFID data within a given timeout window.
    Continuously polls the RFID reader until a valid tag is detected or the timeout expires.
    """
    try:
        RFID_PORT = global_vars.rfid_port  # Replace with your RFID reader's port
        BAUD_RATE = 9600
        print(f"Connecting to RFID reader on {RFID_PORT} at {BAUD_RATE} baud...")

        # Open the serial connection to the RFID reader
        ser = serial.Serial(RFID_PORT, BAUD_RATE, timeout=1)

        # Clear the serial buffer to avoid stale data
        ser.flushInput()
        ser.flushOutput()

        print("Waiting for RFID scan...")
        start_time = time.time()

        while True:
            # Check if the timeout has been reached
            if time.time() - start_time > timeout:
                print("RFID scan timed out.")
                ser.close()
                return None

            # Read data from the RFID reader
            rfid_tag = ser.readline().decode('utf-8').strip()
            print(f"Raw RFID data: {rfid_tag}")  # Log raw data for debugging

            if rfid_tag and len(rfid_tag) == 8:  # Validate the tag length
                print(f"Valid RFID Tag Detected: {rfid_tag}")
                ser.close()
                return rfid_tag

    except serial.SerialException as e:
        print(f"Serial error: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None
