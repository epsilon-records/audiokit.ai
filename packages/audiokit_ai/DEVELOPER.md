# **AudioKit-AI Developer Guide** 🛠️

Welcome to the **AudioKit-AI** project! This guide will help you set up your development environment, run tests, and contribute to the project.

---

## **Table of Contents**
1. [Prerequisites](#prerequisites)
2. [Setting Up the Development Environment](#setting-up-the-development-environment)
3. [Running the Application](#running-the-application)
4. [Running Tests](#running-tests)
5. [Contributing](#contributing)
6. [Logging](#logging)
7. [Docker Setup](#docker-setup)
8. [Troubleshooting](#troubleshooting)

---

## **Prerequisites** 📋

Before you begin, ensure you have the following installed:

- **Python 3.11** 🐍
- **Docker** 🐳 (optional, for containerized development)
- **Git** 📂
- **Hatch** 🐣 (Python build and project management tool)

---

## **Setting Up the Development Environment** 🏗️

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/your-username/audiokit-ai.git
   cd audiokit-ai
   ```

2. **Install Dependencies:**
   ```bash
   pip install hatch
   hatch env create
   ```

3. **Set Up Environment Variables:**
   Create a `.env` file in the root directory and add the following:
   ```env
   GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json
   REDIS_HOST=localhost
   REDIS_PORT=6379
   JWT_SECRET=supersecretkey
   JWT_ALGORITHM=HS256
   ```

---

## **Running the Application** 🚀

To run the FastAPI server locally:

```bash
hatch run uvicorn audiokit_ai.main:app --host 0.0.0.0 --port 8000 --reload
```

Visit `http://localhost:8000/docs` to access the Swagger UI.

---

## **Running Tests** 🧪

To run the test suite:

```bash
hatch run test:pytest
```

For verbose output and coverage reports:

```bash
hatch run test:pytest -v --cov=audiokit_ai --cov-report=term-missing
```

---

## **Contributing** 🤝

We welcome contributions! Here's how to get started:

1. **Fork the Repository:**  
   Fork the repository to your GitHub account.

2. **Create a Branch:**  
   Create a new branch for your feature or bug fix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Commit Your Changes:**  
   Make your changes and commit them with a descriptive message:
   ```bash
   git commit -m "Add your feature or fix"
   ```

4. **Push Your Changes:**  
   Push your changes to your forked repository:
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Create a Pull Request:**  
   Open a pull request from your branch to the `main` branch of the original repository.

---

## **Logging** 📝

We use **Loguru** for structured and emoji-based logging. Here's an example of how to use it:

```python
from audiokit_ai.core.logger import logger

logger.info("This is an info message ℹ️")
logger.error("This is an error message ❌")
```

---

## **Docker Setup** 🐳

To build and run the project in Docker:

1. **Build the Docker Image:**
   ```bash
   docker build -f docker/Dockerfile -t audiokit_ai .
   ```

2. **Run the Container:**
   ```bash
   docker run --rm -p 8000:8000 audiokit_ai
   ```

---

## **Troubleshooting** 🔧

### **1. Missing Dependencies**
If you encounter missing dependencies, ensure you've installed all required packages:
```bash
pip install -e ".[test]"
```

### **2. Google Cloud Credentials**
If you see errors related to Google Cloud credentials, ensure the `GOOGLE_APPLICATION_CREDENTIALS` environment variable is set correctly.

### **3. Redis Connection Issues**
If Redis isn't running, start it with:
```bash
docker run --rm -p 6379:6379 redis
```

---

## **Happy Coding!** 🎉
We're excited to have you on board. If you have any questions, feel free to reach out or open an issue in the repository.