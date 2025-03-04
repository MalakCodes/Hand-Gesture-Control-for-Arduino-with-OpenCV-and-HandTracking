import cv2
from cvzone.HandTrackingModule import HandDetector
import serial
import time

# Initialize serial communication with Arduino (adjust 'COM3' to your port)
ser = serial.Serial('COM3', 9600)
time.sleep(2)  # Wait for the serial connection to stabilize

# Initialize hand detector
detector = HandDetector(detectionCon=0.8, maxHands=1)

# Start video capture
video = cv2.VideoCapture(0)

# Variable to keep track of the previous finger status
previous_finger_status = None

while True:
    ret, frame = video.read()
    frame = cv2.flip(frame, 1)

    # Detect hands in the frame
    hands, img = detector.findHands(frame)

    if hands:
        lmList = hands[0]  # Landmark list of the first hand
        fingerUp = detector.fingersUp(lmList)  # Get the status of each finger

        # Convert finger status list to string
        finger_status_str = ''.join(map(str, fingerUp))  # Convert [0,1,1,0,0] to '01100'

        # Only send the finger status if it has changed from the previous one
        if finger_status_str != previous_finger_status:
            # Send the status of all fingers to Arduino as a string
            data_to_send = f"@{finger_status_str}\n"  # Format: @finger_status
            ser.write(data_to_send.encode())  # Send data over serial
            
            print(f"Sent to Arduino: {data_to_send.strip()}")  # For debugging
            
            # Update the previous_finger_status to the current one
            previous_finger_status = finger_status_str
        
        # Display the finger status on the frame
        cv2.putText(frame, f'Finger status: {finger_status_str}', (20, 460), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1, cv2.LINE_AA)

    # Display the video feed
    cv2.imshow("Hand Detection", frame)

    # Exit on pressing the 'k' key
    k = cv2.waitKey(1)
    if k == ord("q"):
        break

# Release resources
video.release()
cv2.destroyAllWindows()
ser.close()  # Close the serial connection
