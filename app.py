from nicegui import ui
from model import Buisness, Saved
import sys
import os
current_dir = os.getcwd()
sys.path.append(f'{current_dir}/pages')
sys.path.append(f'{current_dir}/bot')
from pages import home, updatesPage
from bot import bizscraper
import asyncio

async def test_app():
    await bizscraper.main()
    print("Scraping DONE!")

@ui.page('/')
async def home_page():
    home_p = home.BuisnessPage(Buisness, 'All Buisness')
    home_p.header()
    await home_p.main()
    with ui.footer(fixed=False).classes('bg-zinc-700'):
        ui.label("Footer")

@ui.page('/saves')
async def saves_page():
    home_p = home.BuisnessPage(Saved, 'All Saved')
    home_p.header()
    await home_p.main()
    with ui.footer(fixed=False).classes('bg-zinc-700'):
        ui.label("Footer")

@ui.page('/updates')
async def update_page():
    update_page = updatesPage.UpdatePage()
    await update_page.main()
        
if len(sys.argv) > 1:
    asyncio.run(test_app())
else:
    ui.run(port=4000, title='DataViz', favicon="🌐")