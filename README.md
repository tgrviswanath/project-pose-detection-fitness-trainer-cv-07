# Project CV-07 - Pose Detection Fitness Trainer

Microservice CV system that detects 33 body landmarks using MediaPipe Pose, computes joint angles, and provides rule-based fitness feedback.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  FRONTEND  (React - Port 3000)                              │
│  axios POST /api/v1/pose                                    │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP JSON
┌──────────────────────▼──────────────────────────────────────┐
│  BACKEND  (FastAPI - Port 8000)                             │
│  httpx POST /api/v1/cv/pose  →  calls cv-service            │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP JSON
┌──────────────────────▼──────────────────────────────────────┐
│  CV SERVICE  (FastAPI - Port 8001)                          │
│  MediaPipe Pose → 33 landmarks → joint angles → feedback    │
│  Returns { landmarks[], angles{}, feedback[], annotated_image } │
└─────────────────────────────────────────────────────────────┘
```

---

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

---

## Joint Angles Computed

| Joint | Landmarks Used | Fitness Use |
|-------|---------------|-------------|
| Left/Right Knee | hip-knee-ankle | Squat depth |
| Left/Right Elbow | shoulder-elbow-wrist | Curl / push-up |
| Left/Right Hip | shoulder-hip-knee | Posture |
| Left/Right Shoulder | elbow-shoulder-hip | Overhead press |

---

## Tech Stack

| Layer | Tools |
|-------|-------|
| Frontend | React, MUI |
| Backend | FastAPI, httpx |
| CV | MediaPipe Pose, OpenCV, NumPy |
| Model | Pretrained MediaPipe Pose (auto-loaded) |
| Deployment | Docker, docker-compose |

---

## Prerequisites

- Python 3.12+
- Node.js — run `nvs use 20.14.0` before starting the frontend

---

## Local Run

### Step 1 — Start CV Service (Terminal 1)

```bash
cd cv-service
python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

Verify: http://localhost:8001/health → `{"status":"ok"}`

### Step 2 — Start Backend (Terminal 2)

```bash
cd backend
python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Step 3 — Start Frontend (Terminal 3)

```bash
cd frontend
npm install && npm start
```

Opens at: http://localhost:3000

---

## Environment Files

### `backend/.env`

```
APP_NAME=Pose Detection API
APP_VERSION=1.0.0
ALLOWED_ORIGINS=["http://localhost:3000"]
CV_SERVICE_URL=http://localhost:8001
```

### `frontend/.env`

```
REACT_APP_API_URL=http://localhost:8000
```

---

## Docker Run

```bash
docker-compose up --build
```

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API docs | http://localhost:8000/docs |
| CV Service docs | http://localhost:8001/docs |

---

## Run Tests

```bash
cd cv-service && venv\Scripts\activate
pytest ../tests/cv-service/ -v

cd backend && venv\Scripts\activate
pytest ../tests/backend/ -v
```

---

## Project Structure

```
project-pose-detection-fitness-trainer-cv-07/
├── frontend/                    ← React (Port 3000)
├── backend/                     ← FastAPI (Port 8000)
├── cv-service/                  ← FastAPI CV (Port 8001)
│   └── app/
│       ├── api/routes.py
│       ├── core/pose.py         ← MediaPipe Pose + angle computation
│       ├── core/feedback.py     ← Rule-based fitness feedback
│       └── main.py
├── samples/
├── tests/
├── docker/
└── docker-compose.yml
```

---

## API Reference

```
POST /api/v1/pose
Body:     { "image": "<base64>" }
Response: {
  "landmarks": [{ "x": 0.5, "y": 0.3, "z": 0.1, "visibility": 0.99 }],
  "angles": { "left_knee": 145.2, "right_elbow": 90.1 },
  "feedback": ["Keep your back straight", "Lower your squat"],
  "annotated_image": "<base64>"
}
```

---

## Dataset

Use any fitness/exercise photo with a clearly visible full body.
Try Human Pose Estimation datasets from Kaggle (MPII, COCO Keypoints).
