import os
import sys
import time
import logging
import requests

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def wait_for_http_service(url, max_attempts=30, delay=2, headers=None):

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
    vllm_base = os.getenv("VLLM_URL", "http://vllm:8000")

    health_url = vllm_base.rstrip("/") + "/health" if "/v1" not in vllm_base else vllm_base.rsplit("/v1", 1)[0] + "/health"
    models_url = vllm_base.rstrip("/") + "/models" if vllm_base.endswith("/v1") else vllm_base.rstrip("/") + "/v1/models"

    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("VLLM_API_KEY")
    headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}

    if not wait_for_http_service(health_url, max_attempts=15, headers=headers):
        if not wait_for_http_service(models_url, max_attempts=15, headers=headers):
            logger.error("vLLM service failed to become ready")
            return False

    logger.info("vLLM service is ready")
    return True

def main():

    logger.info("Starting service dependency checks...")
    
    if not wait_for_vllm():
        logger.error("vLLM dependency check failed")
        sys.exit(1)
    
if __name__ == "__main__":
    main()