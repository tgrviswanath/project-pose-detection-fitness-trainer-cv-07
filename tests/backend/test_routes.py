from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from app.main import app

client = TestClient(app)

MOCK_RESULT = {
    "pose_detected": True,
    "landmarks": [{"index": 0, "name": "NOSE", "x": 0.5, "y": 0.2, "z": 0.0, "visibility": 0.99}],
    "angles": {"left_knee": 145.2, "right_knee": 142.8, "left_elbow": 165.0, "right_elbow": 163.5,
               "left_hip": 172.1, "right_hip": 170.5, "left_shoulder": 45.2, "right_shoulder": 44.8},
    "feedback": [{"joint": "knees", "status": "info", "message": "Knee angle: 144°"}],
    "annotated_image": "base64string",
    "image_width": 480, "image_height": 640,
}


def test_health():
    r = client.get("/health")
    assert r.status_code == 200


@patch("app.core.service.detect_pose", new_callable=AsyncMock, return_value=MOCK_RESULT)
def test_pose_endpoint(mock_pose):
    r = client.post("/api/v1/pose",
        files={"file": ("test.jpg", b"fake", "image/jpeg")})
    assert r.status_code == 200
    data = r.json()
    assert data["pose_detected"] is True
    assert "angles" in data
    assert "feedback" in data
    assert len(data["landmarks"]) == 1
