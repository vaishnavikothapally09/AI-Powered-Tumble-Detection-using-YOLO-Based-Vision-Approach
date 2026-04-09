import os
import cv2
import time
import threading
import base64
from flask import Flask, Response, jsonify, request
from flask_cors import CORS
from core.detector import TumbleDetector
from core.email_service import EmailService

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Global variables
detector = None
camera = None
detection_active = False
email_service = EmailService()  # Initialize email service
recipient_email = None

def generate_frames():
    """Generator function for video streaming"""
    global detector, camera, detection_active, email_service, recipient_email
    
    while detection_active:
        if camera is None:
            break
            
        ret, frame = camera.read()
        if not ret:
            break

        try:
            processed_frame, status, fall_detected = detector.process_frame(frame)
            
            # Send email if tumble detected
            if fall_detected and email_service and recipient_email:
                try:
                    # Save frame temporarily
                    timestamp = int(time.time())
                    temp_path = f"images/temp_fall_{timestamp}.jpg"
                    cv2.imwrite(temp_path, processed_frame)
                    
                    # Send email in background thread
                    email_thread = threading.Thread(
                        target=email_service.send_tumble_alert,
                        args=(recipient_email, temp_path, status)
                    )
                    email_thread.daemon = True
                    email_thread.start()
                except Exception as e:
                    print(f"Error sending email: {e}")
            
            # Encode frame as JPEG
            ret, buffer = cv2.imencode('.jpg', processed_frame)
            if not ret:
                continue
                
            frame_bytes = buffer.tobytes()
            
            # Yield frame in multipart format
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                   
        except Exception as e:
            print(f"Error processing frame: {e}")
            continue

@app.route('/api/start', methods=['POST'])
def start_detection():
    """Start tumble detection"""
    global detector, camera, detection_active, recipient_email
    
    try:
        data = request.get_json()
        recipient_email = data.get('email', '')
        
        if not recipient_email:
            return jsonify({'error': 'Email is required'}), 400
        
        # Initialize detector if not already done
        if detector is None:
            detector = TumbleDetector()
        
        # Initialize camera if not already done
        if camera is None:
            camera = cv2.VideoCapture(0)
            camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            camera.set(cv2.CAP_PROP_FPS, 30)
            
            if not camera.isOpened():
                return jsonify({'error': 'Could not open camera'}), 500
        
        detection_active = True
        
        return jsonify({
            'status': 'success',
            'message': 'Detection started',
            'email': recipient_email
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stop', methods=['POST'])
def stop_detection():
    """Stop tumble detection"""
    global camera, detection_active
    
    try:
        detection_active = False
        
        if camera:
            camera.release()
            camera = None
        
        return jsonify({
            'status': 'success',
            'message': 'Detection stopped'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get detection status"""
    global detection_active
    
    return jsonify({
        'status': 'active' if detection_active else 'inactive',
        'detection_active': detection_active
    })

@app.route('/api/video_feed')
def video_feed():
    """Video streaming route"""
    if not detection_active:
        return jsonify({'error': 'Detection not active'}), 400
    
    return Response(
        generate_frames(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

@app.route('/api/test_email', methods=['POST'])
def test_email():
    """Test email configuration"""
    global email_service
    
    try:
        data = request.get_json()
        test_email = data.get('email', '')
        
        if not test_email:
            return jsonify({'error': 'Email is required'}), 400
        
        # Send test email
        success = email_service.send_test_email(test_email)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': 'Test email sent successfully'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to send test email'
            }), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Tumble Detection API'
    })

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
    except KeyboardInterrupt:
        print("\nShutting down server...")
        detection_active = False
        if camera:
            camera.release()
        cv2.destroyAllWindows()

