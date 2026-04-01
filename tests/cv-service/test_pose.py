from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from PIL import Image
import io
from app.main import app

client = TestClient(app)


def _sample_image() -> bytes:
    img = Image.new("RGB", (480, 640), color=(200, 180, 160))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def _mock_landmark(x=0.5, y=0.5, z=0.0, vis=0.9):
    lm = MagicMock()
    lm.x, lm.y, lm.z, lm.visibility = x, y, z, vis
    return lm


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


@patch("app.core.detector._get_pose")
def test_pose_detected(mock_get_pose):
    mock_pose = MagicMock()
    mock_results = MagicMock()
    mock_results.pose_landmarks = MagicMock()
    mock_results.pose_landmarks.landmark = [_mock_landmark()] * 33
    mock_pose.process.return_value = mock_results
    mock_get_pose.return_value = mock_pose

    r = client.post("/api/v1/cv/pose",
        files={"file": ("test.jpg", _sample_image(), "image/jpeg")})
    assert r.status_code == 200
    data = r.json()
    assert "pose_detected" in data
    assert "landmarks" in data
    assert "angles" in data
    assert "feedback" in data
    assert "annotated_image" in data


@patch("app.core.detector._get_pose")
def test_no_pose(mock_get_pose):
    mock_pose = MagicMock()
    mock_results = MagicMock()
    mock_results.pose_landmarks = None
    mock_pose.process.return_value = mock_results
    mock_get_pose.return_value = mock_pose

    r = client.post("/api/v1/cv/pose",
        files={"file": ("test.jpg", _sample_image(), "image/jpeg")})
    assert r.status_code == 200
    assert r.json()["pose_detected"] is False


def test_unsupported_format():
    r = client.post("/api/v1/cv/pose",
        files={"file": ("test.gif", b"GIF89a", "image/gif")})
    assert r.status_code == 400


def test_empty_file():
    r = client.post("/api/v1/cv/pose",
        files={"file": ("test.jpg", b"", "image/jpeg")})
    assert r.status_code == 400
