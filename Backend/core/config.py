# Posture Detection Thresholds
HEAD_HIP_RATIO_LYING = 0.35
HEAD_SHOULDER_MARGIN = 15

# Sideways Tumble Detection
SIDEWAYS_ANGLE_THRESHOLD = 50  # Degrees - body angle for sideways tumble
SIDEWAYS_LEAN_THRESHOLD = 0.4  # Ratio of body width for sideways lean
SUDDEN_ANGLE_CHANGE = 25  # Degrees - sudden angle change threshold

# Person Disappearance Detection (bending head down, disappearing from view)
PERSON_DISAPPEAR_TIME = 1.0  # Seconds - time before considering person disappeared
DISAPPEAR_TUMBLE_THRESHOLD = 0.8  # Seconds - time to confirm tumble after disappearance

# Sitting Position Detection
SITTING_KNEE_HIP_RATIO = 0.7  # Ratio - when knee-hip distance suggests sitting
SITTING_HEIGHT_RATIO = 0.6  # Ratio - body height reduction when sitting
SITTING_TUMBLE_THRESHOLD = 0.5  # Seconds - time to confirm tumble while sitting

# Velocity and Acceleration Thresholds
VELOCITY_THRESHOLD = 0.15  # Normalized velocity for sudden movement
ACCELERATION_THRESHOLD = 0.2  # Normalized acceleration for rapid changes

# Timing Thresholds (in seconds)
FALLING_TIME = 0.3  # Reduced for faster detection
LYING_CONFIRM_TIME = 0.8  # Reduced for faster confirmation
SIDEWAYS_CONFIRM_TIME = 0.5  # Time to confirm sideways tumble
VELOCITY_WINDOW = 0.3  # Window for velocity calculation

# Cooldown
FALL_COOLDOWN_TIME = 3  # Reduced cooldown for real-time detection

# Head Rotation and Collapse Detection
HEAD_ROTATION_THRESHOLD = 45  # Degrees - head rotation angle for collapse detection
HEAD_COLLAPSE_SPEED = 0.12  # Rate of head downward movement
SUDDEN_HEAD_DROP = 50  # Pixels - sudden head position drop

# Body Collapse Detection
BODY_COLLAPSE_RATIO = 0.5  # Ratio - body height reduction indicating collapse
VERTICAL_VELOCITY_THRESHOLD = 0.2  # Downward velocity threshold
BODY_WIDTH_EXPANSION = 1.3  # Ratio - body width expansion when falling

# Sudden Drop Detection
SUDDEN_DROP_THRESHOLD = 80  # Pixels - sudden vertical position change
DROP_VELOCITY_THRESHOLD = 0.25  # High velocity indicating free fall
ACCELERATION_DROP_THRESHOLD = 0.3  # Acceleration threshold for drops

# Forward/Backward Lean Detection
FORWARD_LEAN_ANGLE = 30  # Degrees - forward lean angle
BACKWARD_LEAN_ANGLE = -25  # Degrees - backward lean angle
LEAN_COLLAPSE_TIME = 0.4  # Seconds - time before lean becomes collapse

# Knee Bend and Collapse
KNEE_BEND_ANGLE = 120  # Degrees - extreme knee bend angle
ANKLE_KNEE_HEIGHT_DIFF = 0.4  # Ratio - ankle-knee height difference
FULL_COLLAPSE_HEIGHT = 0.5  # Ratio - body height when fully collapsed

# Multiple Keypoint Loss Detection
CRITICAL_KEYPOINT_LOSS = 4  # Number of keypoints - loss threshold
HEAD_VISIBILITY_LOSS_TIME = 0.6  # Seconds - head keypoint loss time

# Confidence Thresholds
KEYPOINT_CONFIDENCE = 0.3  # Minimum keypoint confidence
MODEL_CONFIDENCE = 0.5  # YOLO detection confidence
