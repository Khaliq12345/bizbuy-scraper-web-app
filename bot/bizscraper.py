import httpx, detailScraper
import pandas as pd
from selectolax.parser import HTMLParser
from urllib.parse import urljoin
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

async def main():
    db = DB()
    page_num = 1
    while db.is_next:
        await s_engine(page_num, db)
        page_num += 1

    save_data(db.buis_infos)
        
# if __name__ == '__main__':
#     asyncio.run(main())

    

