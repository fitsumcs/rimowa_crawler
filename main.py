import os
import uuid
import asyncio
import aiohttp
from pyppeteer import launch
from dotenv import load_dotenv
from scrapy.http import HtmlResponse
from algoliasearch.search_client import SearchClient
import httpx
import requests



# Load environment variables from .env file
load_dotenv()

# Get environment variables
RUB_URL = os.getenv("RUB_URL")
SCRAPER_BASE_URL = os.getenv("SCRAPER_BASE_URL")
ALGOLIA_APP_ID = os.getenv("ALGOLIA_APP_ID")
ALGOLIA_API_KEY = os.getenv("ALGOLIA_API_KEY")
ALGOLIA_INDEX_NAME = os.getenv("ALGOLIA_INDEX_NAME")
categories = os.getenv('CATEGORIES').split(',')


async def fetch_json(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json(), response.status

async def get_ruble_rate():
    data, status = await fetch_json(RUB_URL)
    if status == 200:
        return float(data.get("rates", {}).get("RUB", 0))
    else:
        return 0.0



async def fetch_page_content(url):
    try:
        response =  requests.get(url)
        if response.status_code == 200:
            return response.text, response.url
        else:
            print(f"Failed to fetch content from {url}. Status code: {response.status_code}")
            return "", None
    except Exception as e:
        print(f"An error occurred while fetching content from {url}: {e}")
        return "", None


def parse_product(product, ruble_rate):
    brand = "Rimowa"
    product_id = product.css('::attr(data-itemid)').get()
    product_title = product.css('.product-name::text').get()
    product_price = product.css('::attr(data-itemprice)').get()
    product_images = [
        {
            "url": 'https://www.rimowa.com' + img.css('::attr(src)').get(),
            "order": idx,
            "size": "1000"
        } for idx, img in enumerate(product.css('img'))
    ]
    product_category = product.css('::attr(data-itemcategory)').get()
    product_variants = [{
        "id": product.css('::attr(data-itemvariant)').get(),
        "size": product.css('::attr(data-itemvariant)').get(),
        "price": float(product_price.replace(',', '.')) * 1.2 * ruble_rate if product_price else None,
        "type": "Size"
    }]
    objectID = str(uuid.uuid4())
    product_data = {
        "id": product_id if product_id else None,
        "title": product_title.strip() if product_title else None,
        "price": float(product_price.replace(',', '.')) * 1.2 * ruble_rate if product_price else None,
        "category": product_category.split(' - ') if product_category else [],
        "currency": "RUB",
        "brand": {
            "id": brand.lower().replace(" ", "-"),
            "name": brand,
            "description": brand
        },
        "gender": ["unisex"],
        "slug": f"{brand.lower().replace(' ', '-')}-{brand}-{brand}-{objectID}",
        "images": product_images if product_images else [],
        "variants": product_variants if product_variants else [],
        "objectID": objectID
    }
    return product_data

def add_to_algolia(product_list):
    # Connect and authenticate with Algolia app
    client = SearchClient.create(ALGOLIA_APP_ID, ALGOLIA_API_KEY)
    index = client.init_index(ALGOLIA_INDEX_NAME)

    # Clear existing objects
    index.clear_objects().wait()

    # Add product list to Algolia index
    index.save_objects(product_list).wait()

async def main():
    product_list = []
    ruble_rate = await get_ruble_rate()

    for category in categories:
        category_url = f"{SCRAPER_BASE_URL}/all-{category}"
        page_content, _ = await fetch_page_content(category_url)

        if not page_content:
            continue

        response = HtmlResponse(url=category_url, body=page_content, encoding='utf-8')
        products = response.css('.grid-tile')

        for product in products:
            product_data = parse_product(product, ruble_rate)
            product_list.append(product_data)

    add_to_algolia(product_list)
    print("Products added to Algolia index.")

if __name__ == "__main__":
    asyncio.run(main())
