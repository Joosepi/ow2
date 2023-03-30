import cv2
import mediapipe as mp
import numpy as np
import time
import ctypes
import tkinter as tk

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

# Create the GUI window
root = tk.Tk()
root.title("Pose Detection GUI")

# Create the video capture object
cap = cv2.VideoCapture(0)

# Create the canvas for the video stream
canvas = tk.Canvas(root, width=640, height=480)
canvas.pack()

# Create the button to toggle prediction
def toggle_prediction():
    global prediction_on
    prediction_on = not prediction_on

toggle_button = tk.Button(root, text="Toggle Prediction", command=toggle_prediction)
toggle_button.pack()

# Create the scale for the field of view
def fov_changed(value):
    global FOV
    FOV = int(value)

fov_scale = tk.Scale(root, from_=10, to=180, length=300, orient=tk.HORIZONTAL, label="Field of View", command=fov_changed)
fov_scale.pack()

# Create the main loop for the GUI
def update():
    global prediction_on
    global FOV

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
    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
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
        if frame.shape[1] / 2 - FOV / 2 <= robot_center[0] <= frame.shape[1] :
if frame.shape[1] / 2 - FOV / 2 <= robot_center[0] <= frame.shape[1] / 2 + FOV / 2:
    # Draw a circle on the robot center
    cv2.circle(frame, robot_center, 10, (0, 255, 0), -1)

    # Get the normalized coordinates of the robot center
    normalized_x = robot_center[0] / frame.shape[1]
    normalized_y = robot_center[1] / frame.shape[0]

    # Call the function that aims the robot at the point
    aim_at_point(normalized_x, normalized_y)

    # Print a message
    cv2.putText(frame, "Robot in Field of View", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

# Convert the RGB image back to BGR for display
image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

# Display the image on the canvas
canvas.image = tk.PhotoImage(data=cv2.imencode('.png', image)[1].tobytes())
canvas.create_image(0, 0, anchor=tk.NW, image=canvas.image)

# Call this function again after a delay
root.after(10, update)

# Start the GUI loop
root.after(0, update)
root.mainloop()

