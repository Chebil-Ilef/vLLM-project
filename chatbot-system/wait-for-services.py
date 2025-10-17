#!/usr/bin/env python3

import os
import sys
import time
import logging
import requests
from urllib.parse import urlparse

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def wait_for_http_service(url, max_attempts=30, delay=2, headers=None):
    """Wait for an HTTP service to become available."""
    logger.info(f"Waiting for HTTP service at {url}")
    
    for attempt in range(1, max_attempts + 1):
        try:
            response = requests.get(url, timeout=5, headers=headers or {})
            if response.status_code < 500:  # Accept any non-server error response
                logger.info(f"HTTP service at {url} is ready (status: {response.status_code})")
                return True
        except requests.exceptions.RequestException as e:
            logger.debug(f"Attempt {attempt}/{max_attempts}: {e}")
        
        if attempt < max_attempts:
            logger.info(f"HTTP service not ready, retrying in {delay}s... ({attempt}/{max_attempts})")
            time.sleep(delay)
    
    logger.error(f"HTTP service at {url} failed to become ready after {max_attempts} attempts")
    return False

def wait_for_vllm():
    """Wait for vLLM service to be ready."""
    vllm_url = os.getenv("VLLM_URL", "http://vllm:8000")
    api_key = os.getenv("VLLM_API_KEY")
    
    # Prepare headers with API key if available
    headers = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    
    health_url = f"{vllm_url}/health"
    
    # First try health endpoint, fallback to models endpoint
    if not wait_for_http_service(health_url, max_attempts=15, headers=headers):
        models_url = f"{vllm_url}/v1/models"
        if not wait_for_http_service(models_url, max_attempts=15, headers=headers):
            logger.error("vLLM service failed to become ready")
            return False
    
    logger.info("vLLM service is ready")
    return True

def wait_for_neo4j():
    """Wait for Neo4j service to be ready."""
    neo4j_uri = os.getenv("NEO4J_URI", "bolt://neo4j:7687")
    parsed = urlparse(neo4j_uri)
    host = parsed.hostname
    port = parsed.port or 7687
    
    # Simple TCP connection test for Neo4j
    import socket
    
    logger.info(f"Waiting for Neo4j at {host}:{port}")
    
    for attempt in range(1, 31):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                logger.info("Neo4j service is ready")
                return True
        except Exception as e:
            logger.debug(f"Attempt {attempt}/30: {e}")
        
        if attempt < 30:
            logger.info(f"Neo4j not ready, retrying in 2s... ({attempt}/30)")
            time.sleep(2)
    
    logger.error("Neo4j service failed to become ready")
    return False

def main():
    """Wait for all required services."""
    logger.info("Starting service dependency checks...")
    
    # Wait for vLLM (required for main functionality)
    if not wait_for_vllm():
        logger.error("vLLM dependency check failed")
        sys.exit(1)
    
    # Wait for Neo4j (if needed)
    neo4j_uri = os.getenv("NEO4J_URI")
    if neo4j_uri:
        if not wait_for_neo4j():
            logger.warning("Neo4j dependency check failed - continuing anyway")
    
    logger.info("All dependency checks completed successfully")

if __name__ == "__main__":
    main()