"""
Joint angle calculator for fitness feedback.
Computes angle at the middle point given 3 landmark points.
"""
import numpy as np


def calculate_angle(a: list, b: list, c: list) -> float:
    """
    Calculate angle at point b given points a, b, c.
    Returns angle in degrees (0-180).
    """
    a, b, c = np.array(a), np.array(b), np.array(c)
    ba = a - b
    bc = c - b
    cosine = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-7)
    angle = np.degrees(np.arccos(np.clip(cosine, -1.0, 1.0)))
    return round(float(angle), 1)


def get_exercise_feedback(angles: dict) -> list[dict]:
    """
    Rule-based fitness feedback based on joint angles.
    Returns list of feedback items with status and message.
    """
    feedback = []

    # Squat check: knee angle
    if "left_knee" in angles and "right_knee" in angles:
        avg_knee = (angles["left_knee"] + angles["right_knee"]) / 2
        if avg_knee < 90:
            feedback.append({"joint": "knees", "status": "good", "message": "Deep squat — great depth!"})
        elif avg_knee < 120:
            feedback.append({"joint": "knees", "status": "warning", "message": "Squat deeper for full range of motion"})
        else:
            feedback.append({"joint": "knees", "status": "info", "message": f"Knee angle: {avg_knee:.0f}°"})

    # Elbow check: arm curl / push-up
    if "left_elbow" in angles and "right_elbow" in angles:
        avg_elbow = (angles["left_elbow"] + angles["right_elbow"]) / 2
        if avg_elbow < 45:
            feedback.append({"joint": "elbows", "status": "good", "message": "Full curl — excellent!"})
        elif avg_elbow < 90:
            feedback.append({"joint": "elbows", "status": "warning", "message": "Curl more for full range"})

    # Hip check: posture
    if "left_hip" in angles and "right_hip" in angles:
        avg_hip = (angles["left_hip"] + angles["right_hip"]) / 2
        if 160 <= avg_hip <= 180:
            feedback.append({"joint": "hips", "status": "good", "message": "Good upright posture"})
        elif avg_hip < 120:
            feedback.append({"joint": "hips", "status": "warning", "message": "Keep your back straight"})

    # Shoulder check
    if "left_shoulder" in angles and "right_shoulder" in angles:
        avg_shoulder = (angles["left_shoulder"] + angles["right_shoulder"]) / 2
        feedback.append({"joint": "shoulders", "status": "info",
                         "message": f"Shoulder angle: {avg_shoulder:.0f}°"})

    return feedback
