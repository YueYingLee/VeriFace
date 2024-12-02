import serial
import time

def poll_rfid_once(timeout=10):
    """
    Poll the RFID reader for a single scan within the given timeout period.
    :param timeout: The time in seconds to wait for an RFID tag.
    :return: The scanned RFID tag, or None if no tag was scanned within the timeout.
    """
    try:
        RFID_PORT = '/dev/ttyUSB0'
        BAUD_RATE = 9600
        print(f"Connecting to RFID reader on {RFID_PORT} at {BAUD_RATE} baud...")

        # Replace 'COM5' with your Arduino's serial port
        ser = serial.Serial(RFID_PORT, BAUD_RATE, timeout=1)  # 1-second serial timeout
        print("Waiting for RFID scan...")
        
        start_time = time.time()
        while True:
            if time.time() - start_time > timeout:
                print("RFID scan timed out.")
                ser.close()
                return None  # Return None if timeout occurs

            # Read a line from the RFID reader
            rfid_tag = ser.readline().decode('utf-8').strip()

            if rfid_tag:
                print(f"RFID Tag Scanned: {rfid_tag}\n")
                ser.close()
                return rfid_tag  # Return the scanned RFID tag if found

    except serial.SerialException as e:
        print(f"Serial error: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None
