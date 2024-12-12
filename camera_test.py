import cv2

# Initialize the webcam (default camera index 0)
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

# Check if the camera is opened successfully
if not cap.isOpened():
    print("Error: Could not access the webcam")
    exit()

print("Press 'q' to exit")

# Loop to capture frames from the webcam
while True:
    ret, frame = cap.read()  # Capture a single frame
    if not ret:
        print("Failed to grab frame")
        break

    # Display the frame in a window
    cv2.imshow("Webcam", frame)

    # Break the loop when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close the window
cap.release()
cv2.destroyAllWindows()
