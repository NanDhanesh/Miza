import cv2
import numpy as np
import time
from datetime import datetime

# Tracks eyes using cv2 and OpenCV Haar Cascade Classifier
# Shows a preview and a heatmap, and calculates a rudimentary focus score
# based on the time spent with eyes detected

def main():
    # Initialize webcam
    cap = cv2.VideoCapture(0)
    
    # Check if webcam is opened correctly
    if not cap.isOpened():
        print("Error: Could not open webcam")
        return
    
    # Load pre-trained face and eye detectors
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
    
    # Initialize tracking variables
    eye_positions = []
    max_positions = 30  # Store last 30 positions for tracking history
    
    # Initialize focus tracking variables
    start_time = time.time()
    total_time = 0
    focus_time = 0
    last_eyes_detected_time = None
    focus_threshold = 1.0  # Consider user focused if eyes detected within this many seconds
    
    # Initialize heatmap
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to capture initial frame")
        return
    
    heatmap = np.zeros((frame.shape[0], frame.shape[1]), dtype=np.float32)
    
    print("Eye tracking started. Press 'q' to quit.")
    
    while True:
        # Read frame from webcam
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to capture frame")
            break
        
        # Create copy for display
        display = frame.copy()
        
        # Convert to grayscale for detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        eyes_detected = False
        
        for (x, y, w, h) in faces:
            # Draw face rectangle
            cv2.rectangle(display, (x, y), (x+w, y+h), (255, 0, 0), 2)
            
            # Region of interest for eyes
            roi_gray = gray[y:y+h, x:x+w]
            roi_color = display[y:y+h, x:x+w]
            
            # Detect eyes within the face region
            eyes = eye_cascade.detectMultiScale(roi_gray)
            
            if len(eyes) > 0:
                eyes_detected = True
                
            for (ex, ey, ew, eh) in eyes:
                # Calculate center of eye
                eye_center_x = x + ex + ew//2
                eye_center_y = y + ey + eh//2
                
                # Update heatmap with Gaussian distribution around eye center
                cv2.circle(
                    heatmap, 
                    (eye_center_x, eye_center_y), 
                    30,  # radius of influence 
                    0.1,  # intensity to add
                    -1    # fill the circle
                )
                
                # Store eye position
                eye_positions.append((eye_center_x, eye_center_y))
                
                # Limit the number of positions stored
                if len(eye_positions) > max_positions:
                    eye_positions.pop(0)
                
                # Draw eye rectangle (standard bounding box)
                cv2.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), (0, 255, 0), 2)
                
                # Draw eye center point
                cv2.circle(display, (eye_center_x, eye_center_y), 2, (0, 0, 255), -1)
        
        # Update focus tracking
        current_time = time.time()
        frame_duration = current_time - (total_time + start_time)
        total_time += frame_duration
        
        if eyes_detected:
            if last_eyes_detected_time is None or (current_time - last_eyes_detected_time) < focus_threshold:
                focus_time += frame_duration
            last_eyes_detected_time = current_time
        
        # Draw tracking history (connecting recent eye positions)
        if len(eye_positions) > 1:
            for i in range(1, len(eye_positions)):
                # Draw line between consecutive positions with fading intensity
                intensity = int(255 * (i / len(eye_positions)))
                cv2.line(display, eye_positions[i-1], eye_positions[i], (0, intensity, 255-intensity), 1)
        
        # Prepare heatmap visualization
        # Normalize heatmap
        heatmap_normalized = cv2.normalize(heatmap, None, 0, 255, cv2.NORM_MINMAX)
        heatmap_normalized = np.uint8(heatmap_normalized)
        
        # Apply colormap for visualization
        heatmap_color = cv2.applyColorMap(heatmap_normalized, cv2.COLORMAP_JET)
        
        # Add transparency to blend with original image
        heatmap_display = cv2.addWeighted(frame, 0.6, heatmap_color, 0.4, 0)
        
        # Add text displaying focus metrics
        focus_percentage = (focus_time / total_time) * 100 if total_time > 0 else 0
        cv2.putText(display, f"Focus: {focus_percentage:.1f}%", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Display the resulting frames
        cv2.imshow('Eye Tracking', display)
        cv2.imshow('Attention Heatmap', heatmap_display)
        
        # Slowly decay heatmap
        heatmap = heatmap * 0.99
        
        # Break loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Calculate final focus score
    session_duration = total_time
    focus_score = (focus_time / session_duration) * 100 if session_duration > 0 else 0
    
    print("\n--- Session Summary ---")
    print(f"Session Duration: {session_duration:.2f} seconds")
    print(f"Focus Time: {focus_time:.2f} seconds")
    print(f"Focus Score: {focus_score:.2f}%")
    
    # Release resources
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()