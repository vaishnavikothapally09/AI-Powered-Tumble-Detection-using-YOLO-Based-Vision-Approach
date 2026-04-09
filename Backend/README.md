# Tumble Detection Backend

Real-time tumble detection system with email alerts using YOLOv8 pose estimation.

## Features

- **Real-time Detection**: Detects tumbles in real-time using webcam feed
- **Multiple Detection Modes**:
  - Forward/backward tumbles
  - Sideways tumbles
  - Person disappearance (bending head down)
  - Sitting position tumbles
  - Rapid movement detection
- **Email Alerts**: Sends email with captured image when tumble is detected
- **REST API**: Flask-based API for frontend integration
- **Video Streaming**: Live video feed via HTTP streaming

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Email (SMTP)

Copy `.env.example` to `.env` and configure your SMTP settings:

```bash
# For Gmail
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=your-email@gmail.com
```

**Note for Gmail users:**
1. Enable 2-factor authentication on your Google account
2. Generate an App Password: https://myaccount.google.com/apppasswords
3. Use the App Password (not your regular password) as `SMTP_PASSWORD`

### 3. Run the Server

```bash
python app.py
```

The server will start on `http://localhost:5000`

## API Endpoints

### Start Detection
```http
POST /api/start
Content-Type: application/json

{
  "email": "recipient@example.com"
}
```

### Stop Detection
```http
POST /api/stop
```

### Get Status
```http
GET /api/status
```

### Video Feed
```http
GET /api/video_feed
```
Returns: Multipart MJPEG stream

### Test Email
```http
POST /api/test_email
Content-Type: application/json

{
  "email": "recipient@example.com"
}
```

### Health Check
```http
GET /api/health
```

## Local Testing

For local testing without frontend:

```bash
python run_local.py
```

This opens a window showing the detection in real-time.

## Environment Variables

- `SMTP_SERVER`: SMTP server address (default: smtp.gmail.com)
- `SMTP_PORT`: SMTP server port (default: 587)
- `SMTP_USERNAME`: SMTP username/email
- `SMTP_PASSWORD`: SMTP password/app password
- `FROM_EMAIL`: Email address to send from

## Configuration

Detection parameters can be adjusted in `core/config.py`:

- `PERSON_DISAPPEAR_TIME`: Time before considering person disappeared (seconds)
- `SITTING_TUMBLE_THRESHOLD`: Time to confirm tumble while sitting (seconds)
- `SIDEWAYS_ANGLE_THRESHOLD`: Body angle threshold for sideways tumble (degrees)
- `FALL_COOLDOWN_TIME`: Cooldown between email alerts (seconds)

