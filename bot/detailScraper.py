import httpx
import asyncio
import numpy as np
import bizscraper
import math
from selectolax.parser import HTMLParser
import config

def split_urls_into_batches(list_of_urls: list):
    splits = np.array_split(list_of_urls, math.ceil(len(list_of_urls)/2))
    return splits

async def log_response(response: httpx.Response):
    print(f'Response url: {response.url} | Status: {response.status_code}')
    
async def log_requests(resquest: httpx.Request):
    print(f'Request url: {resquest.url}')
    
logger = {"response": [log_response], "request": [log_requests]}

async def make_request(url: str, db: bizscraper.DB):
    async with httpx.AsyncClient(timeout=None, event_hooks=logger) as client:
        payload = {
            'api_key': config.scraper_api, 
            'url': url}
        response = await client.get("https://api.scraperapi.com/", params=payload)
        if response.status_code == 200:
            soup = HTMLParser(response.text)
            info = await bizscraper.parse_buis_detail_page(soup)
            db.buis_infos.append(info)
        
async def engine(urls: list, db: bizscraper.DB):
    batches = split_urls_into_batches(urls)
    for batch in list(batches):
        tasks = []
        for url in batch:
            tasks.append(
                make_request(url, db)
            )
        await asyncio.gather(*tasks)
        