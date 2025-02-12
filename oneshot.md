# AudioKit MCP Server v2.0 - One-Shot Codebase Generation

## Objective

Generate the complete backend codebase for **AudioKit MCP Server v2.0**, implementing all features, architecture, and infrastructure based on the provided technical specifications.

---

## Core Specifications

### Technology Stack

- **Framework:** FastAPI
- **Language:** Python 3.11
- **Vector Store:** Pinecone
- **LLM Integration:** OpenRouter
- **Storage:**
  - PostgreSQL for metadata
  - MinIO/S3 for audio files
- **Queue Processing:** Celery + Redis
- **Security:** JWT Authentication, Rate Limiting
- **Deployment:** Docker + Kubernetes (GKE)
- **CI/CD:** GitHub Actions
- **Monitoring:** Prometheus + Grafana

---

## Key Features

### Core Functionality

- Real-time music analytics
- Audio processing pipeline
- Natural language query system
- Unified data ingestion
- Comprehensive metadata management

### AI-Powered Features

- Audio similarity search (FAISS + OpenL3)
- Audio fingerprinting
- Genre classification
- Trend analysis

---

## Architecture Requirements

### Modular Design

- Clear separation of concerns
- Independent, testable modules
- Well-defined interfaces
- Dependency injection

### Pipeline Architecture

1. **Ingestion Pipeline**
   - Audio metadata
   - Text documents
   - File processing
2. **Processing Pipeline**
   - Audio conversion
   - Metadata extraction
   - Feature extraction
3. **Query Pipeline**
   - Natural language processing
   - Vector search
   - Result aggregation
4. **Monitoring Pipeline**
   - Performance metrics
   - Error tracking
   - Health checks

### Error Handling

- Comprehensive error handling
- Detailed error logging
- Graceful degradation
- Automatic retries

---

## OpenRouter Integration

### Key Features

- Support for multiple models (Claude-3.5-Sonnet, GPT-4-Turbo, Llama-3-70b)
- Automatic fallback to alternative models
- Rate limit handling
- Cost tracking
- Response caching

### Configuration

- Centralized configuration management
- Environment variable support
- Model selection via API
- Customizable timeout and retry settings

---

## Implementation Requirements

### Code Quality

- Type hints for all functions
- Comprehensive docstrings
- Unit tests with 90%+ coverage
- Integration tests for all endpoints
- Linting and formatting with black/isort

### Documentation

- API documentation with Swagger/OpenAPI
- Architecture documentation
- Deployment guide
- Developer onboarding guide

### Performance

- Optimized for low-latency responses
- Efficient resource utilization
- Scalable for high-volume requests

### Security

- Comprehensive input validation
- Secure authentication and authorization
- Data encryption at rest and in transit
- Regular security audits

---

## Deliverables

1. Complete backend codebase
2. Dockerfiles and Kubernetes manifests
3. Terraform infrastructure as code
4. CI/CD pipeline configuration
5. Comprehensive documentation
6. Test suite with high coverage

## Codebase Structure

audiokit_mcp_server/
├── core/
│ ├── config.py
│ ├── logger.py
│ └── utils.py
├── handlers/
│ ├── ingestion/
│ │ ├── audio_ingestor.py
│ │ ├── text_ingestor.py
│ │ └── file_ingestor.py
│ ├── query/
│ │ ├── query_handler.py
│ │ └── search_handler.py
│ ├── processing/
│ │ ├── audio_processor.py
│ │ └── metadata_extractor.py
│ └── storage/
│ ├── vector_store.py
│ └── document_store.py
├── models/
│ ├── audio.py
│ ├── metadata.py
│ └── query.py
├── services/
│ ├── llm_service.py
│ ├── embedding_service.py
│ └── indexing_service.py
├── pipelines/
│ ├── ingestion_pipeline.py
│ ├── processing_pipeline.py
│ └── query_pipeline.py
└── main.py

---

## Implementation Requirements

### Code Quality

- Type hints for all functions
- Comprehensive docstrings
- Unit tests with 90%+ coverage
- Integration tests for all endpoints
- Linting and formatting with black/isort

### Documentation

- API documentation with Swagger/OpenAPI
- Architecture documentation
- Deployment guide
- Developer onboarding guide

### Performance

- Optimized for low-latency responses
- Efficient resource utilization
- Scalable for high-volume requests

### Security

- Comprehensive input validation
- Secure authentication and authorization
- Data encryption at rest and in transit
- Regular security audits

---

## Deliverables

1. Complete backend codebase
2. Dockerfiles and Kubernetes manifests
3. Terraform infrastructure as code
4. CI/CD pipeline configuration
5. Comprehensive documentation
6. Test suite with high coverage
