"""System monitoring functionality for AudioKit."""
from datetime import datetime
import psutil
from typing import Dict

_start_time = datetime.now()

def get_uptime() -> str:
    """Get service uptime as formatted string."""
    uptime = datetime.now() - _start_time
    hours = int(uptime.total_seconds() // 3600)
    minutes = int((uptime.total_seconds() % 3600) // 60)
    return f"{hours}h {minutes}m"

def check_database_health() -> str:
    """Check database connection health."""
    # TODO: Implement actual database health check
    return "healthy"

def check_storage_health() -> str:
    """Check storage system health."""
    try:
        disk = psutil.disk_usage('/')
        if disk.percent < 90:  # Less than 90% full
            return "healthy"
        return "warning: disk space low"
    except Exception:
        return "error: unable to check storage"

def get_system_metrics() -> Dict[str, float]:
    """Get system resource metrics."""
    return {
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage('/').percent
    } 