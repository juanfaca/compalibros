import cloudscraper
import json
from bs4 import BeautifulSoup
import pandas as pd

id='116685'

scraper = cloudscraper.create_scraper(
    delay=10,
    browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False}
)

# URL de la API
api_url = "https://www.communitas.pe/sale/get_combination_info_website"

# Payload de la API
payload = {
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
        "product_template_id": 110947,
        "product_id": [id],
        "combination": [],#[784609, 784606, 784613, 784607, 784610, 832635, 784612, 784608, 784611],
        "parent_combination": [],
        "add_qty": 1,
        "pricelist_id": False
    },
    "id": 1
}

# Encabezados de la API
headers = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Referer": "https://www.communitas.pe/shop/"
}

response = scraper.post(api_url, headers=headers, data=json.dumps(payload))
resultado = response.content


print(resultado.content)