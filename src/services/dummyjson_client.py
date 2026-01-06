import requests

BASE_URL = "https://dummyjson.com"

def fetch_product(product_id: int) -> dict:
    r = requests.get(f"{BASE_URL}/products/{product_id}", timeout=15)
    r.raise_for_status()
    return r.json()
