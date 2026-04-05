# Azure Deployment Guide — Project CV-07 Pose Detection Fitness Trainer

---

## Azure Services for Pose Detection

### 1. Ready-to-Use AI (No Model Needed)

| Service                              | What it does                                                                 | When to use                                        |
|--------------------------------------|------------------------------------------------------------------------------|----------------------------------------------------|
| **Azure AI Vision — Pose Estimation**| Detect body keypoints and skeleton from images                               | Replace your MediaPipe Pose pipeline               |
| **Azure OpenAI Vision**              | GPT-4V for fitness form analysis and coaching feedback via prompt            | When you need AI-generated fitness coaching        |
| **Azure AI Video Indexer**           | Analyze video for pose and activity recognition                              | When you need video-based pose analysis            |

> **Azure AI Vision Pose Estimation + Azure OpenAI** replace your MediaPipe + rule-based feedback pipeline with managed services.

### 2. Host Your Own Model (Keep Current Stack)

| Service                        | What it does                                                        | When to use                                           |
|--------------------------------|---------------------------------------------------------------------|-------------------------------------------------------|
| **Azure Container Apps**       | Run your 3 Docker containers (frontend, backend, cv-service)        | Best match for your current microservice architecture |
| **Azure Container Registry**   | Store your Docker images                                            | Used with Container Apps or AKS                       |

### 3. Frontend Hosting

| Service                   | What it does                                                               |
|---------------------------|----------------------------------------------------------------------------|
| **Azure Static Web Apps** | Host your React frontend — free tier available, auto CI/CD from GitHub     |

### 4. Supporting Services

| Service                       | Purpose                                                                  |
|-------------------------------|--------------------------------------------------------------------------|
| **Azure Blob Storage**        | Store uploaded images and pose analysis results                          |
| **Azure Key Vault**           | Store API keys and connection strings instead of .env files              |
| **Azure Monitor + App Insights** | Track detection latency, joint angle distributions, request volume   |

---

## Recommended Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Azure Static Web Apps — React Frontend                     │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTPS
┌──────────────────────▼──────────────────────────────────────┐
│  Azure Container Apps — Backend (FastAPI :8000)             │
└──────────────────────┬──────────────────────────────────────┘
                       │ Internal
        ┌──────────────┴──────────────┐
        │ Option A                    │ Option B
        ▼                             ▼
┌───────────────────┐    ┌────────────────────────────────────┐
│ Container Apps    │    │ Azure AI Vision Pose Estimation    │
│ CV Service :8001  │    │ + Azure OpenAI (coaching)          │
│ MediaPipe Pose    │    │ No model download needed           │
└───────────────────┘    └────────────────────────────────────┘
```

---

## Prerequisites

```bash
az login
az group create --name rg-pose-detection --location uksouth
az extension add --name containerapp --upgrade
```

---

## Step 1 — Create Container Registry and Push Images

```bash
az acr create --resource-group rg-pose-detection --name posedetectacr --sku Basic --admin-enabled true
az acr login --name posedetectacr
ACR=posedetectacr.azurecr.io
docker build -f docker/Dockerfile.cv-service -t $ACR/cv-service:latest ./cv-service
docker push $ACR/cv-service:latest
docker build -f docker/Dockerfile.backend -t $ACR/backend:latest ./backend
docker push $ACR/backend:latest
```

---

## Step 2 — Deploy Container Apps

```bash
az containerapp env create --name posedetect-env --resource-group rg-pose-detection --location uksouth

az containerapp create \
  --name cv-service --resource-group rg-pose-detection \
  --environment posedetect-env --image $ACR/cv-service:latest \
  --registry-server $ACR --target-port 8001 --ingress internal \
  --min-replicas 1 --max-replicas 3 --cpu 1 --memory 2.0Gi

az containerapp create \
  --name backend --resource-group rg-pose-detection \
  --environment posedetect-env --image $ACR/backend:latest \
  --registry-server $ACR --target-port 8000 --ingress external \
  --min-replicas 1 --max-replicas 5 --cpu 0.5 --memory 1.0Gi \
  --env-vars CV_SERVICE_URL=http://cv-service:8001
```

---

## Option B — Use Azure OpenAI Vision for Fitness Coaching

```python
from openai import AzureOpenAI
import base64, json

client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    api_version="2024-02-01"
)

def analyze_pose(image_bytes: bytes) -> dict:
    image_b64 = base64.b64encode(image_bytes).decode()
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": [
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}},
            {"type": "text", "text": "Analyze this fitness image. Return JSON: {exercise, joint_angles: {left_knee, right_knee, left_elbow, right_elbow}, feedback: [], score: 0-100}"}
        ]}]
    )
    return json.loads(response.choices[0].message.content)
```

---

## Estimated Monthly Cost

| Service                  | Tier      | Est. Cost          |
|--------------------------|-----------|--------------------|
| Container Apps (backend) | 0.5 vCPU  | ~$10–15/month      |
| Container Apps (cv-svc)  | 1 vCPU    | ~$15–20/month      |
| Container Registry       | Basic     | ~$5/month          |
| Static Web Apps          | Free      | $0                 |
| Azure OpenAI (GPT-4o)    | Pay per token | ~$5–15/month   |
| **Total (Option A)**     |           | **~$30–40/month**  |
| **Total (Option B)**     |           | **~$20–35/month**  |

For exact estimates → https://calculator.azure.com

---

## Teardown

```bash
az group delete --name rg-pose-detection --yes --no-wait
```
