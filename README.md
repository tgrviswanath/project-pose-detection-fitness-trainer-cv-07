# Project 07 - Pose Detection Fitness Trainer (CV)

Detect 33 body landmarks using MediaPipe Pose, compute joint angles, and provide rule-based fitness feedback.

## Architecture

```
Frontend :3000  →  Backend :8000  →  CV Service :8001
  React/MUI        FastAPI/httpx      FastAPI/MediaPipe
```

## How It Works

```
Image uploaded
    ↓
MediaPipe Pose detects 33 body landmarks
    ↓
Joint angles computed (knees, elbows, hips, shoulders)
    ↓
Rule-based fitness feedback generated
    ↓
Skeleton drawn on annotated image with angle labels
    ↓
Return: landmarks[] + angles{} + feedback[] + annotated_image (base64)
```

## Joint Angles Computed

| Joint | Landmarks Used | Fitness Use |
|---|---|---|
| Left/Right Knee | hip-knee-ankle | Squat depth |
| Left/Right Elbow | shoulder-elbow-wrist | Curl / push-up |
| Left/Right Hip | shoulder-hip-knee | Posture |
| Left/Right Shoulder | elbow-shoulder-hip | Overhead press |

## What's Different from Projects 01-06

| | P05 | P06 | P07 |
|---|---|---|---|
| Model | Cosine similarity | YOLOv8 | MediaPipe Pose |
| Output | Similar images | Object boxes | 33 keypoints + angles |
| New concept | Embeddings | YOLO | Skeleton + biomechanics |

## Local Run

```bash
# Terminal 1 - CV Service
cd cv-service && python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001

# Terminal 2 - Backend
cd backend && python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Terminal 3 - Frontend
cd frontend && npm install && npm start
```

- CV Service docs: http://localhost:8001/docs
- Backend docs:   http://localhost:8000/docs
- UI:             http://localhost:3000

## Docker

```bash
docker-compose up --build
```

## Dataset
Use any fitness/exercise photo with a clearly visible full body.
Try Human Pose Estimation datasets from Kaggle (MPII, COCO Keypoints).
