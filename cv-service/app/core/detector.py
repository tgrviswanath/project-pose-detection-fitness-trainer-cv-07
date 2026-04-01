"""
MediaPipe Pose detector.
- Detects 33 body landmarks
- Computes key joint angles (knees, elbows, hips, shoulders)
- Draws skeleton on annotated image
- Returns landmarks + angles + fitness feedback + annotated image
"""
import cv2
import mediapipe as mp
import numpy as np
from PIL import Image
import io
import base64
from app.core.config import settings
from app.core.angles import calculate_angle, get_exercise_feedback

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

_pose = None


def _get_pose():
    global _pose
    if _pose is None:
        _pose = mp_pose.Pose(
            static_image_mode=True,
            min_detection_confidence=settings.MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=settings.MIN_TRACKING_CONFIDENCE,
        )
    return _pose


def _load_image(image_bytes: bytes) -> np.ndarray:
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    w, h = img.size
    if max(w, h) > settings.MAX_IMAGE_SIZE:
        scale = settings.MAX_IMAGE_SIZE / max(w, h)
        img = img.resize((int(w * scale), int(h * scale)))
    return np.array(img)


def _to_base64(img_rgb: np.ndarray) -> str:
    img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
    _, buf = cv2.imencode(".jpg", img_bgr, [cv2.IMWRITE_JPEG_QUALITY, 85])
    return base64.b64encode(buf).decode("utf-8")


def _lm(landmarks, idx, h, w):
    lm = landmarks[idx]
    return [lm.x * w, lm.y * h]


def detect_pose(image_bytes: bytes) -> dict:
    pose = _get_pose()
    img = _load_image(image_bytes)
    h, w = img.shape[:2]

    results = pose.process(img)

    if not results.pose_landmarks:
        return {
            "pose_detected": False,
            "landmarks": [],
            "angles": {},
            "feedback": [],
            "annotated_image": _to_base64(img),
        }

    lms = results.pose_landmarks.landmark

    # Extract key landmarks
    def pt(idx): return _lm(lms, idx, h, w)

    # Compute joint angles using MediaPipe landmark indices
    angles = {
        "left_elbow":    calculate_angle(pt(11), pt(13), pt(15)),   # shoulder-elbow-wrist
        "right_elbow":   calculate_angle(pt(12), pt(14), pt(16)),
        "left_knee":     calculate_angle(pt(23), pt(25), pt(27)),   # hip-knee-ankle
        "right_knee":    calculate_angle(pt(24), pt(26), pt(28)),
        "left_hip":      calculate_angle(pt(11), pt(23), pt(25)),   # shoulder-hip-knee
        "right_hip":     calculate_angle(pt(12), pt(24), pt(26)),
        "left_shoulder": calculate_angle(pt(13), pt(11), pt(23)),   # elbow-shoulder-hip
        "right_shoulder":calculate_angle(pt(14), pt(12), pt(24)),
    }

    # Build landmarks list (normalized 0-1)
    landmarks = [
        {
            "index": i,
            "name": mp_pose.PoseLandmark(i).name,
            "x": round(lm.x, 4),
            "y": round(lm.y, 4),
            "z": round(lm.z, 4),
            "visibility": round(lm.visibility, 4),
        }
        for i, lm in enumerate(lms)
    ]

    # Draw skeleton
    annotated = img.copy()
    mp_drawing.draw_landmarks(
        annotated,
        results.pose_landmarks,
        mp_pose.POSE_CONNECTIONS,
        landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style(),
    )

    # Overlay angle labels on image
    angle_positions = {
        "left_elbow": pt(13), "right_elbow": pt(14),
        "left_knee": pt(25), "right_knee": pt(26),
        "left_hip": pt(23), "right_hip": pt(24),
    }
    for name, pos in angle_positions.items():
        if name in angles:
            cv2.putText(
                annotated, f"{angles[name]:.0f}°",
                (int(pos[0]) + 5, int(pos[1]) - 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2,
            )

    feedback = get_exercise_feedback(angles)

    return {
        "pose_detected": True,
        "landmarks": landmarks,
        "angles": angles,
        "feedback": feedback,
        "annotated_image": _to_base64(annotated),
        "image_width": w,
        "image_height": h,
    }
