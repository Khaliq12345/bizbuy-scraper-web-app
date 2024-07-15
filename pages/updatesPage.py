from nicegui import ui
from threading import Thread
from bot import bizscraper
import asyncio
from home import BuisnessPage
import pandas as pd
from sqlalchemy import create_engine
import config

class UpdatePage(BuisnessPage):
    def __init__(self):
        self.buis_links = []
        self.buis_infos = []
        self.is_next = True
        self.page_str = None
        self.page_num = 1
    
    def save_data(self, buis_infos):
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
                print("Data Saved!")
                self.spinner.visible = False
                self.page_str = f'Completed'
        except Exception as e:
            print(e)

    async def scraper(self, page_num):
        self.spinner.visible = True
        page_num = int(page_num)
        try:
            while self.is_next:
                print(f'Page: {page_num}')
                self.page_str = f'Page -> {page_num}'
                await bizscraper.s_engine(page_num, self)
                page_num += 1
                self.is_next = False
                await asyncio.sleep(2)

            t = Thread(target=self.save_data, args=(self.buis_infos,))
            t.start()
        except Exception as e:
            with self.update_page_body:
                ui.notification(
                f"""Error while scraping:
                Message: {e}""", type='negative', position='top', multi_line=True)
        finally:
            self.spinner.visible = False

    async def main(self):
        self.page_title = "Updates"
        self.header()
        with ui.row().classes('w-full justify-center') as self.update_page_body:
            with ui.card().props('flat bordered').classes('border-8'):
                with ui.card_section().classes('w-full'):
                    with ui.row().classes('w-full justify-center'):
                        ui.label("OPTIONS").classes('text-h5')
                with ui.card_actions().classes('w-full'):
                    with ui.row().classes('w-full justify-center'):
                        i = ui.number("Start Page Number", value=self.page_num).bind_value(
                            target_object=self, target_name='page_num'
                        )
                with ui.card_actions().classes('w-full'):
                    with ui.row().classes('justify-center w-full'):
                        ui.button("Run scraper").on_click(
                            lambda: self.scraper(self.page_num)
                        )
                        self.log_element = ui.row().classes('w-full justify-center')
                        self.label = ui.label("Page -> 0").bind_text(self, target_name='page_str')
                
