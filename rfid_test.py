import serial
from app.facial_recognition import global_vars

def main():
    try:
        RFID_PORT = global_vars.rfid_port
        BAUD_RATE = 9600
        print(f"Connecting to RFID reader on {RFID_PORT} at {BAUD_RATE} baud...")
        with serial.Serial(RFID_PORT, BAUD_RATE, timeout=10) as ser:  # 10-second timeout
            print("Connection successful!")
            print("Waiting for RFID scan...")

            while True:
                # Read RFID tag data from the serial port
                rfid_data = ser.readline().decode('utf-8').strip()

                if rfid_data:
                    print(f"RFID Tag Scanned: {rfid_data}")
                    print("Press Ctrl+C to exit.")
                else:
                    print("No RFID tag detected. Retrying...")

    except serial.SerialException as e:
        print(f"Error: Could not connect to the RFID reader. {e}")
    except KeyboardInterrupt:
        print("\nExiting RFID reader test. Goodbye!")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()