from nicegui import ui, app
import nicegui
import pandas as pd
import ultraimport
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, Query

Saves = ultraimport('./model.py', 'Saved')

ui.add_head_html(
    """<meta name="viewport" content="width=device-width, initial-scale=1.0">"""
)

mappers = [
    {"name": "Location", 'field': 'location'},
    {"name": "Asking Price", 'field': 'asking_price'},
    {"name": "Cash Flow", 'field': 'cash_flow'},
    {"name": "Gross Revenue", 'field': 'gross_revenue'},
    {"name": "Profit Margin", 'field': 'profit_margin'},
    {"name": "Asking Multiple", "field": 'asking_multiple'},
    {"name": "Gross Margin", "field": 'gross_margin'},
    {"name": "COGS", 'field': "cogs"},
    {"name": "EBITDA", 'field': "ebitda"},
    {"name": "Inventory", 'field': "inventory"},
    {"name": "Real Estate", "field": "real_estate"},
    {"name": "Established", "field": 'established'},
    {"name": "Employees", "field": "employees"},
    {"name": "Seller Financing Available", 'field': 'seller_financing_available'},
    {"name": "Reason for selling", 'field': "reason_for_selling"},
]


class BuisnessPage:
    def __init__(self, model, page_title):
        self.page_num = 0
        self.model = model
        self.more_button = None
        self.page_title = page_title
        self.asking_price = None
        self.cash_flow = None
        self.filters = []
    
    #Backends

    def load_objects(self):
        session = self.new_session()
        obj = select(self.model)
        for f in self.filters:
            obj = obj.filter(f)
        obj = obj.order_by(self.model.color).offset(self.page_num*2).limit(2)    
        objects = session.execute(obj)
        objects_dicts = [o[0].__dict__ for o in objects]
        session.close()
        return objects_dicts
    
    def load_with_filters(self):
        self.dialog.close()
        print("Filtering")
        self.filters = []
        self.page_num = 0
        if self.asking_price:
            self.filters.append(
                eval(f"""self.model.asking_price <= {self.asking_price}""")
            )
        if self.cash_flow:
            self.filters.append(
                eval(f"""self.model.cash_flow <= {self.cash_flow}""")
            )
        if len(self.filters) == 0:
            pass
        else:
            self.body.clear()
            self.load_page_body()

    def validate_numbers(self, value: str|None, var: str):
        if value == None:
            return True
        else:
            try:
                float(value)
            except Exception as e:
                print(e)
                return False
            if var == 'asking':
                self.asking_price = float(value)
                return True
            elif var == 'cash_flow':
                self.cash_flow = float(value)
                return True
            
    def save_buisess(self, row: dict):
        try:
            del row['_sa_instance_state']
            session = self.new_session()
            s1 = Saves(**row)
            session.add(s1)
            session.commit()
            session.close()
            ui.notification(f"{row['name']} Saved", 
            close_button=True, timeout=3)
        except:
            pass

    def remove_buisess(self, row: dict):
        try:
            del row['_sa_instance_state']
            session = self.new_session()
            ds = session.query(Saves)
            ds.filter(Saves.buis_id == row['buis_id']).delete()
            session.commit()
            session.close()
            ui.navigate.reload() 
        except:
            pass
    
    def new_session(self):
        engine = create_engine('sqlite:///db.sqlite3')
        Session = sessionmaker(bind=engine)
        session = Session()
        return session

    def get_color_name(self, row):
        match row['color_name']:
            case 'success':
                return 'green-400'
            case 'warning':
                return 'yellow-400'
            case 'danger':
                return 'red-400'
    
    #Frontends       
 
    def header(self):
        with ui.header().classes('bg-zinc-700'):
            with ui.row(align_items='center').classes('w-full justify-between items-center'):
                with ui.column().classes('col-3 w-full'):
                    with ui.row().classes('justify-center w-full max-lg:hidden'):
                        ui.button("Filter", on_click=lambda: self.right_drawer.toggle())
                        ui.button("Show saved", on_click=lambda: ui.navigate.to('/saves'))
                    with ui.row().classes('justify-start w-full lg:hidden'):
                        with ui.button(icon='menu'):
                            with ui.menu():
                                ui.menu_item("Filter", on_click=lambda: self.dialog.open())
                                ui.menu_item("Show saved", on_click=lambda: ui.navigate.to('/saves'))
                ui.space()
                with ui.column().classes('col w-full'):
                    with ui.row(align_items='center').classes('w-full justify-evenly'):
                        with ui.column().classes('col-3'):
                            with ui.row().classes('w-full justify-center lg:text-4xl text-sm outline'):
                                ui.label(self.page_title)
                        with ui.column().classes('col-3'):
                            with ui.row().classes('w-full justify-center lg:text-4xl text-sm outline'):
                                with ui.link(target='/').classes('no-underline'):
                                    ui.label('DATA VIZ').classes('text-white')

    def filter_ui(self):
        with ui.row(wrap=False).classes('w-full justify-center my-10'):
            with ui.column():
                with ui.list().props('bordered separator'):
                    ui.item_label('Filters').props('header').classes('text-bold text-h6 flex justify-center')
                    ui.separator()
                    with ui.item():
                        with ui.item_section():
                            ui.number("Asking price", 
                            validation=lambda value: "Provide proper number" if not 
                            self.validate_numbers(value, 'asking') else None).props('filled')
                    with ui.item():
                        with ui.item_section():
                            ui.number("Cash Flow", 
                            validation=lambda value: "Provide proper number" if not 
                            self.validate_numbers(value, 'cash_flow') else None).props('filled')
                with ui.row().classes('w-full justify-center'):
                    ui.button("Submit", icon='start',
                    color='zinc-700 text-white', on_click=self.load_with_filters).props('flat')

    def small_screen_dialog(self):
        with ui.dialog() as self.dialog, ui.card().classes('bg-zinc-300'):
            self.filter_ui()

    def large_screen_drawer(self):
        with ui.left_drawer().classes('bg-zinc-300 md:visible') as self.right_drawer:
            self.filter_ui()

    def make_a_business_card(self, row):
        for mapper in mappers:
            with ui.item():
                with ui.item_section():
                    with ui.row(align_items='center').classes('w-full justify-between'):
                        if mapper['field'] == 'reason_for_selling':
                            ui.item_label(mapper['name'])
                            with ui.button('Reason for selling',
                                color='zinc-700').props('flat').classes('text-white'):
                                with ui.menu():
                                    with ui.element('p').classes('p-3'):
                                        ui.label(row[mapper['field']])
                        else:
                            ui.item_label(mapper['name'])
                            ui.item_label(row[mapper['field']])
        ui.separator().classes('my-2')
        with ui.element('div').classes('flex justify-around mb-2'):
            ui.button("Save Buisness", color='secondary', icon='save').props('outline').on_click(
                lambda: self.save_buisess(row)
            )
            if self.page_title == 'All Saved':
                ui.button("Remove Buisness", color='red', icon='delete').props('outline').on_click(
                    lambda: self.remove_buisess(row)
                )
         
    def load_cards(self, objects):
        with self.body:
            with ui.row().classes('justify-center grid grid-cols-2 max-lg:grid-cols-1 md:container md:mx-auto'):
                for idx, row in enumerate(objects):
                    buis_color = self.get_color_name(row)
                    with ui.column().classes(f'border-8 border-{buis_color} mb-10'):
                        with ui.row(align_items='stretch').classes('w-full justify-center'):
                            with ui.list().props('separator bordered').classes('w-full'):
                                ui.item_label(row['name']).props('header').classes(f'text-bold text-black bg-{buis_color}')
                                ui.separator()
                                self.make_a_business_card(row)

    def load_page_body(self):
        objects = self.load_objects()
        if len(objects) > 0:
            self.load_cards(objects)
        else:
            if self.more_button:
                self.more_button.disable()
    
    def handle_pagination(self):
        self.page_num += 1
        self.load_page_body()

    def main(self):
        self.body = ui.element('body').classes('font-mono')
        self.large_screen_drawer()
        self.small_screen_dialog()
        with ui.row().classes('justify-center w-full'):
            self.more_button = ui.button("Load more", 
                on_click=lambda: self.handle_pagination()).classes('sticky bottom-0 flat')
        self.load_page_body()

       