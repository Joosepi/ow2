import pyautogui
import numpy as np
import cv2

# Set the target color
target_color = (189, 21, 196)

while True:
    # Capture the screen and convert to HSV color space
    screen = np.array(pyautogui.screenshot())
    hsv = cv2.cvtColor(screen, cv2.COLOR_BGR2HSV)
    
    # Threshold the image to get the mask
    lower = np.array([target_color[0] - 10, 100, 100])
    upper = np.array([target_color[0] + 10, 255, 255])
    mask = cv2.inRange(hsv, lower, upper)
    
    # Find the contours of the mask
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # If we found a contour, move the mouse to its center
    if len(contours) > 0:
        # Get the center of the first contour
        M = cv2.moments(contours[0])
        cx = int(M['m10'] / M['m00'])
        cy = int(M['m01'] / M['m00'])
        
        # Get the screen size
        screen_size = pyautogui.size()
        
        # Calculate the center of the screen
        screen_center_x = screen_size.width // 2
        screen_center_y = screen_size.height // 2
        
        # Calculate the offset from the center
        offset_x = cx - screen_center_x
        offset_y = cy - screen_center_y
        
        # Calculate the mouse movement distance
        move_x = offset_x / screen_center_x * aim_max_move_pixels
        move_y = offset_y / screen_center_y * aim_max_move_pixels
        
        # Move the mouse
        pyautogui.moveRel(move_x, move_y, duration=aim_duration_millis/1000)
