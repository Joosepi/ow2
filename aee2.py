import cv2
import mediapipe as mp
import numpy as np
import time
import ctypes

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose


FOV = 100  # Field of View
prediction_on = False

# Load the DLL file
dll_path = "path/to/dll/file.dll"
my_dll = ctypes.WinDLL(dll_path)

# Define the function that calls the DLL file
def aim_at_point(x, y):
    my_dll.aim_at_point(x, y)

with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
    while cap.isOpened():
        ret, frame = cap.read()

        # Flip the image horizontally for a later selfie-view display
        frame = cv2.flip(frame, 1)

        # Convert the BGR image to RGB.
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Set flag to draw the output image with landmarks and connectors
        if prediction_on:
            draw = True
        else:
            draw = False

        # To improve performance, optionally mark the frame as not writeable to pass by reference.
        image.flags.writeable = False

        # Process the image and find pose landmarks
        results = pose.process(image)

        # Set flag to write the output image to the frame if landmarks are detected
        if results.pose_landmarks and prediction_on:
            image.flags.writeable = True
            mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

            # Get the center point of the robot
            x_max = 0
            x_min = 10000
            y_max = 0
            y_min = 10000

            for landmark in results.pose_landmarks.landmark:
                x, y = int(landmark.x * frame.shape[1]), int(landmark.y * frame.shape[0])
                if x > x_max:
                    x_max = x
                if x < x_min:
                    x_min = x
                if y > y_max:
                    y_max = y
                if y < y_min:
                    y_min = y

            robot_center = (int((x_max + x_min) / 2), int((y_max + y_min) / 2))

        # If the robot is within the field of view, draw a circle on it and print a message
        if robot_center:
            if frame.shape[1] / 2 - FOV / 2 <= robot_center[0] <= frame.shape[1] / 2 + FOV / 2:
                if frame.shape[0] / 2 - FOV / 2 <= robot_center[1] <= frame.shape[0] / 2 + FOV / 2:
                    cv2.circle(frame, robot_center, 10, (0, 255, 0), -1)
                    print("Robot detected within field of view!")

        # Display the resulting image
        cv2.imshow('MediaPipe Pose', frame)

        # Check for key press to turn prediction on/off
        key = cv2.waitKey(1)
        if key == ord('t'):
            prediction_on = not prediction_on

        # Break the loop if q is pressed
        if key == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
