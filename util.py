import numpy as np

def get_angle(a, b, c):
    """Calculate the angle at point b formed by points a, b, c (in degrees)."""
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(np.degrees(radians))
    if angle > 180:
        angle = 360 - angle
    return angle

def get_distance(landmark_list):
    """Calculate distance between two landmarks and interpolate to 0-1000 range."""
    if len(landmark_list) < 2:
        return 0
    (x1, y1), (x2, y2) = landmark_list[0], landmark_list[1]
    l = np.hypot(x2 - x1, y2 - y1)
    return np.interp(l, [0, 1], [0, 1000])

def get_hand_size(hand_landmarks):
    """Calculate approximate hand size using wrist-to-middle-finger-base distance.
    Used to normalize gesture distances so they work regardless of hand-to-camera distance."""
    wrist = hand_landmarks.landmark[0]
    middle_base = hand_landmarks.landmark[9]
    return np.hypot(wrist.x - middle_base.x, wrist.y - middle_base.y)

def is_finger_up(hand_landmarks, tip_id):
    """Check if a finger is extended (tip is above its PIP joint).
    tip_id: 8 (index), 12 (middle), 16 (ring), 20 (pinky)"""
    return hand_landmarks.landmark[tip_id].y < hand_landmarks.landmark[tip_id - 2].y

def is_thumb_up(hand_landmarks):
    """Check if thumb is extended (tip is further from palm than IP joint)."""
    thumb_tip = hand_landmarks.landmark[4]
    thumb_ip = hand_landmarks.landmark[3]
    wrist = hand_landmarks.landmark[0]
    # Use x-distance from wrist since thumb extends sideways
    return abs(thumb_tip.x - wrist.x) > abs(thumb_ip.x - wrist.x)

def get_finger_states(hand_landmarks):
    """Return a list of 5 booleans: [thumb, index, middle, ring, pinky] — True if extended."""
    return [
        is_thumb_up(hand_landmarks),
        is_finger_up(hand_landmarks, 8),
        is_finger_up(hand_landmarks, 12),
        is_finger_up(hand_landmarks, 16),
        is_finger_up(hand_landmarks, 20),
    ]

def smooth_value(current, target, factor=0.3):
    """Exponential moving average for smooth transitions."""
    return current + (target - current) * factor