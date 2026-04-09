# Tumble Detection System

A real-time tumble detection system using YOLOv8 pose estimation with email alerts and web interface.

## Features

- ✅ Real-time tumble detection from webcam
- ✅ Multiple detection modes:
  - Forward/backward tumbles
  - Sideways tumbles
  - Person disappearance (bending head down, moving out of view)
  - Sitting position tumbles
  - Rapid movement detection
- ✅ Email alerts with captured images via SMTP
- ✅ Web interface (Next.js frontend)
- ✅ REST API for integration
- ✅ Live video streaming

## Project Structure

```
tumbleDetection/
├── Backend/
│   ├── app.py                 # Flask API server
│   ├── run_local.py          # Local testing script
│   ├── core/
│   │   ├── detector.py       # Tumble detection logic
│   │   ├── config.py         # Configuration parameters
│   │   └── email_service.py  # SMTP email service
│   ├── images/               # Captured tumble images
│   └── requirements.txt      # Python dependencies
└── Frontend/
    ├── app/
    ├── components/
    │   └── detection-interface.jsx  # Main UI component
    └── package.json
```

## Quick Start

### Backend Setup

1. Navigate to Backend directory:
```bash
cd Backend
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Configure SMTP email (optional):
   - Copy `.env.example` to `.env`
   - Add your SMTP credentials
   - See Backend/README.md for detailed instructions

4. Run the server:
```bash
python app.py
```

The backend will run on `http://localhost:5000`

### Frontend Setup

1. Navigate to Frontend directory:
```bash
cd Frontend
```

2. Install dependencies:
```bash
npm install
# or
pnpm install
```

3. Create `.env.local` file (optional):
```
NEXT_PUBLIC_API_URL=http://localhost:5000
```

4. Run the development server:
```bash
npm run dev
# or
pnpm dev
```

The frontend will run on `http://localhost:3000`

## Usage

### Web Interface

1. Open the web interface at `http://localhost:3000`
2. Enter the caretaker's email address
3. Click "Start Detection" to begin monitoring
4. The system will send email alerts when tumbles are detected

### Local Testing (Without Frontend)

Run the local testing script:
```bash
cd Backend
python run_local.py
```

This opens a window showing real-time detection with visual feedback.

## Configuration

### Detection Parameters

Edit `Backend/core/config.py` to adjust detection sensitivity:

- `PERSON_DISAPPEAR_TIME`: Time before person disappearance triggers alert (default: 1.0s)
- `SITTING_TUMBLE_THRESHOLD`: Time to confirm tumble while sitting (default: 0.5s)
- `SIDEWAYS_ANGLE_THRESHOLD`: Body angle for sideways tumble (default: 35°)
- `FALL_COOLDOWN_TIME`: Cooldown between email alerts (default: 3s)

### Email Configuration

Configure SMTP settings in `.env` file (see Backend/README.md for details).

## API Documentation

See `Backend/README.md` for complete API documentation.

## Troubleshooting

### Camera Not Working
- Ensure camera permissions are granted
- Try changing camera index in `app.py` (default: 0)
- Check if another application is using the camera

### Email Not Sending
- Verify SMTP credentials in `.env`
- For Gmail, use App Password (not regular password)
- Check firewall/network settings
- Use "Test Email" button in frontend to verify configuration

### Detection Not Working
- Ensure good lighting conditions
- Person should be clearly visible in frame
- Check camera resolution settings
- Review detection parameters in `config.py`

## License

This project is for educational and research purposes.

## Support

For issues or questions, please check the documentation in the respective Backend and Frontend directories.

