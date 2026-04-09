import cv2
import time
from core.detector import TumbleDetector

def main():
    detector = TumbleDetector()
    
    # Open webcam
    cap = cv2.VideoCapture(0)
    
    # Set camera properties for better performance
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    if not cap.isOpened():
        print("Error: Could not open webcam")
        return
    
    # FPS tracking
    fps_start_time = time.time()
    fps_frame_count = 0
    current_fps = 0
    
    print("Tumble Detection System Started")
    print("Press ESC to exit")
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Failed to read frame")
                break

            # Process frame
            processed_frame, status, fall_detected = detector.process_frame(frame)
            
            # Calculate FPS
            fps_frame_count += 1
            if fps_frame_count % 30 == 0:
                fps_end_time = time.time()
                current_fps = 30.0 / (fps_end_time - fps_start_time)
                fps_start_time = fps_end_time
            
            # Display FPS
            cv2.putText(
                processed_frame,
                f"FPS: {current_fps:.1f}",
                (processed_frame.shape[1] - 150, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )
            
            # Show frame
            cv2.imshow("Real-time Tumble Detection", processed_frame)

            # Exit on ESC key
            if cv2.waitKey(1) & 0xFF == 27:
                break
                
    except KeyboardInterrupt:
        print("\nStopping detection system...")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("System stopped")

if __name__ == "__main__":
    main()
