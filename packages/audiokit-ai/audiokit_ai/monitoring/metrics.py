from prometheus_client import start_http_server, Counter, Gauge, Histogram
from prometheus_async.aio.web import start_metrics_app
from fastapi import APIRouter

metrics_router = APIRouter()

# Define metrics
REQUEST_COUNT = Counter(
    'audiokit_requests_total',
    'Total API requests',
    ['method', 'endpoint', 'status']
)

PROCESSING_TIME = Histogram(
    'audiokit_processing_seconds',
    'Audio processing time',
    ['operation']
)

ACTIVE_JOBS = Gauge(
    'audiokit_active_jobs',
    'Currently processing jobs'
)

@metrics_router.get('/metrics')
async def metrics_endpoint():
    """Prometheus metrics endpoint"""
    return await start_metrics_app()

def setup_metrics(config):
    """Initialize metrics server"""
    start_http_server(config.metrics_port)
    ACTIVE_JOBS.set(0) 