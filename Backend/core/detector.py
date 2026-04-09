import time
import os
import cv2
import numpy as np
from collections import deque
from ultralytics import YOLO
from core.config import (
    HEAD_HIP_RATIO_LYING,
    HEAD_SHOULDER_MARGIN,
    FALLING_TIME,
    LYING_CONFIRM_TIME,
    SIDEWAYS_CONFIRM_TIME,
    FALL_COOLDOWN_TIME,
    SIDEWAYS_ANGLE_THRESHOLD,
    SIDEWAYS_LEAN_THRESHOLD,
    SUDDEN_ANGLE_CHANGE,
    VELOCITY_THRESHOLD,
    ACCELERATION_THRESHOLD,
    VELOCITY_WINDOW,
    KEYPOINT_CONFIDENCE,
    MODEL_CONFIDENCE,
    PERSON_DISAPPEAR_TIME,
    DISAPPEAR_TUMBLE_THRESHOLD,
    SITTING_KNEE_HIP_RATIO,
    SITTING_HEIGHT_RATIO,
    SITTING_TUMBLE_THRESHOLD,
    HEAD_ROTATION_THRESHOLD,
    HEAD_COLLAPSE_SPEED,
    SUDDEN_HEAD_DROP,
    BODY_COLLAPSE_RATIO,
    VERTICAL_VELOCITY_THRESHOLD,
    BODY_WIDTH_EXPANSION,
    SUDDEN_DROP_THRESHOLD,
    DROP_VELOCITY_THRESHOLD,
    ACCELERATION_DROP_THRESHOLD,
    FORWARD_LEAN_ANGLE,
    BACKWARD_LEAN_ANGLE,
    LEAN_COLLAPSE_TIME,
    KNEE_BEND_ANGLE,
    ANKLE_KNEE_HEIGHT_DIFF,
    FULL_COLLAPSE_HEIGHT,
    CRITICAL_KEYPOINT_LOSS,
    HEAD_VISIBILITY_LOSS_TIME
)


class TumbleDetector:
    def __init__(self):
        self.model = YOLO("yolov8n-pose.pt")

        # State machine
        self.state = "STANDING"
        self.state_start_time = time.time()

        # History tracking for velocity and acceleration
        self.position_history = deque(maxlen=10)  # Store recent positions
        self.angle_history = deque(maxlen=10)  # Store recent body angles
        self.timestamp_history = deque(maxlen=10)  # Store timestamps
        
        # Previous values for comparison
        self.prev_center_of_mass = None
        self.prev_body_angle = None
        self.prev_timestamp = None
        
        # Person visibility tracking
        self.person_visible_time = time.time()
        self.person_disappeared_time = None
        self.last_person_detected = True
        
        # Baseline body height for comparison (standing height)
        self.baseline_body_height = None

        self.last_saved_time = 0
        os.makedirs("images", exist_ok=True)

    def calculate_body_angle(self, l_shoulder, r_shoulder, l_hip, r_hip):
        """Calculate the angle of the body (shoulders to hips)"""
        # Check if keypoints are valid (non-zero)
        if np.any(l_shoulder == 0) or np.any(r_shoulder == 0) or \
           np.any(l_hip == 0) or np.any(r_hip == 0):
            return None

        # Calculate shoulder and hip midpoints
        shoulder_mid = ((l_shoulder[0] + r_shoulder[0]) / 2, 
                       (l_shoulder[1] + r_shoulder[1]) / 2)
        hip_mid = ((l_hip[0] + r_hip[0]) / 2,
                   (l_hip[1] + r_hip[1]) / 2)

        # Calculate angle from vertical (0 degrees is upright)
        dx = shoulder_mid[0] - hip_mid[0]
        dy = shoulder_mid[1] - hip_mid[1]
        
        if dy == 0:
            return 90.0 if dx > 0 else -90.0
        
        angle = np.arctan2(dx, -dy) * 180.0 / np.pi
        return angle

    def calculate_center_of_mass(self, keypoints):
        """Calculate center of mass from keypoints"""
        valid_points = []
        for point in keypoints:
            if np.any(point != 0):  # Valid keypoint
                valid_points.append(point)
        
        if not valid_points:
            return None
        
        valid_points = np.array(valid_points)
        com = np.mean(valid_points, axis=0)
        return com

    def calculate_velocity(self, current_com, current_time):
        """Calculate velocity based on center of mass movement"""
        # First frame - no previous data
        if self.prev_center_of_mass is None or self.prev_timestamp is None:
            return 0.0

        # Same timestamp (shouldn't happen, but safety check)
        if current_time == self.prev_timestamp:
            return 0.0

        dt = current_time - self.prev_timestamp
        if dt <= 0:
            return 0.0

        # Calculate displacement (Euclidean distance)
        displacement = np.linalg.norm(current_com - self.prev_center_of_mass)
        
        # Velocity in pixels per second
        velocity = displacement / dt
        
        return velocity

    def detect_sideways_tumble(self, body_angle, current_time):
        """Detect sideways tumble based on body angle"""
        if body_angle is None:
            return False

        # Check if body is leaning significantly to one side
        abs_angle = abs(body_angle)
        is_sideways_leaning = abs_angle > SIDEWAYS_ANGLE_THRESHOLD

        # Check for sudden angle change
        sudden_angle_change = False
        if self.prev_body_angle is not None:
            angle_change = abs(body_angle - self.prev_body_angle)
            sudden_angle_change = angle_change > SUDDEN_ANGLE_CHANGE

        return is_sideways_leaning or sudden_angle_change

    def detect_lying_posture(self, head_y, shoulder_y, hip_y, body_height, 
                            head_x, shoulder_mid_x, hip_mid_x):
        """Detect if person is in lying posture"""
        if body_height <= 0:
            return False

        # Forward/backward lying detection
        head_hip_ratio = abs(head_y - hip_y) / body_height
        head_below_shoulder = head_y > (shoulder_y + HEAD_SHOULDER_MARGIN)
        
        forward_backward_lying = (
            head_hip_ratio < HEAD_HIP_RATIO_LYING and
            head_below_shoulder
        )

        return forward_backward_lying

    def detect_rapid_movement(self, velocity, current_time):
        """Detect rapid movement based on velocity"""
        if velocity > VELOCITY_THRESHOLD:
            return True
        return False

    def detect_sitting_position(self, l_hip, r_hip, l_knee, r_knee, body_height):
        """Detect if person is in sitting position"""
        # Check if keypoints are valid
        if np.any(l_hip == 0) or np.any(r_hip == 0) or \
           np.any(l_knee == 0) or np.any(r_knee == 0):
            return False

        # Calculate hip and knee midpoints
        hip_y = (l_hip[1] + r_hip[1]) / 2
        knee_y = (l_knee[1] + r_knee[1]) / 2
        
        # Calculate vertical distance between hip and knee
        hip_knee_distance = abs(hip_y - knee_y)
        
        if body_height <= 0:
            return False
        
        # Check if knee-hip distance ratio suggests sitting
        hip_knee_ratio = hip_knee_distance / body_height
        sitting_by_ratio = hip_knee_ratio < SITTING_KNEE_HIP_RATIO
        
        # Check if body height is reduced (compared to baseline if available)
        height_reduced = False
        if self.baseline_body_height is not None and self.baseline_body_height > 0:
            height_ratio = body_height / self.baseline_body_height
            height_reduced = height_ratio < SITTING_HEIGHT_RATIO
        
        return sitting_by_ratio or height_reduced

    def check_person_disappearance(self, person_detected, current_time):
        """Check if person has disappeared (bent head down, moved out of view)"""
        if person_detected:
            self.person_visible_time = current_time
            self.person_disappeared_time = None
            self.last_person_detected = True
            return False
        else:
            # Person not detected
            if self.last_person_detected:
                # Just disappeared
                self.person_disappeared_time = current_time
                self.last_person_detected = False
            
            if self.person_disappeared_time is not None:
                disappear_duration = current_time - self.person_disappeared_time
                # Person disappeared for significant time
                if disappear_duration > PERSON_DISAPPEAR_TIME:
                    return True
            return False

    def detect_head_collapse(self, head_y, head_x, shoulder_y, current_time):
        """Detect head collapse (sudden downward head movement)"""
        if head_y == 0 or shoulder_y == 0:
            return False
        
        # Track head position
        if self.prev_head_y is not None and self.prev_head_timestamp is not None:
            dt = current_time - self.prev_head_timestamp
            if dt > 0:
                # Calculate head drop speed
                head_drop = head_y - self.prev_head_y
                drop_speed = abs(head_drop) / dt
                
                # Check for sudden head drop
                if head_drop > SUDDEN_HEAD_DROP and drop_speed > HEAD_COLLAPSE_SPEED:
                    return True
        
        # Update history
        self.prev_head_y = head_y
        self.prev_head_timestamp = current_time
        return False

    def detect_body_collapse(self, body_height, body_width, center_of_mass_y, current_time):
        """Detect body collapse (sudden height reduction)"""
        if center_of_mass_y is None or self.baseline_body_height is None:
            return False
        
        # Check body height reduction
        if self.baseline_body_height > 0:
            height_ratio = body_height / self.baseline_body_height
            if height_ratio < BODY_COLLAPSE_RATIO:
                return True
        
        # Check vertical velocity
        if self.prev_center_y is not None:
            dt = current_time - (self.prev_timestamp or current_time)
            if dt > 0:
                vertical_velocity = (center_of_mass_y - self.prev_center_y) / dt
                self.vertical_velocity_history.append(vertical_velocity)
                
                if len(self.vertical_velocity_history) >= 3:
                    avg_velocity = np.mean(list(self.vertical_velocity_history))
                    if avg_velocity > VERTICAL_VELOCITY_THRESHOLD:
                        return True
        
        # Check body width expansion (falling spreads body)
        if self.baseline_body_height is not None and self.baseline_body_height > 0:
            expected_width = body_height * 0.3  # Rough width estimate
            if body_width > expected_width * BODY_WIDTH_EXPANSION:
                return True
        
        self.prev_center_y = center_of_mass_y
        return False

    def detect_sudden_drop(self, center_of_mass, current_time):
        """Detect sudden vertical drop (free fall)"""
        if center_of_mass is None or self.prev_center_of_mass is None:
            return False
        
        if self.prev_timestamp is None:
            return False
        
        dt = current_time - self.prev_timestamp
        if dt <= 0:
            return False
        
        # Calculate vertical displacement
        vertical_drop = center_of_mass[1] - self.prev_center_of_mass[1]
        
        # Check for sudden drop
        if vertical_drop > SUDDEN_DROP_THRESHOLD:
            # Calculate velocity
            velocity = vertical_drop / dt
            if velocity > DROP_VELOCITY_THRESHOLD:
                return True
        
        return False

    def detect_forward_backward_lean(self, body_angle):
        """Detect forward or backward lean that could lead to collapse"""
        if body_angle is None:
            return False
        
        # Forward lean (positive angle)
        if body_angle > FORWARD_LEAN_ANGLE:
            return True
        
        # Backward lean (negative angle)
        if body_angle < BACKWARD_LEAN_ANGLE:
            return True
        
        return False

    def detect_knee_collapse(self, l_knee, r_knee, l_ankle, r_ankle, hip_y):
        """Detect knee collapse (extreme knee bend)"""
        if np.any(l_knee == 0) or np.any(r_knee == 0) or \
           np.any(l_ankle == 0) or np.any(r_ankle == 0):
            return False
        
        # Calculate knee angles (simplified - using positions)
        # For left knee
        l_knee_ankle_vec = l_ankle - l_knee
        l_hip_knee_vec = l_knee - np.array([(l_knee[0] + r_knee[0])/2, hip_y])
        
        # Calculate angle between vectors
        def angle_between_vectors(v1, v2):
            dot = np.dot(v1, v2)
            norms = np.linalg.norm(v1) * np.linalg.norm(v2)
            if norms == 0:
                return 180
            cos_angle = np.clip(dot / norms, -1.0, 1.0)
            return np.degrees(np.arccos(cos_angle))
        
        l_knee_angle = angle_between_vectors(l_knee_ankle_vec, l_hip_knee_vec)
        
        # Check for extreme knee bend
        if l_knee_angle < KNEE_BEND_ANGLE or l_knee_angle > (180 - KNEE_BEND_ANGLE):
            return True
        
        # Check ankle-knee height difference
        knee_y = (l_knee[1] + r_knee[1]) / 2
        ankle_y = (l_ankle[1] + r_ankle[1]) / 2
        height_diff = abs(knee_y - ankle_y) / (abs(hip_y - ankle_y) + 1)
        
        if height_diff < ANKLE_KNEE_HEIGHT_DIFF:
            return True
        
        return False

    def detect_keypoint_loss(self, keypoints, keypoints_conf):
        """Detect critical keypoint loss indicating collapse"""
        if keypoints_conf is None:
            return False
        
        # Count missing/low confidence keypoints
        missing_count = np.sum(keypoints_conf < KEYPOINT_CONFIDENCE)
        
        if missing_count >= CRITICAL_KEYPOINT_LOSS:
            return True
        
        # Check if head is missing (critical)
        if keypoints_conf[0] < KEYPOINT_CONFIDENCE:
            # Check how long head has been missing
            return True
        
        return False

    def process_frame(self, frame):
        status = "Normal Activity"
        fall_detected = False
        tumble_type = ""

        results = self.model(frame, conf=MODEL_CONFIDENCE, verbose=False)

        now = time.time()
        
        # ---------------- SAFE CHECK ----------------
        person_detected = (
            results and
            results[0].boxes is not None and
            len(results[0].boxes) > 0 and
            results[0].keypoints is not None
        )
        
        # Check for person disappearance
        person_disappeared = self.check_person_disappearance(person_detected, now)
        
        if not person_detected:
            # Handle person disappearance
            if person_disappeared and self.state != "STANDING":
                # Person disappeared after being detected - potential tumble
                disappear_duration = now - (self.person_disappeared_time or now)
                if disappear_duration >= DISAPPEAR_TUMBLE_THRESHOLD:
                    status = "🚨 TUMBLE DETECTED (Person Disappeared)"
                    fall_detected = True
                    tumble_type = "Person Disappeared"
            
            # No person detected → keep previous state but reset after timeout
            if self.state != "STANDING" and (now - self.state_start_time) > 2.0:
                self.state = "STANDING"
                self.prev_center_of_mass = None
                self.prev_body_angle = None
            
            cv2.putText(
                frame,
                f"State: {self.state} (no person detected)",
                (30, 90),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 255),
                2
            )
            return frame, status, fall_detected

        keypoints = results[0].keypoints.xy.cpu().numpy()
        keypoints_conf = results[0].keypoints.conf.cpu().numpy() if results[0].keypoints.conf is not None else None
        boxes = results[0].boxes.xyxy.cpu().numpy()

        # ---------------- SINGLE PERSON (BIGGEST BOX) ----------------
        areas = []
        for i, box in enumerate(boxes):
            x1, y1, x2, y2 = box
            area = max(0, (x2 - x1)) * max(0, (y2 - y1))
            areas.append((i, area))

        if not areas:
            return frame, status, fall_detected

        idx = max(areas, key=lambda x: x[1])[0]
        person = keypoints[idx]
        person_conf = keypoints_conf[idx] if keypoints_conf is not None else None

        # ---------------- KEYPOINTS ----------------
        head = person[0]
        l_sh = person[5]
        r_sh = person[6]
        l_elbow = person[7]
        r_elbow = person[8]
        l_hip = person[11]
        r_hip = person[12]
        l_knee = person[13]
        r_knee = person[14]

        # Filter low confidence keypoints
        if person_conf is not None:
            if person_conf[0] < KEYPOINT_CONFIDENCE:
                head = np.array([0, 0])
            if person_conf[5] < KEYPOINT_CONFIDENCE or person_conf[6] < KEYPOINT_CONFIDENCE:
                l_sh = np.array([0, 0])
                r_sh = np.array([0, 0])
            if person_conf[11] < KEYPOINT_CONFIDENCE or person_conf[12] < KEYPOINT_CONFIDENCE:
                l_hip = np.array([0, 0])
                r_hip = np.array([0, 0])

        head_x, head_y = head[0], head[1]
        l_sh_x, l_sh_y = l_sh[0], l_sh[1]
        r_sh_x, r_sh_y = r_sh[0], r_sh[1]
        shoulder_mid_x = (l_sh_x + r_sh_x) / 2 if l_sh_x > 0 and r_sh_x > 0 else head_x
        shoulder_y = (l_sh_y + r_sh_y) / 2 if l_sh_y > 0 and r_sh_y > 0 else head_y
        l_hip_x, l_hip_y = l_hip[0], l_hip[1]
        r_hip_x, r_hip_y = r_hip[0], r_hip[1]
        hip_mid_x = (l_hip_x + r_hip_x) / 2 if l_hip_x > 0 and r_hip_x > 0 else head_x
        hip_y = (l_hip_y + r_hip_y) / 2 if l_hip_y > 0 and r_hip_y > 0 else head_y

        # Calculate body metrics
        body_height = np.max(person[:, 1]) - np.min(person[:, 1])
        body_width = np.max(person[:, 0]) - np.min(person[:, 0])
        
        if body_height <= 0:
            return frame, status, fall_detected

        # Update baseline body height if not set or if standing
        if self.baseline_body_height is None or self.state == "STANDING":
            self.baseline_body_height = body_height

        # Calculate body angle for sideways detection
        body_angle = self.calculate_body_angle(l_sh, r_sh, l_hip, r_hip)
        
        # Calculate center of mass
        center_of_mass = self.calculate_center_of_mass(person)
        
        # Detect sitting position
        sitting_position = self.detect_sitting_position(l_hip, r_hip, l_knee, r_knee, body_height)
        
        # Calculate velocity if we have previous data
        velocity = 0.0
        if center_of_mass is not None:
            velocity = self.calculate_velocity(center_of_mass, now)
            # Update previous values for next frame
            self.prev_center_of_mass = center_of_mass.copy()
            self.prev_timestamp = now

        # Store angle history
        if body_angle is not None:
            if self.prev_body_angle is not None:
                self.angle_history.append(body_angle)
                self.timestamp_history.append(now)
            self.prev_body_angle = body_angle

        # ---------------- POSTURE DETECTION ----------------
        lying_posture = self.detect_lying_posture(
            head_y, shoulder_y, hip_y, body_height,
            head_x, shoulder_mid_x, hip_mid_x
        )
        
        sideways_tumble = False
        if body_angle is not None:
            sideways_tumble = self.detect_sideways_tumble(body_angle, now)
        
        rapid_movement = self.detect_rapid_movement(velocity, now)

        # ---------------- STATE MACHINE ----------------
        if self.state == "STANDING":
            # Check for any tumble indicators
            if lying_posture:
                self.state = "FALLING_FORWARD_BACKWARD"
                self.state_start_time = now
                tumble_type = "Forward/Backward"
            elif sideways_tumble:
                self.state = "FALLING_SIDEWAYS"
                self.state_start_time = now
                tumble_type = "Sideways"
            elif rapid_movement:
                self.state = "RAPID_MOVEMENT"
                self.state_start_time = now

        elif self.state == "FALLING_FORWARD_BACKWARD":
            if lying_posture:
                if now - self.state_start_time >= FALLING_TIME:
                    self.state = "LYING"
                    self.state_start_time = now
                    tumble_type = "Forward/Backward"
            else:
                # Returned to normal posture quickly
                if now - self.state_start_time < FALLING_TIME:
                    self.state = "STANDING"
                else:
                    self.state = "STANDING"

        elif self.state == "FALLING_SIDEWAYS":
            if sideways_tumble or lying_posture:
                if now - self.state_start_time >= SIDEWAYS_CONFIRM_TIME:
                    self.state = "LYING"
                    self.state_start_time = now
                    tumble_type = "Sideways"
            else:
                # Returned to normal posture
                if now - self.state_start_time < SIDEWAYS_CONFIRM_TIME:
                    self.state = "STANDING"
                else:
                    self.state = "STANDING"

        elif self.state == "RAPID_MOVEMENT":
            if lying_posture or sideways_tumble:
                self.state = "LYING"
                self.state_start_time = now
                tumble_type = "Rapid Movement"
            elif not rapid_movement:
                self.state = "STANDING"
            elif now - self.state_start_time > 1.0:
                self.state = "STANDING"

        elif self.state == "SITTING_TUMBLE":
            if sitting_position and (lying_posture or sideways_tumble):
                if now - self.state_start_time >= SITTING_TUMBLE_THRESHOLD:
                    self.state = "LYING"
                    self.state_start_time = now
                    tumble_type = "Sitting"
            elif not sitting_position:
                # Person got up from sitting
                self.state = "STANDING"
            elif now - self.state_start_time > 2.0:
                self.state = "STANDING"

        elif self.state == "LYING":
            if lying_posture or sideways_tumble or sitting_position:
                if now - self.state_start_time >= LYING_CONFIRM_TIME:
                    status = f"🚨 TUMBLE DETECTED ({tumble_type})"
                    fall_detected = True
            else:
                # Person got up
                self.state = "STANDING"

        # ---------------- DRAW & ANNOTATE ----------------
        frame = results[0].plot()

        # Draw additional information
        info_y = 30
        cv2.putText(
            frame,
            f"State: {self.state}",
            (30, info_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )
        
        info_y += 35
        if body_angle is not None:
            cv2.putText(
                frame,
                f"Body Angle: {body_angle:.1f}°",
                (30, info_y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 0),
                2
            )
            info_y += 30

        if velocity > 0:
            cv2.putText(
                frame,
                f"Velocity: {velocity:.2f}",
                (30, info_y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 0),
                2
            )
            info_y += 30

        # Main status display
        cv2.putText(
            frame,
            status,
            (30, frame.shape[0] - 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.2,
            (0, 0, 255) if fall_detected else (0, 255, 0),
            3
        )

        # Draw body angle indicator
        if body_angle is not None and center_of_mass is not None:
            angle_rad = np.deg2rad(body_angle)
            line_length = 50
            end_x = int(center_of_mass[0] + line_length * np.sin(angle_rad))
            end_y = int(center_of_mass[1] + line_length * np.cos(angle_rad))
            cv2.line(
                frame,
                (int(center_of_mass[0]), int(center_of_mass[1])),
                (end_x, end_y),
                (0, 255, 255),
                3
            )

        # ---------------- SAVE IMAGE ----------------
        if fall_detected and (now - self.last_saved_time) > FALL_COOLDOWN_TIME:
            filename = f"images/fall_{int(now)}.jpg"
            cv2.imwrite(filename, frame)
            self.last_saved_time = now

        return frame, status, fall_detected
