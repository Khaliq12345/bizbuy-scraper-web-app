from nicegui import ui
import helper_page as hp
from bot import detailScraper

class SP_DB:
    buis_infos = []

class SP:
    def __init__(self):
        self.page_title = "Scraper"
        self.p_urls_list = []
        
    #Backend-----------------------------------------
    def validate_urls(self):
        self.p_urls_list = [p.strip() for p in self.p_urls_list if len(p) > 0]
        
    async def start_scraper(self):
        self.body.clear()
        db = SP_DB()
        db.buis_infos = []
        self.validate_urls()
        self.spinner.visible = True
        await detailScraper.engine(self.p_urls_list, 'Colorado', db)
        hp.load_cards(self, db.buis_infos)
        self.spinner.visible = False
        
    #Frontend --------------------------------------
    def main(self):
        hp.header(self)
        with ui.element('div').classes('grid grid-cols-6 w-full'):
            with ui.column().classes('col-span-4 col-start-2 outlined'):
                with ui.row().classes('w-full justify-center'):
                    ui.select([], with_input=True, clearable=True, new_value_mode='add-unique', 
                    multiple=True, label='Paste url(s) here')\
                    .classes('w-full').props('use-chips stack-label hide-dropdown-icon').bind_value(
                        self, 'p_urls_list')
                
                    self.submit_btn = ui.button("Submit").on_click(
                        self.start_scraper
                    )
        self.body = ui.element('div').classes('font-mono w-full')
    
    
            