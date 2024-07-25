from nicegui import ui
from model import Buisness, Saved
import sys
import os
current_dir = os.getcwd()
sys.path.append(f'{current_dir}/pages')
sys.path.append(f'{current_dir}/bot')
from pages import home, login_page, helper_page as hp
from bot import bizscraper
import asyncio

async def test_app():
    await bizscraper.main()
    print("Scraping DONE!")

@ui.page('/')
async def home_page():
    if hp.is_still_login():
        home_p = home.BuisnessPage(Buisness, 'All Buisness')
        home_p.header()
        await home_p.main()
        with ui.footer(fixed=False).classes('bg-zinc-700'):
            ui.label("Footer")
    else:
        ui.navigate.to('/login')

@ui.page('/saves')
async def saves_page():
    if hp.is_still_login():
        home_p = home.BuisnessPage(Saved, 'All Saved')
        home_p.header()
        await home_p.main()
        with ui.footer(fixed=False).classes('bg-zinc-700'):
            ui.label("Footer")
    else:
        ui.navigate.to('/login')
        
@ui.page('/login')
def the_login_page():
    lp = login_page.Login_Page()
    lp.main()
        
if len(sys.argv) > 1:
    asyncio.run(test_app())
else:
    ui.run(port=4000, title='DataViz', favicon="🌐", reconnect_timeout=60, storage_secret='tester')