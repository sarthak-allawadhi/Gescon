'''
    Smart Hand Gesture Mouse Control System
    ========================================
    Original concept by Aditya Jindal. Enhanced & improved version.
    
    Supported Gestures:
        1. Cursor Movement     — Point with index finger to move cursor
        2. Single Click        — Pinch thumb + index finger together
        3. Double Click        — Two quick pinches within 0.4 seconds
        4. Scroll Up           — All 4 fingers up, hand in upper zone
        5. Scroll Down         — All 4 fingers up, hand in lower zone
        6. Screenshot          — Pinch thumb + pinky (peace sign with thumb-pinky touch)
        7. Type a Letter       — Show a fist (all fingers closed), then open specific fingers:
                                   • Index only        → types "A"
                                   • Index + Middle     → types "B"
                                   • Index + Mid + Ring → types "C"
        
    Controls:
        Press 'q' to quit the application.
'''

import cv2 as cv
import mediapipe as mp
import pyautogui as pag
import time as t
import math as m
import os
from datetime import datetime
from util import get_angle, get_distance, get_hand_size, get_finger_states, smooth_value

# ──────────────────────────────────────────────
#  PyAutoGUI Configuration
# ──────────────────────────────────────────────
pag.PAUSE = 0          # Remove the default 0.1s delay after every PyAutoGUI call (huge FPS boost)
pag.FAILSAFE = True    # Move mouse to top-left corner to emergency-stop the script

# ──────────────────────────────────────────────
#  MediaPipe Hand Tracking Setup
# ──────────────────────────────────────────────
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

hands = mp_hands.Hands(
    max_num_hands=1,              # Track only one hand for stability
    min_detection_confidence=0.8,
    min_tracking_confidence=0.7   # Higher tracking confidence = fewer false positives
)

# ──────────────────────────────────────────────
#  Webcam Setup
# ──────────────────────────────────────────────
cap = cv.VideoCapture(0)
# If camera doesn't open with 0, try changing to 1 (for external / iPhone Continuity Camera)

cap.set(cv.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv.CAP_PROP_FPS, 30)

if not cap.isOpened():
    print("ERROR: Camera could not be opened!")
    print("Try changing cv.VideoCapture(0) to cv.VideoCapture(1)")
    exit()

# ──────────────────────────────────────────────
#  Screen & Cursor Configuration
# ──────────────────────────────────────────────
screen_w, screen_h = pag.size()

# Active Zone: Only map hand positions within this zone to the full screen.
# This means you don't have to reach the very edges of the camera frame.
ACTIVE_ZONE_X_MIN = 0.15    # Left boundary  (15% from left)
ACTIVE_ZONE_X_MAX = 0.85    # Right boundary  (85% from left)
ACTIVE_ZONE_Y_MIN = 0.15    # Top boundary    (15% from top)
ACTIVE_ZONE_Y_MAX = 0.85    # Bottom boundary (85% from top)

# Cursor smoothing (EMA factor: lower = smoother but more laggy, higher = snappier)
SMOOTHING_FACTOR = 0.35
smooth_x, smooth_y = screen_w // 2, screen_h // 2

# ──────────────────────────────────────────────
#  Gesture State Variables
# ──────────────────────────────────────────────
click_times = []
click_cooldown = 0.5
freeze_cursor = False
scroll_mode = False

# Screenshot cooldown (prevent rapid-fire screenshots)
last_screenshot_time = 0
SCREENSHOT_COOLDOWN = 2.0

# Type gesture state
last_type_time = 0
TYPE_COOLDOWN = 1.0
prev_fist = False   # Track if we were in a fist on the previous frame

# FPS counter
fps_time = t.time()

# Screenshots directory
SCREENSHOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "screenshots")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

# ──────────────────────────────────────────────
#  Helper Functions
# ──────────────────────────────────────────────

def map_to_screen(x, y):
    """Map hand coordinates from active zone to full screen coordinates."""
    # Clamp to active zone
    x = max(ACTIVE_ZONE_X_MIN, min(ACTIVE_ZONE_X_MAX, x))
    y = max(ACTIVE_ZONE_Y_MIN, min(ACTIVE_ZONE_Y_MAX, y))
    
    # Normalize within active zone (0.0 to 1.0)
    norm_x = (x - ACTIVE_ZONE_X_MIN) / (ACTIVE_ZONE_X_MAX - ACTIVE_ZONE_X_MIN)
    norm_y = (y - ACTIVE_ZONE_Y_MIN) / (ACTIVE_ZONE_Y_MAX - ACTIVE_ZONE_Y_MIN)
    
    # Map to screen
    screen_x = int(norm_x * screen_w)
    screen_y = int(norm_y * screen_h)
    
    return screen_x, screen_y

def get_pinch_distance(hand_landmarks, tip1_id, tip2_id):
    """Get normalized pinch distance between two fingertips (distance-invariant)."""
    tip1 = hand_landmarks.landmark[tip1_id]
    tip2 = hand_landmarks.landmark[tip2_id]
    raw_dist = m.hypot(tip1.x - tip2.x, tip1.y - tip2.y)
    
    # Normalize by hand size so distance threshold works at any hand-to-camera distance
    hand_size = get_hand_size(hand_landmarks)
    if hand_size > 0:
        return raw_dist / hand_size
    return raw_dist

def draw_status(frame, text, position=(10, 50), color=(0, 255, 255), scale=0.8):
    """Draw status text with a dark background for readability."""
    (text_w, text_h), _ = cv.getTextSize(text, cv.FONT_HERSHEY_SIMPLEX, scale, 2)
    x, y = position
    cv.rectangle(frame, (x - 5, y - text_h - 10), (x + text_w + 5, y + 5), (0, 0, 0), -1)
    cv.putText(frame, text, position, cv.FONT_HERSHEY_SIMPLEX, scale, color, 2)

def draw_active_zone(frame, frame_h, frame_w):
    """Draw the active tracking zone on the frame."""
    x1 = int(ACTIVE_ZONE_X_MIN * frame_w)
    y1 = int(ACTIVE_ZONE_Y_MIN * frame_h)
    x2 = int(ACTIVE_ZONE_X_MAX * frame_w)
    y2 = int(ACTIVE_ZONE_Y_MAX * frame_h)
    cv.rectangle(frame, (x1, y1), (x2, y2), (100, 255, 100), 1)

# ──────────────────────────────────────────────
#  Main Loop
# ──────────────────────────────────────────────
print("\n╔══════════════════════════════════════════╗")
print("║   Smart Hand Mouse Control System        ║")
print("║──────────────────────────────────────────║")
print("║   Gestures:                              ║")
print("║     • Index finger    → Move cursor      ║")
print("║     • Thumb + Index   → Click            ║")
print("║     • Quick 2x pinch  → Double Click     ║")
print("║     • All fingers up  → Scroll mode      ║")
print("║     • Thumb + Pinky   → Screenshot       ║")
print("║     • Fist → Fingers  → Type letter      ║")
print("║                                          ║")
print("║   Press 'q' to quit                      ║")
print("╚══════════════════════════════════════════╝\n")

while True:
    ret, frame = cap.read()
    if not ret:
        print("ERROR: Frame could not be received!")
        break
    
    frame = cv.flip(frame, 1)
    frame_h, frame_w, _ = frame.shape
    rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
    result = hands.process(rgb)

    # Draw active zone guide
    draw_active_zone(frame, frame_h, frame_w)

    # ── FPS Counter ──
    current_time = t.time()
    fps = 1 / (current_time - fps_time) if (current_time - fps_time) > 0 else 0
    fps_time = current_time
    cv.putText(frame, f"FPS: {int(fps)}", (frame_w - 120, 30), cv.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    if result.multi_hand_landmarks:
        # Process only the first detected hand
        hand_landmarks = result.multi_hand_landmarks[0]
        mp_drawing.draw_landmarks(
            frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
            mp_drawing_styles.get_default_hand_landmarks_style(),
            mp_drawing_styles.get_default_hand_connections_style()
        )

        # ── Get Fingertip Positions ──
        thumb_tip = hand_landmarks.landmark[4]
        index_tip = hand_landmarks.landmark[8]
        middle_tip = hand_landmarks.landmark[12]
        ring_tip = hand_landmarks.landmark[16]
        pinky_tip = hand_landmarks.landmark[20]

        # ── Finger States: [thumb, index, middle, ring, pinky] ──
        finger_states = get_finger_states(hand_landmarks)
        fingers_up_count = sum(finger_states[1:])  # Exclude thumb for scroll/type detection

        # ══════════════════════════════════════
        #  GESTURE 1: Click (Thumb + Index Pinch)
        # ══════════════════════════════════════
        pinch_dist = get_pinch_distance(hand_landmarks, 4, 8)  # thumb tip to index tip
        
        if pinch_dist < 0.25:   # Normalized threshold (works at any distance!)
            if not freeze_cursor:
                freeze_cursor = True
                click_times.append(t.time())

                # Double Click: Two pinches within 0.4 seconds
                if len(click_times) >= 2 and click_times[-1] - click_times[-2] < 0.4:
                    pag.doubleClick()
                    draw_status(frame, "DOUBLE CLICK", (10, 50), (0, 255, 255))
                    click_times = []
                else:
                    pag.click()
                    draw_status(frame, "SINGLE CLICK", (10, 50), (255, 255, 0))
        else:
            if freeze_cursor:
                t.sleep(0.05)  # Small debounce on release
            freeze_cursor = False

        # Clean old click times (prevent memory leak)
        if len(click_times) > 5:
            click_times = click_times[-2:]

        # ══════════════════════════════════════
        #  GESTURE 2: Cursor Movement (Index Finger)
        # ══════════════════════════════════════
        if not freeze_cursor:
            target_x, target_y = map_to_screen(index_tip.x, index_tip.y)
            
            # Apply smoothing (EMA)
            smooth_x = smooth_value(smooth_x, target_x, SMOOTHING_FACTOR)
            smooth_y = smooth_value(smooth_y, target_y, SMOOTHING_FACTOR)
            
            pag.moveTo(int(smooth_x), int(smooth_y))

        # ══════════════════════════════════════
        #  GESTURE 3: Scroll Mode (All 4 fingers up)
        # ══════════════════════════════════════
        scroll_mode = (fingers_up_count == 4)

        if scroll_mode:
            if index_tip.y < 0.35:
                pag.scroll(5)
                draw_status(frame, "SCROLL UP", (10, 90), (0, 200, 255))
            elif index_tip.y > 0.65:
                pag.scroll(-5)
                draw_status(frame, "SCROLL DOWN", (10, 90), (255, 100, 0))
            else:
                draw_status(frame, "SCROLL MODE", (10, 90), (200, 200, 200))

        # ══════════════════════════════════════
        #  GESTURE 4: Screenshot (Thumb + Pinky Pinch)
        # ══════════════════════════════════════
        pinky_pinch = get_pinch_distance(hand_landmarks, 4, 20)  # thumb tip to pinky tip
        
        if pinky_pinch < 0.3 and (t.time() - last_screenshot_time) > SCREENSHOT_COOLDOWN:
            # Only trigger if index, middle, ring are UP (to avoid accidental triggers from fist)
            if finger_states[1] and finger_states[2] and finger_states[3]:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filepath = os.path.join(SCREENSHOT_DIR, f"screenshot_{timestamp}.png")
                screenshot = pag.screenshot()
                screenshot.save(filepath)
                last_screenshot_time = t.time()
                draw_status(frame, f"SCREENSHOT SAVED!", (10, 130), (0, 255, 0))
                print(f"  Screenshot saved: {filepath}")

        # ══════════════════════════════════════
        #  GESTURE 5: Type a Letter (Fist → Open fingers)
        # ══════════════════════════════════════
        #  Make a fist first, then open fingers to type:
        #    Index only          → "A"
        #    Index + Middle      → "B"
        #    Index + Mid + Ring  → "C"
        # ══════════════════════════════════════
        is_fist = (fingers_up_count == 0 and not finger_states[0])
        
        if is_fist:
            prev_fist = True
            draw_status(frame, "FIST READY...", (10, 170), (180, 180, 180))
        
        elif prev_fist and (t.time() - last_type_time) > TYPE_COOLDOWN:
            # Transitioned from fist to open — check which fingers opened
            if finger_states[1] and not finger_states[2] and not finger_states[3] and not finger_states[4]:
                pag.press('a')
                draw_status(frame, "TYPED: A", (10, 170), (255, 100, 255))
                last_type_time = t.time()
                prev_fist = False
            
            elif finger_states[1] and finger_states[2] and not finger_states[3] and not finger_states[4]:
                pag.press('b')
                draw_status(frame, "TYPED: B", (10, 170), (255, 100, 255))
                last_type_time = t.time()
                prev_fist = False
            
            elif finger_states[1] and finger_states[2] and finger_states[3] and not finger_states[4]:
                pag.press('c')
                draw_status(frame, "TYPED: C", (10, 170), (255, 100, 255))
                last_type_time = t.time()
                prev_fist = False
            
            else:
                # If no recognized pattern, reset fist state
                prev_fist = False

        # ── Draw finger state indicator ──
        state_text = "Fingers: " + "".join(["●" if f else "○" for f in finger_states])
        cv.putText(frame, state_text, (10, frame_h - 20), cv.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

    # ── Display Frame ──
    cv.imshow("Smart Hand Mouse Control", frame)
    if cv.waitKey(1) & 0xFF == ord('q'):
        break

# ── Cleanup ──
cap.release()
cv.destroyAllWindows()
print("\nSession ended. Goodbye!")