### **Prompt for o3-mini-high: AudioKit-AI Server**  
**Objective:** Generate the **entire backend codebase** for **AudioKit-AI Server**, implementing all features, CI/CD, cloud infrastructure, and API services based on the provided technical documentation.

---

## **System Instruction**  
You are an advanced AI coding assistant specialized in building high-performance, production-grade software. Your task is to generate the **complete backend codebase** for **AudioKit-AI Server**, an **AI-powered audio processing service**.  

The backend must be **modular, scalable, and secure**, implementing all described **features, infrastructure, CI/CD pipelines, and optimizations**.

---

## **1️⃣ Core Backend Specifications**
- **Framework:** `FastAPI`
- **Programming Language:** `Python 3.11`
- **Model Serving:** `NVIDIA Triton Server`, `ONNX Runtime`, `TensorRT`
- **Storage:**
  - **PostgreSQL** for metadata & job history
  - **MinIO/S3** for storing audio files
- **Queue Processing:** `Celery` with `Redis`
- **Rate Limiting & Security:** `FastAPI-Limiter`, `JWT Authentication`
- **Deployment Strategy:** `Docker + Kubernetes (GKE) with Helm & Terraform`
- **CI/CD Pipeline:** `GitHub Actions` automating linting, testing, packaging, and deployment
- **Cloud Provider:** `Google Cloud Platform (GCP)`
- **Infrastructure as Code:** `Terraform`
- **Autoscaling & Load Balancing:** `GKE + HPA`
- **Monitoring & Logging:** `Prometheus + Grafana`

---

## **2️⃣ Features to Implement**
### **AI-Powered Audio Processing**
✅ **Noise Reduction (`ak.denoise()`)** – DeepFilterNet-based  
✅ **Source Separation (`ak.separate()`)** – Demucs-based  
✅ **Audio Mastering (`ak.auto_master()`)** – DSPNet + U-Net  
✅ **Speech Transcription (`ak.transcribe()`)** – OpenAI Whisper  
✅ **Voice Cloning (`ak.clone_voice()`)** – Tacotron2 + VITS  
✅ **MIDI-to-Audio (`ak.midi_to_audio()`)** – DDSP  
✅ **Music Generation (`ak.generate_music()`)** – Riffusion + Jukebox  
✅ **Audio Search (`ak.search_by_sound()`)** – FAISS + OpenL3  
✅ **Audio Fingerprinting (`ak.identify_song()`)**  
✅ **Genre Classification (`ak.detect_genre()`)**  

---

## **3️⃣ API & SDK Integration**
- **FastAPI-based REST API**
- **gRPC Support for High-Performance Calls**
- **Authentication via API Keys & JWT Tokens**
- **WebSockets for Real-Time Audio Streaming Processing**
- **Swagger/OpenAPI Documentation**
- **Rate Limiting using Redis**
- **Caching with Redis for Faster Responses**

---

## **4️⃣ CI/CD & Deployment**
### **CI/CD Automation**
- **GitHub Actions Workflow:**
  - ✅ Linting with `ruff`
  - ✅ Unit Testing with `pytest`
  - ✅ Packaging & Publishing `audiokit-ai-server` to PyPI
  - ✅ Building & Pushing Docker Images to DockerHub
  - ✅ Deploying Helm Charts to GKE

### **Kubernetes Deployment on GKE**
- **Helm Chart (`audiokit-ai-helm/`)**
- **Kubernetes `deployment.yaml` & `service.yaml`**
- **Horizontal Pod Autoscaler (HPA) for Auto-Scaling**
- **Cloud Load Balancer for Traffic Management**

### **Terraform Infrastructure Management**
- **Deploys Compute Instances with NVIDIA GPUs**
- **Creates GKE Cluster with Auto-Scaling**
- **Provisioned Cloud Storage (`GCS`) for Audio Files**
- **Configures Load Balancer & VPC for Network Security**

---

## **5️⃣ Security & Monitoring**
- **Rate Limiting with Redis**
- **API Authentication (JWT + API Keys)**
- **Log Aggregation with `kubectl logs`**
- **Prometheus Metrics + Grafana Dashboards**
- **Role-Based Access Control (RBAC) in GKE**
- **Secure Secrets Management with Kubernetes Secrets**

---

## **6️⃣ Expected Output**
1. **Complete Python Codebase** implementing all backend logic.
2. **Helm Chart for Kubernetes Deployment**.
3. **Terraform Scripts for Infrastructure Setup**.
4. **GitHub Actions Workflow YAML** for CI/CD.
5. **Fully Functional REST API with Swagger UI**.
6. **Unit & Integration Tests for all Features**.

---

## **7️⃣ Additional Requirements**
- Ensure **modular and scalable architecture** for future feature expansion.
- Follow **best practices for security, logging, and performance optimization**.
- Implement **exception handling and graceful error management**.
- Provide **comprehensive API documentation**.
- Ensure **comprehensive test coverage (unit & integration tests)**.

---

### **🚀 Generate the full AudioKit-AI backend codebase, ensuring modularity, scalability, and security while implementing all described features and infrastructure.**