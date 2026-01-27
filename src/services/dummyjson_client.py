import requests
import logging

logger = logging.getLogger("price_monitor")
BASE_URL = "https://dummyjson.com"

def fetch_product(product_id: int) -> dict:
    logger.info("Запрашиваю данные по товару: %s", product_id)
    r = requests.get(f"{BASE_URL}/products/{product_id}", timeout=15)
    r.raise_for_status()
    logger.info("API ответ. product_id=%s status=%s", product_id, r.status_code)
    return r.json()
