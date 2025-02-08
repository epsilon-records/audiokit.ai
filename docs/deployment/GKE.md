# **AudioKit-AI Server: Helm Chart for GKE Deployment**

## **Version:** 1.1
## **Date:** [Insert Date]
## **Prepared by:** AudioKit Team

---

# **I. Overview**
This document provides a **Helm chart configuration** for deploying **AudioKit-AI Server** on **Google Kubernetes Engine (GKE)**. Helm simplifies **scalable, repeatable, and configurable** deployments for Kubernetes environments and integrates with Terraform for **automated infrastructure provisioning**.

## **II. Why Use Helm for GKE?**
✅ **Automated Deployment & Scaling** – Simplifies configuration management.
✅ **Supports Rolling Updates** – Ensures zero-downtime upgrades.
✅ **Customizable via `values.yaml`** – Adaptable for different environments.
✅ **Load Balancer Integration** – Connects to GCP’s external traffic manager.
✅ **Terraform-Integrated Deployment** – Fully automated infrastructure creation.

---

# **III. Helm Chart Structure**
```
audiokit-ai-helm/
│── charts/
│── templates/
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   ├── configmap.yaml
│   ├── hpa.yaml
│── values.yaml
│── Chart.yaml
│── terraform/
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
```

---

# **IV. Helm Chart Configuration**

## **1️⃣ Define Helm Chart Metadata**
📌 **`Chart.yaml`**
```yaml
apiVersion: v2
name: audiokit-ai
version: 1.0.0
description: Helm chart for deploying AudioKit-AI Server on GKE
maintainers:
  - name: AudioKit Team
```

## **2️⃣ Configurable Values**
📌 **`values.yaml`**
```yaml
replicaCount: 2

image:
  repository: gcr.io/my-project/audiokit-ai-server
  tag: latest
  pullPolicy: Always

env:
  GCP_PROJECT: "my-audiokit-project"
  REGION: "us-central1"
  STORAGE_BUCKET: "audiokit-ai-storage"

service:
  type: LoadBalancer
  port: 8080

resources:
  requests:
    cpu: "500m"
    memory: "1Gi"
  limits:
    cpu: "2000m"
    memory: "4Gi"
```

## **3️⃣ Kubernetes Deployment File**
📌 **`templates/deployment.yaml`**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Release.Name }}-server
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      app: audiokit-ai
  template:
    metadata:
      labels:
        app: audiokit-ai
    spec:
      containers:
      - name: audiokit-ai
        image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
        ports:
        - containerPort: 8080
        env:
        - name: GCP_PROJECT
          value: "{{ .Values.env.GCP_PROJECT }}"
        - name: STORAGE_BUCKET
          value: "{{ .Values.env.STORAGE_BUCKET }}"
```

## **4️⃣ Kubernetes Horizontal Pod Autoscaler (HPA)**
📌 **`templates/hpa.yaml`**
```yaml
apiVersion: autoscaling/v2beta2
kind: HorizontalPodAutoscaler
metadata:
  name: {{ .Release.Name }}-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: {{ .Release.Name }}-server
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 75
```

## **5️⃣ Terraform Automation Integration**
📌 **`terraform/main.tf`**
```hcl
provider "google" {
  project = var.project
  region  = var.region
}

resource "google_container_cluster" "gke" {
  name     = "audiokit-cluster"
  location = var.region
}
```

---

# **V. Deploying AudioKit-AI on GKE Using Helm & Terraform**

## **1. Install Helm & Terraform**
```bash
curl https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 | bash
brew install terraform
```

## **2. Initialize Terraform for GKE**
```bash
cd terraform/
terraform init
terraform apply -auto-approve
```

## **3. Deploy Helm Chart to GKE**
```bash
helm install audiokit-ai ./audiokit-ai-helm --set image.tag=latest
```

## **4. Verify Deployment**
```bash
kubectl get pods
kubectl get services
kubectl get hpa
```

## **5. Upgrade Deployment**
```bash
helm upgrade audiokit-ai ./audiokit-ai-helm --set image.tag=v1.1.0
```

## **6. Uninstall Helm Deployment**
```bash
helm uninstall audiokit-ai
terraform destroy -auto-approve
```

---

# **VI. Next Steps**
✅ **Integrate Helm Charts into CI/CD pipeline**.  
✅ **Enable auto-scaling with HPA**.  
✅ **Configure monitoring with Prometheus & Grafana**.  
✅ **Automate Terraform-managed Helm deployments for GKE**.  

