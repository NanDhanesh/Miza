import cv2
import numpy as np
import time
from datetime import datetime
import matplotlib.pyplot as plt

def main():
    # Initialize webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam")
        return

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

    eye_positions = []
    max_positions = 30

    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to capture initial frame")
        return

    heatmap = np.zeros((frame.shape[0], frame.shape[1]), dtype=np.float32)

    start_time = time.time()
    focus_time = 0  # seconds with eyes detected

    print("Eye tracking started. Press 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to capture frame")
            break

        display = frame.copy()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        eyes_detected = False

        for (x, y, w, h) in faces:
            roi_gray = gray[y:y+h, x:x+w]
            roi_color = display[y:y+h, x:x+w]
            eyes = eye_cascade.detectMultiScale(roi_gray)

            if len(eyes) > 0:
                eyes_detected = True

            for (ex, ey, ew, eh) in eyes:
                eye_center_x = x + ex + ew//2
                eye_center_y = y + ey + eh//2
                cv2.circle(heatmap, (eye_center_x, eye_center_y), 30, 0.1, -1)
                eye_positions.append((eye_center_x, eye_center_y))
                if len(eye_positions) > max_positions:
                    eye_positions.pop(0)
                cv2.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), (0, 255, 0), 2)
                cv2.circle(display, (eye_center_x, eye_center_y), 2, (0, 0, 255), -1)

        if eyes_detected:
            focus_time += 1 / 30.0  # assuming ~30fps

        for i in range(1, len(eye_positions)):
            intensity = int(255 * (i / len(eye_positions)))
            cv2.line(display, eye_positions[i-1], eye_positions[i], (0, intensity, 255-intensity), 1)

        heatmap_normalized = cv2.normalize(heatmap, None, 0, 255, cv2.NORM_MINMAX)
        heatmap_normalized = np.uint8(heatmap_normalized)
        heatmap_color = cv2.applyColorMap(heatmap_normalized, cv2.COLORMAP_JET)
        heatmap_display = cv2.addWeighted(frame, 0.6, heatmap_color, 0.4, 0)

        elapsed_time = time.time() - start_time
        focus_percentage = (focus_time / elapsed_time) * 100 if elapsed_time > 0 else 0

        cv2.putText(display, f"Focus: {focus_percentage:.1f}%", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        cv2.imshow('Eye Tracking', display)
        cv2.imshow('Attention Heatmap', heatmap_display)
        heatmap *= 0.99

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    # Final Report
    print("\n--- Session Summary ---")
    print(f"Session Duration: {elapsed_time:.2f} seconds")
    print(f"Focus Time (eyes on screen): {focus_time:.2f} seconds")
    print(f"Eye Focus Score: {focus_percentage:.2f}%")

    # 🔥 Sexy breakdown plot
    unfocused_time = elapsed_time - focus_time
    labels = ['Focused', 'Not Focused']
    times = [focus_time, unfocused_time]
    colors = ['#2ecc71', '#e74c3c']

    plt.style.use('dark_background')
    plt.rcParams['font.family'] = 'DejaVu Sans'

    fig, ax = plt.subplots(figsize=(6, 4), facecolor='black')

    # Faint glow
    glow_rect = plt.Rectangle((-0.5, -1), 2, max(times)+3, linewidth=0,
                               edgecolor=None, facecolor='white', alpha=0.03, zorder=0)
    ax.add_patch(glow_rect)

    bars = ax.bar(labels, times, color=colors, edgecolor='white', linewidth=1.2, zorder=2)

    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2.0,
                yval / 2,
                f'{yval:.1f}s',
                ha='center', va='center',
                color='black', fontsize=12, fontweight='bold',
                bbox=dict(facecolor='white', alpha=0.6, boxstyle='round,pad=0.3'))

    ax.set_title('Focus Breakdown', fontsize=14, color='white', pad=15)
    ax.set_ylabel('Time (seconds)', fontsize=12, color='white')
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')
    ax.set_ylim(bottom=0)
    fig.tight_layout()

    plt.show()

if __name__ == "__main__":
    main()
