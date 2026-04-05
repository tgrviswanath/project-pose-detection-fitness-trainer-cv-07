# GCP Deployment Guide — Project CV-07 Pose Detection Fitness Trainer

---

## GCP Services for Pose Detection

### 1. Ready-to-Use AI (No Model Needed)

| Service                              | What it does                                                                 | When to use                                        |
|--------------------------------------|------------------------------------------------------------------------------|----------------------------------------------------|
| **Cloud Vision API**                 | Detect body parts and crop regions for pose analysis                         | Preprocessing step before pose estimation          |
| **Vertex AI Gemini Vision**          | Gemini Pro Vision for fitness form analysis and coaching feedback via prompt | Replace your rule-based feedback pipeline          |
| **Vertex AI AutoML Vision**          | Train custom pose classifier on your fitness dataset                         | When you need custom exercise recognition          |

> **Vertex AI Gemini Vision** replaces your MediaPipe + rule-based feedback pipeline. Gemini can analyze joint angles, form, and generate coaching feedback from a single image.

### 2. Host Your Own Model (Keep Current Stack)

| Service                    | What it does                                                        | When to use                                           |
|----------------------------|---------------------------------------------------------------------|-------------------------------------------------------|
| **Cloud Run**              | Run backend + cv-service containers — serverless, scales to zero    | Best match for your current microservice architecture |
| **Artifact Registry**      | Store your Docker images                                            | Used with Cloud Run or GKE                            |

### 3. Frontend Hosting

| Service                    | What it does                                                              |
|----------------------------|---------------------------------------------------------------------------| 
| **Firebase Hosting**       | Host your React frontend — free tier, auto CI/CD from GitHub              |

### 4. Supporting Services

| Service                        | Purpose                                                                   |
|--------------------------------|---------------------------------------------------------------------------|
| **Cloud Storage**              | Store uploaded images and pose analysis results                           |
| **Secret Manager**             | Store API keys and connection strings instead of .env files               |
| **Cloud Monitoring + Logging** | Track detection latency, joint angle distributions, request volume        |

---

## Recommended Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Firebase Hosting — React Frontend                          │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTPS
┌──────────────────────▼──────────────────────────────────────┐
│  Cloud Run — Backend (FastAPI :8000)                        │
└──────────────────────┬──────────────────────────────────────┘
                       │ Internal HTTPS
        ┌──────────────┴──────────────┐
        │ Option A                    │ Option B
        ▼                             ▼
┌───────────────────┐    ┌────────────────────────────────────┐
│ Cloud Run         │    │ Vertex AI Gemini Vision            │
│ CV Service :8001  │    │ Fitness form analysis + coaching   │
│ MediaPipe Pose    │    │ No model download needed           │
└───────────────────┘    └────────────────────────────────────┘
```

---

## Prerequisites

```bash
gcloud auth login
gcloud projects create posedetect-cv-project --name="Pose Detection Fitness"
gcloud config set project posedetect-cv-project
gcloud services enable run.googleapis.com artifactregistry.googleapis.com \
  secretmanager.googleapis.com aiplatform.googleapis.com \
  storage.googleapis.com cloudbuild.googleapis.com
```

---

## Step 1 — Create Artifact Registry and Push Images

```bash
GCP_REGION=europe-west2
gcloud artifacts repositories create posedetect-repo \
  --repository-format=docker --location=$GCP_REGION
gcloud auth configure-docker $GCP_REGION-docker.pkg.dev
AR=$GCP_REGION-docker.pkg.dev/posedetect-cv-project/posedetect-repo
docker build -f docker/Dockerfile.cv-service -t $AR/cv-service:latest ./cv-service
docker push $AR/cv-service:latest
docker build -f docker/Dockerfile.backend -t $AR/backend:latest ./backend
docker push $AR/backend:latest
```

---

## Step 2 — Deploy to Cloud Run

```bash
gcloud run deploy cv-service \
  --image $AR/cv-service:latest --region $GCP_REGION \
  --port 8001 --no-allow-unauthenticated \
  --min-instances 1 --max-instances 3 --memory 2Gi --cpu 1

CV_URL=$(gcloud run services describe cv-service --region $GCP_REGION --format "value(status.url)")

gcloud run deploy backend \
  --image $AR/backend:latest --region $GCP_REGION \
  --port 8000 --allow-unauthenticated \
  --min-instances 1 --max-instances 5 --memory 1Gi --cpu 1 \
  --set-env-vars CV_SERVICE_URL=$CV_URL
```

---

## Option B — Use Vertex AI Gemini Vision

```python
import vertexai
from vertexai.generative_models import GenerativeModel, Part
import base64, json

vertexai.init(project="posedetect-cv-project", location="europe-west2")
gemini = GenerativeModel("gemini-pro-vision")

def analyze_pose(image_bytes: bytes) -> dict:
    image_part = Part.from_data(data=image_bytes, mime_type="image/jpeg")
    response = gemini.generate_content([
        image_part,
        "Analyze this fitness image. Return JSON: {exercise, joint_angles: {left_knee, right_knee, left_elbow, right_elbow}, feedback: [], score: 0-100}"
    ])
    return json.loads(response.text)
```

---

## Estimated Monthly Cost

| Service                    | Tier                  | Est. Cost          |
|----------------------------|-----------------------|--------------------|
| Cloud Run (backend)        | 1 vCPU / 1 GB         | ~$10–15/month      |
| Cloud Run (cv-service)     | 1 vCPU / 2 GB         | ~$12–18/month      |
| Artifact Registry          | Storage               | ~$1–2/month        |
| Firebase Hosting           | Free tier             | $0                 |
| Vertex AI Gemini Vision    | Pay per token         | ~$5–15/month       |
| **Total (Option A)**       |                       | **~$23–35/month**  |
| **Total (Option B)**       |                       | **~$18–33/month**  |

For exact estimates → https://cloud.google.com/products/calculator

---

## Teardown

```bash
gcloud run services delete backend --region $GCP_REGION --quiet
gcloud run services delete cv-service --region $GCP_REGION --quiet
gcloud artifacts repositories delete posedetect-repo --location=$GCP_REGION --quiet
gcloud projects delete posedetect-cv-project
```
