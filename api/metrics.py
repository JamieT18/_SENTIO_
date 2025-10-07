"""
Prometheus metrics endpoint for advanced analytics
"""
from fastapi import APIRouter
from fastapi.responses import JSONResponse
import psutil
import time

router = APIRouter()

@router.get("/admin/metrics")
def get_metrics():
    # Simulate Prometheus metrics
    metrics = {
        "cpu_percent": psutil.cpu_percent(),
        "memory_used": psutil.virtual_memory().used,
        "memory_total": psutil.virtual_memory().total,
        "uptime": time.time() - psutil.boot_time(),
        "error_rate": 0.01,
        "request_latency": 0.2
    }
    return JSONResponse(metrics)
