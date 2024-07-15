from nicegui import ui
from threading import Thread
from bot import bizscraper
import asyncio
from home import BuisnessPage

class UpdatePage(BuisnessPage):
    def __init__(self):
        self.buis_links = []
        self.buis_infos = []
        self.is_next = True
        self.page_str = None

    async def scraper(self):
        self.spinner.visible = True
        page_num = 28
        while self.is_next:
            print(f'Page: {page_num}')
            self.page_str = f'Page -> {page_num}'
            await bizscraper.s_engine(page_num, self)
            page_num += 1
            self.is_next = False
            await asyncio.sleep(2)

        t = Thread(target=bizscraper.save_data, args=(self.buis_infos,))
        t.start()
        print("DONE!")
        self.spinner.visible = False
        self.page_str = f'Completed'

    async def main(self):
        self.page_title = "Updates"
        self.header()
        with ui.row().classes('w-full justify-center'):
            with ui.card().props('flat bordered').classes('border-8'):
                with ui.card_section().classes('w-full'):
                    with ui.row().classes('w-full justify-center'):
                        ui.label("OPTIONS").classes('text-h5')
                with ui.card_actions().classes('w-full'):
                    with ui.row().classes('w-full justify-center'):
                        ui.input("Location")
                with ui.card_actions().classes('w-full'):
                    with ui.row().classes('justify-center w-full'):
                        ui.button("Run scraper").on_click(
                            lambda: self.scraper()
                        )
                        self.log_element = ui.row().classes('w-full justify-center')
                        self.label = ui.label("Page -> 0").bind_text(self, target_name='page_str')
                
