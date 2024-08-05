import httpx
import asyncio
import numpy as np
import math
from selectolax.parser import HTMLParser
import config
import uuid
import hashlib
from b_model import Buisness
import json

#parsing data-----------------
def division_error(a, b):
    try:
        return round(a/b, 2)
    except ZeroDivisionError:
        return 0

def create_uuid_from_string(val: str):
    hex_string = hashlib.md5(val.encode("UTF-8")).hexdigest()
    return uuid.UUID(hex=hex_string)

def divide_chunks(l, n): 
    # looping till length l 
    for i in range(0, len(l), n):  
        yield l[i:i + n] 

def get_spec_info(specs: list[HTMLParser], info: str, default):
    for spec in specs:
        if spec.css_first('span.title').text() == info:
            value = spec.css_first('span.title').next.next.text(strip=True)
            try:
               return int(value.replace('$', '').replace(',', '').replace('*', ''))
            except:
                return value if value != 'N/A' else 0
    return default

def get_spec_from_dd(dds: list[HTMLParser], dts: list[HTMLParser], info:str, default):
    for idx, dt in enumerate(dts):
        if dt.text() == info:
            value = dds[idx].text(strip=True)
            try:
               return int(value.replace('$', '').replace(',', ''))
            except:
                return default
    return default

def parse_buis_detail_page(soup: HTMLParser, url: str, state: str):
    specs = soup.css('p.m-listing-row')
    dds, dts = soup.css('dd'), soup.css('dt')
    asking_price = get_spec_info(specs, 'Asking Price:', 0)
    if asking_price == 0:
        asking_price = get_spec_info(specs, 'Initial Fee:', 0)
    cash_flow = get_spec_info(specs, 'Cash Flow:', 0)
    gross_revenue = get_spec_info(specs, 'Gross Revenue:', 0)
    name = soup.css_first('h1').text(strip=True)
    ebitida = get_spec_info(specs, 'EBITDA:', 0)
    ff_e = get_spec_info(specs, 'FF&E:', 0)
    inventory = get_spec_info(specs, "Inventory:", 0)
    established = get_spec_info(specs, "Established:", 0)
    real_estate = get_spec_info(specs, 'Real Estate:', 0)
    employees = get_spec_from_dd(dds, dts, 'Employees:', 0)
    reason_for_selling = get_spec_from_dd(dds, dts, 'Reason for Selling:', 'Not available')
    seller_financing = 'yes' if soup.css_first('div[id="seller-financing"]') else 'no'
    cogs = get_spec_info(specs, 'COGS:', 0)
    profit_margin_orig = division_error(cash_flow, gross_revenue)
    gross_margin = division_error(cogs, gross_revenue)
    asking_multiple = division_error(asking_price, cash_flow)
    state = state.replace('-', ' ').title()
    info = {
        'buis_id': create_uuid_from_string(name).hex,
        'name': name,
        'location': state,
        'asking_price': asking_price,
        'cash_flow': cash_flow,
        'gross_revenue': gross_revenue,
        'ebitda': ebitida,
        'ff_e': ff_e,
        'inventory': inventory,
        'real_estate': real_estate,
        'established': established,
        'employees': employees,
        'reason_for_selling': reason_for_selling,
        'seller_financing_available': seller_financing,
        'cogs': cogs,
        'profit_margin_orig': profit_margin_orig,
        'gross_margin': gross_margin,
        'asking_multiple': asking_multiple,
        'buis_link': url
    }
    b_data = json.loads(Buisness(**info).model_dump_json())
    return b_data

def split_urls_into_batches(list_of_urls: list):
    split_num = math.ceil(len(list_of_urls)/2)
    split_num = split_num if split_num > 0 else 1
    splits = np.array_split(list_of_urls, split_num)
    return splits

async def log_response(response: httpx.Response):
    print(f'Response url: {response.url} | Status: {response.status_code}')
    
async def log_requests(resquest: httpx.Request):
    print(f'Request url: {resquest.url}')
    
logger = {"response": [log_response], "request": [log_requests]}

async def make_request(url: str, state, db):
    try:
        async with httpx.AsyncClient(timeout=None, event_hooks=logger) as client:
            payload = {
                'api_key': config.scraper_api, 
                'url': url}
            response = await client.get("https://api.scraperapi.com/", params=payload)
            if response.status_code == 200:
                soup = HTMLParser(response.text)
                info = parse_buis_detail_page(soup, url, state)
                db.buis_infos.append(info)
    except Exception as e:
        print(e)
        pass
        
async def engine(urls: list, state, db):
    batches = split_urls_into_batches(urls)
    for batch in list(batches):
        tasks = []
        for url in batch:
            tasks.append(
                make_request(url, state, db)
            )
        await asyncio.gather(*tasks)
        