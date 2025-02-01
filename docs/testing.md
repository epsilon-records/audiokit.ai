# API Testing Guide

## Overview

This guide outlines testing strategies and best practices for the AudioKit AI Platform API. It covers test environment setup, authentication testing, integration testing, performance testing, and security testing.

## Test Environment Setup

### 1. Environment Configuration

```bash
# .env.test
AUDIOKIT_API_URL=https://test-api.audiokit.ai
AUDIOKIT_TEST_TOKEN=test_token_xyz
AUDIOKIT_TEST_EMAIL=test@audiokit.ai
AUDIOKIT_TEST_PASSWORD=test_password
```

### 2. Test Database Setup

```python
from audiokit.db import TestDatabase

async def setup_test_db():
    db = TestDatabase()
    await db.create_tables()
    await db.seed_test_data()
    return db

async def teardown_test_db(db):
    await db.cleanup()
```

### 3. Mock Services

```python
from unittest.mock import AsyncMock
from audiokit.services import PlatformService

class MockPlatformService(PlatformService):
    async def fetch_data(self, platform: str) -> dict:
        return {
            "followers": 1000,
            "engagement": 5.2,
            "growth": 2.1
        }

def setup_mocks():
    return {
        "platform_service": MockPlatformService(),
        "cache_service": AsyncMock(),
        "analytics_service": AsyncMock()
    }
```

## Authentication Testing

### 1. Token Generation Tests

```python
import pytest
from httpx import AsyncClient
from audiokit.auth import generate_test_token

@pytest.mark.asyncio
async def test_token_generation():
    async with AsyncClient() as client:
        response = await client.post(
            "/auth/token",
            json={
                "email": "test@audiokit.ai",
                "password": "test_password"
            }
        )
        assert response.status_code == 200
        assert "access_token" in response.json()
        assert "token_type" in response.json()
```

### 2. Token Validation Tests

```python
@pytest.mark.asyncio
async def test_token_validation():
    token = generate_test_token()
    
    async with AsyncClient() as client:
        response = await client.get(
            "/brain/query",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200

        # Test invalid token
        response = await client.get(
            "/brain/query",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401
```

### 3. Permission Tests

```python
@pytest.mark.asyncio
async def test_permissions():
    # Admin token
    admin_token = generate_test_token(role="admin")
    # User token
    user_token = generate_test_token(role="user")
    
    async with AsyncClient() as client:
        # Test admin endpoint
        response = await client.get(
            "/admin/metrics",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        
        # Test with insufficient permissions
        response = await client.get(
            "/admin/metrics",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 403
```

## Integration Testing

### 1. Knowledge Base Tests

```python
@pytest.mark.integration
async def test_knowledge_base_flow():
    async with AsyncClient() as client:
        # 1. Upload document
        doc_response = await client.post(
            "/brain/documents",
            files={"file": ("test.txt", "test content")},
            data={"metadata": '{"type": "news"}'}
        )
        assert doc_response.status_code == 200
        doc_id = doc_response.json()["doc_id"]
        
        # 2. Query document
        query_response = await client.post(
            "/brain/query",
            json={"query": "test content"}
        )
        assert query_response.status_code == 200
        results = query_response.json()["results"]
        assert len(results) > 0
        
        # 3. Delete document
        delete_response = await client.delete(
            f"/brain/documents/{doc_id}"
        )
        assert delete_response.status_code == 200
```

### 2. Platform Integration Tests

```python
@pytest.mark.integration
async def test_platform_integration():
    async with AsyncClient() as client:
        # 1. Connect platform
        connect_response = await client.post(
            "/platforms/connect",
            json={
                "platform": "spotify",
                "credentials": {"access_token": "test_token"}
            }
        )
        assert connect_response.status_code == 200
        
        # 2. Fetch analytics
        analytics_response = await client.get(
            "/platforms/spotify/analytics"
        )
        assert analytics_response.status_code == 200
        data = analytics_response.json()
        assert "metrics" in data
```

### 3. End-to-End Flow Tests

```python
@pytest.mark.e2e
async def test_artist_workflow():
    async with AsyncClient() as client:
        # 1. Create artist profile
        profile = await client.post(
            "/artists",
            json={
                "name": "Test Artist",
                "email": "artist@test.com"
            }
        )
        assert profile.status_code == 200
        artist_id = profile.json()["id"]
        
        # 2. Connect platforms
        platforms = ["spotify", "instagram"]
        for platform in platforms:
            response = await client.post(
                f"/artists/{artist_id}/platforms",
                json={"platform": platform}
            )
            assert response.status_code == 200
        
        # 3. Generate content
        content = await client.post(
            f"/artists/{artist_id}/content/generate",
            json={"type": "social_post"}
        )
        assert content.status_code == 200
        
        # 4. Get analytics
        analytics = await client.get(
            f"/artists/{artist_id}/analytics"
        )
        assert analytics.status_code == 200
```

## Performance Testing

### 1. Load Testing

```python
import asyncio
from locust import HttpUser, task, between

class APIUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    async def query_knowledge_base(self):
        await self.client.post(
            "/brain/query",
            json={"query": "test query"}
        )
    
    @task
    async def get_analytics(self):
        await self.client.get("/analytics/overview")
```

### 2. Response Time Tests

```python
import time

@pytest.mark.performance
async def test_response_times():
    async with AsyncClient() as client:
        start_time = time.time()
        response = await client.post(
            "/brain/query",
            json={"query": "test"}
        )
        duration = time.time() - start_time
        
        assert response.status_code == 200
        assert duration < 0.5  # 500ms threshold
```

### 3. Rate Limit Tests

```python
@pytest.mark.performance
async def test_rate_limits():
    async with AsyncClient() as client:
        # Send requests at max rate
        tasks = []
        for _ in range(100):
            tasks.append(
                client.post(
                    "/brain/query",
                    json={"query": "test"}
                )
            )
        
        responses = await asyncio.gather(*tasks)
        rate_limited = [r for r in responses if r.status_code == 429]
        
        assert len(rate_limited) > 0
```

## Security Testing

### 1. Authentication Security

```python
@pytest.mark.security
async def test_auth_security():
    async with AsyncClient() as client:
        # Test SQL injection
        response = await client.post(
            "/auth/token",
            json={
                "email": "' OR '1'='1",
                "password": "password"
            }
        )
        assert response.status_code == 400
        
        # Test password complexity
        response = await client.post(
            "/auth/register",
            json={
                "email": "test@test.com",
                "password": "simple"
            }
        )
        assert response.status_code == 400
```

### 2. Input Validation Tests

```python
@pytest.mark.security
async def test_input_validation():
    async with AsyncClient() as client:
        # Test XSS payload
        response = await client.post(
            "/brain/query",
            json={"query": "<script>alert('xss')</script>"}
        )
        assert response.status_code == 400
        
        # Test large payload
        large_query = "x" * 1_000_000
        response = await client.post(
            "/brain/query",
            json={"query": large_query}
        )
        assert response.status_code == 400
```

### 3. Authorization Tests

```python
@pytest.mark.security
async def test_authorization():
    async with AsyncClient() as client:
        # Test path traversal
        response = await client.get(
            "/brain/documents/../../../etc/passwd"
        )
        assert response.status_code == 400
        
        # Test CORS
        response = await client.options(
            "/brain/query",
            headers={"Origin": "https://evil.com"}
        )
        assert response.status_code == 403
```

## Test Automation

### 1. GitHub Actions Workflow

```yaml
name: API Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements-test.txt
      
      - name: Run tests
        run: |
          pytest tests/ --junitxml=test-results.xml
          
      - name: Upload test results
        uses: actions/upload-artifact@v2
        with:
          name: test-results
          path: test-results.xml
```

### 2. Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: api-tests
        name: API Tests
        entry: pytest tests/api
        language: python
        types: [python]
        pass_filenames: false
```

### 3. Test Coverage

```ini
# pytest.ini
[pytest]
addopts = --cov=audiokit --cov-report=html --cov-fail-under=90
testpaths = tests
markers =
    integration: Integration tests
    performance: Performance tests
    security: Security tests
    e2e: End-to-end tests
```

## Best Practices

### 1. Test Organization

```python
# tests/conftest.py
import pytest
from audiokit.testing import TestClient

@pytest.fixture
async def api_client():
    async with TestClient() as client:
        yield client

@pytest.fixture
async def test_db():
    db = await setup_test_db()
    yield db
    await teardown_test_db(db)

@pytest.fixture
async def mock_services():
    return setup_mocks()
```

### 2. Test Data Management

```python
# tests/data/fixtures.py
from audiokit.testing import TestData

class TestFixtures:
    @staticmethod
    def create_test_artist():
        return {
            "name": "Test Artist",
            "email": "test@artist.com",
            "platforms": ["spotify", "instagram"]
        }
    
    @staticmethod
    def create_test_document():
        return {
            "content": "Test content",
            "metadata": {
                "type": "news",
                "source": "test"
            }
        }
```

### 3. Test Utilities

```python
# tests/utils.py
from typing import Any, Dict
import jwt

def generate_test_token(
    role: str = "user",
    expires_in: int = 3600
) -> str:
    payload = {
        "sub": "test_user",
        "role": role,
        "exp": int(time.time()) + expires_in
    }
    return jwt.encode(payload, "test_secret")

def compare_responses(
    actual: Dict[str, Any],
    expected: Dict[str, Any]
) -> bool:
    """Compare API responses ignoring volatile fields"""
    volatile_fields = ["id", "created_at", "updated_at"]
    return all(
        actual.get(k) == v
        for k, v in expected.items()
        if k not in volatile_fields
    )
``` 