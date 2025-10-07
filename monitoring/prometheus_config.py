"""
Prometheus metrics config for Sentio
"""
from prometheus_client import start_http_server, Summary

REQUEST_TIME = Summary('request_processing_seconds', 'Time spent processing request')

def start_metrics_server(port=8001):
    start_http_server(port)
