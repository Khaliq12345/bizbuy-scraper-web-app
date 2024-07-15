import httpx, detailScraper
import pandas as pd
from selectolax.parser import HTMLParser
from urllib.parse import urljoin
import uuid
import hashlib
from b_model import Buisness
import json
from sqlalchemy import create_engine
import config

class DB:
    buis_links = []
    buis_infos = []
    is_next = True

#save data------------
def save_data(buis_infos):
    try:
        df = pd.DataFrame(buis_infos)
        engine = create_engine(
           config.db_sync_url,
        )
        with engine.begin() as conn:
            df.to_sql(
                name='orig',
                con=conn, index=False, if_exists='replace'
            )
            print("Save DONE!")
    except Exception as e:
        print(e)
        
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

async def parse_buis_detail_page(soup: HTMLParser):
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
    info = {
        'buis_id': create_uuid_from_string(name).hex,
        'name': name,
        'location': 'Colorado',
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
    }
    b_data = json.loads(Buisness(**info).model_dump_json())
    return b_data

#making requests------------------------
def get_all_links(soup: HTMLParser):
    container = soup.css_first('#search-results')
    buises = container.css('.ng-star-inserted')
    b_links = []
    for buis in buises:
        try:
            b_link = buis.css_first('a').attributes['href']
            if ('Business-Opportunity' in b_link) or ("Business-Real-Estate-For-Sale" in b_link) or ("Start-Up-Business" in b_link):
                b_link = urljoin('https://www.bizbuysell.com/', b_link)
                b_links.append(b_link)
        except:
            pass
    return b_links

async def s_engine(page_num: int, db):
    print(f'Page: {page_num}')
    payload = { 'api_key': config.scraper_api, 'url': f'https://www.bizbuysell.com/colorado-businesses-for-sale/{page_num}' }
    async with httpx.AsyncClient(timeout=None) as client:
        r = await client.get('https://api.scraperapi.com/', params=payload, timeout=None)
        soup = HTMLParser(r.text)
        if not soup.css_matches('.bbsPager_next.ng-star-inserted'):
            db.is_next = False
        buis_links = get_all_links(soup)
        print(f'Total links: {len(buis_links)}')
        await detailScraper.engine(buis_links, db)

# async def main():
#     page_num = 28
#     while db.is_next:
#         await s_engine(page_num)
#         page_num += 1

#     t = Thread(target=save_data)
#     t.start()
#     print("DONE!")
        
# if __name__ == '__main__':
#     asyncio.run(main())

    

