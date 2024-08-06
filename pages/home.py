from nicegui import ui, app
import asyncio, math
from sqlalchemy import select, desc, delete, asc, text
from model import Buisness
import helper_page as hp
from static import *

class BuisnessPage:
    def __init__(self, model: Buisness, page_title):
        self.filter_info = None
        self.page_num = 0
        self.total_page_num = 1
        self.model = model
        self.more_button = None
        self.page_title = page_title
        self.asking_price = None
        self.cash_flow = None
        self.asking_multiple= None
        self.order_by_profit_margin = None
        self.order_by_cash_flow = None
        self.state = None
        self.statement = select(self.model).order_by(self.model.color)
        self.total_data = 0
    
    #Backends
    
    async def get_total_page_num(self):
        async_session = await hp.new_session()
        async with async_session() as session:
            self.total_page_num = await session.execute(self.statement)
            self.total_page_num = self.total_page_num.fetchall()
            self.total_page_num = len(self.total_page_num)
            self.total_page_num = math.ceil(self.total_page_num/20)
        return self.total_page_num
    
    def convert_yes_no(self, value):
        if value == 'yes':
            value = 'no'
        else:
            value = 'yes'
        return value  

    async def save_obj_as_dict(self, session, obj):
        objects = await session.execute(obj)
        objects_dicts = [o[0].__dict__ for o in objects]
        return objects_dicts
    
    async def toggle_order(self, value: str):
        self.page_num = 0
        self.dialog.close()
        self.statement = self.statement.order_by(None)
        if value == 'Desc Profit Margin':
            self.statement = self.statement.order_by(desc(self.model.profit_margin_orig))
        elif value == 'Asc Profit Margin':
            self.statement = self.statement.order_by(asc(self.model.profit_margin_orig))
        elif value == 'Desc Cash Flow':
            self.statement = self.statement.order_by(desc(self.model.cash_flow))
        elif value == 'Asc Cash Flow':
            self.statement = self.statement.order_by(asc(self.model.cash_flow))
        self.body.clear()
        asyncio.create_task(self.load_page_body())
    
    async def load_objects(self):
        async_session = await hp.new_session()
        async with async_session() as session:
            q = text("SELECT count(*) FROM orig")
            self.total_page_num = await session.execute(q)
            self.total_page_num = self.total_page_num.first()[0]
            self.total_page_num = math.ceil(self.total_page_num/20)
            obj = self.statement.offset(self.page_num*20).limit(20)
            obj_dict = await self.save_obj_as_dict(session, obj)
        return obj_dict
    
    async def load_with_filters(self):
        self.dialog.close()
        print("Filtering")
        self.page_num = 0
        self.statement = select(self.model)
        if self.asking_price:
            self.statement = self.statement.where(
                self.model.asking_price <= self.asking_price)
        if self.cash_flow:
            self.statement = self.statement.where(
                self.model.cash_flow <= self.cash_flow)
        if self.asking_multiple:
            self.statement = self.statement.where(
                self.model.asking_multiple <= self.asking_multiple)
        if self.state:
            self.statement = self.statement.where(
                self.model.location.in_([self.state]))
        print(self.statement)
        self.body.clear()
        asyncio.create_task(self.load_page_body())
       
    async def remove_buisess(self, row: dict):
        self.spinner.visible = True
        try:
            del row['_sa_instance_state']
            async_session = await hp.new_session()
            async with async_session() as session:
                del_stm = delete(self.model).where(self.model.buis_id == row['buis_id'])
                await session.execute(del_stm)
                await session.commit()
            ui.navigate.reload() 
        except Exception as e:
            print(e)
        finally:
            self.spinner.visible = False
    
    #Frontends

    def filter_ui(self):
        with ui.column(wrap=False).classes('w-full justify-center my-10') as self.filter_col:
            with ui.column():
                with ui.list().props('bordered separator'):
                    ui.item_label('Filters').props('header').classes('text-bold text-h6 flex justify-center')
                    ui.separator()
                    for fm in filters_mappers:
                        if fm['type'] == 'number':      
                            with ui.item():
                                with ui.item_section():
                                    ui.number(fm['name'], min=1).props('filled').bind_value(
                                        self, fm['field']
                                    )
                    with ui.item():
                        with ui.item_section():
                            ui.select(
                                options=["Texas", "New Jersey", "Colorado", 'New York'],
                                label="Select State", clearable=True,
                            ).bind_value(self, 'state')
                            
                with ui.row().classes('w-full justify-center'):
                    ui.button("Submit", icon='start',
                    color='zinc-700 text-white', on_click=self.load_with_filters).props('flat')

    def toggle_ui(self):
        with self.filter_col:
            ui.icon('sort').classes('w-full justify-center')
            with ui.row(wrap=False, align_items='center').classes('w-full justify-center'):
                ui.toggle(
                ["Asc Profit Margin", "Desc Profit Margin", 
                'Asc Cash Flow', 'Desc Cash Flow'], clearable=True)\
                .classes('flex flex-col outline').props('flat')\
                .on_value_change(lambda e: self.toggle_order(e.value))

    def small_screen_dialog(self):
        with ui.dialog() as self.dialog, ui.card().classes('bg-zinc-300'):
            self.filter_ui()
            self.toggle_ui()

    def large_screen_drawer(self):
        with ui.left_drawer().classes('bg-zinc-300 md:visible') as self.right_drawer:
            self.filter_ui()
            self.toggle_ui()
         
    async def load_page_body(self):
        self.spinner.visible = True
        #await self.get_total_page_num()
        #self.pagination_ui()
        objects = await self.load_objects()
        if len(objects) > 0:
            hp.load_cards(self, objects)
        self.filter_info = f'''
        Asking Price <= {self.asking_price} |
        Cash Flow <= {self.cash_flow} |
        Asking Multiple <= {self.asking_multiple} |
        State: {self.state}'''
        self.spinner.visible = False
        
    async def handle_pagination(self):
        self.body.clear()
        await self.load_page_body()

    def pagination_ui(self):
        self.pagination_col.clear()
        with self.pagination_col:
            ui.pagination(0, 280, direction_links=True).on_value_change(
                self.handle_pagination
            ).bind_value(self, 'page_num').props('boundary-links :max-pages="5"')

    async def main(self):
        hp.header(self)
        with ui.element('div').classes('justify-center w-full font-mono text-bold'):
            ui.label("Filters:").bind_text(self, 'filter_info')
        self.body = ui.element('body').classes('font-mono')
        self.large_screen_drawer()
        self.small_screen_dialog()
        self.pagination_col = ui.element('div').classes('flex flex-row justify-center w-full')
        self.pagination_ui()
        asyncio.create_task(self.load_page_body())

       