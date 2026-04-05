# AWS Deployment Guide — Project CV-07 Pose Detection Fitness Trainer

---

## AWS Services for Pose Detection

### 1. Ready-to-Use AI (No Model Needed)

| Service                    | What it does                                                                 | When to use                                        |
|----------------------------|------------------------------------------------------------------------------|----------------------------------------------------|
| **Amazon Rekognition**     | Detect body parts and pose keypoints from images                             | Replace your MediaPipe Pose pipeline               |
| **AWS HealthLake**         | Store and analyze fitness/health data from pose sessions                     | When you need persistent health data storage       |
| **Amazon Bedrock**         | Claude Vision for fitness form analysis and coaching feedback via prompt     | When you need AI-generated fitness coaching        |

> **Amazon Rekognition DetectProtectiveEquipment / body parts** combined with **Amazon Bedrock** for coaching feedback replaces your MediaPipe + rule-based feedback pipeline.

### 2. Host Your Own Model (Keep Current Stack)

| Service                    | What it does                                                        | When to use                                           |
|----------------------------|---------------------------------------------------------------------|-------------------------------------------------------|
| **AWS App Runner**         | Run backend container — simplest, no VPC or cluster needed          | Quickest path to production                           |
| **Amazon ECS Fargate**     | Run backend + cv-service containers in a private VPC                | Best match for your current microservice architecture |
| **Amazon ECR**             | Store your Docker images                                            | Used with App Runner, ECS, or EKS                     |

### 3. Frontend Hosting

| Service               | What it does                                                                  |
|-----------------------|-------------------------------------------------------------------------------|
| **Amazon S3**         | Host your React build as a static website                                     |
| **Amazon CloudFront** | CDN in front of S3 — HTTPS, low latency globally                              |

### 4. Supporting Services

| Service                  | Purpose                                                                   |
|--------------------------|---------------------------------------------------------------------------|
| **Amazon S3**            | Store uploaded images and pose analysis results                           |
| **AWS Secrets Manager**  | Store API keys and connection strings instead of .env files               |
| **Amazon CloudWatch**    | Track detection latency, joint angle distributions, request volume        |

---

## Recommended Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  S3 + CloudFront — React Frontend                           │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTPS
┌──────────────────────▼──────────────────────────────────────┐
│  AWS App Runner / ECS Fargate — Backend (FastAPI :8000)     │
└──────────────────────┬──────────────────────────────────────┘
                       │ Internal
        ┌──────────────┴──────────────┐
        │ Option A                    │ Option B
        ▼                             ▼
┌───────────────────┐    ┌────────────────────────────────────┐
│ ECS Fargate       │    │ Amazon Rekognition                 │
│ CV Service :8001  │    │ + Amazon Bedrock (coaching)        │
│ MediaPipe Pose    │    │ No model download needed           │
└───────────────────┘    └────────────────────────────────────┘
```

---

## Prerequisites

```bash
aws configure
AWS_REGION=eu-west-2
AWS_ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
```

---

## Step 1 — Create ECR and Push Images

```bash
aws ecr create-repository --repository-name posedetect/cv-service --region $AWS_REGION
aws ecr create-repository --repository-name posedetect/backend --region $AWS_REGION
ECR=$AWS_ACCOUNT.dkr.ecr.$AWS_REGION.amazonaws.com
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR
docker build -f docker/Dockerfile.cv-service -t $ECR/posedetect/cv-service:latest ./cv-service
docker push $ECR/posedetect/cv-service:latest
docker build -f docker/Dockerfile.backend -t $ECR/posedetect/backend:latest ./backend
docker push $ECR/posedetect/backend:latest
```

---

## Step 2 — Deploy with App Runner

```bash
aws apprunner create-service \
  --service-name posedetect-backend \
  --source-configuration '{
    "ImageRepository": {
      "ImageIdentifier": "'$ECR'/posedetect/backend:latest",
      "ImageRepositoryType": "ECR",
      "ImageConfiguration": {
        "Port": "8000",
        "RuntimeEnvironmentVariables": {
          "CV_SERVICE_URL": "http://cv-service:8001"
        }
      }
    }
  }' \
  --instance-configuration '{"Cpu": "1 vCPU", "Memory": "2 GB"}' \
  --region $AWS_REGION
```

---

## Option B — Use Amazon Bedrock for Fitness Coaching

```python
import boto3, json, base64

bedrock = boto3.client("bedrock-runtime", region_name="eu-west-2")

def analyze_pose(image_bytes: bytes) -> dict:
    image_b64 = base64.b64encode(image_bytes).decode()
    prompt = """Analyze this fitness/exercise image. Return JSON:
{
  "exercise": "detected exercise name",
  "joint_angles": {"left_knee": 0, "right_knee": 0, "left_elbow": 0, "right_elbow": 0},
  "feedback": ["list of form corrections"],
  "score": 0-100
}"""
    response = bedrock.invoke_model(
        modelId="anthropic.claude-3-sonnet-20240229-v1:0",
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 500,
            "messages": [{"role": "user", "content": [
                {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": image_b64}},
                {"type": "text", "text": prompt}
            ]}]
        }),
        contentType="application/json"
    )
    return json.loads(json.loads(response["body"].read())["content"][0]["text"])
```

---

## Estimated Monthly Cost

| Service                    | Tier              | Est. Cost          |
|----------------------------|-------------------|--------------------|
| App Runner (backend)       | 1 vCPU / 2 GB     | ~$20–25/month      |
| App Runner (cv-service)    | 1 vCPU / 2 GB     | ~$20–25/month      |
| ECR + S3 + CloudFront      | Standard          | ~$3–7/month        |
| Amazon Bedrock (Claude)    | Pay per token     | ~$5–15/month       |
| **Total (Option A)**       |                   | **~$43–57/month**  |
| **Total (Option B)**       |                   | **~$28–47/month**  |

For exact estimates → https://calculator.aws

---

## Teardown

```bash
aws ecr delete-repository --repository-name posedetect/backend --force
aws ecr delete-repository --repository-name posedetect/cv-service --force
```
