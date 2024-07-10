from nicegui import ui, app
import nicegui
import pandas as pd
import ultraimport
from sqlalchemy import create_engine, select, desc
from sqlalchemy.orm import sessionmaker, Query

Saves = ultraimport('./model.py', 'Saved')

ui.add_head_html(
    """<meta name="viewport" content="width=device-width, initial-scale=1.0">"""
)

excludes = [
    "Reason for selling",
    "Seller Financing Available",
    "Seller Financed Payoff Timeline",
    "Employees",
    "Established",
    "Profit Margin",
    "Location",
]

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
    {"name": "Seller Financed Payoff Timeline", "field": "seller_financed_payoff_timeline"},
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
        self.asking_multiple = None
        self.filters = []
        self.order_by_profit_margin = None
        self.order_by_cash_flow = None
    
    #Backends
    
    def float_formatter(self, value):
        try:
            return f'${value:,}'
        except ValueError:
            return value

    def convert_yes_no(self, value):
        if value == 'yes':
            value = 'no'
        else:
            value = 'yes'
        return value  

    def save_obj_as_dict(self, session, obj):
        objects = session.execute(obj)
        objects_dicts = [o[0].__dict__ for o in objects]
        session.close()
        return objects_dicts
    
    def toggle_order(self, col_type: str):
        self.filters = []
        self.page_num = 0
        self.dialog.close()
        if col_type == 'profit_margin':
            self.order_by_cash_flow = None
            self.order_by_profit_margin = self.convert_yes_no(self.order_by_profit_margin)
        elif col_type == 'cash_flow':
            self.order_by_profit_margin = None
            self.order_by_cash_flow = self.convert_yes_no(self.order_by_cash_flow)
        else:
            pass
        self.body.clear()
        self.load_page_body()

    def order_by_schema(self, schema_type: str, yes_or_no: str):
        if yes_or_no == 'yes':
            obj = select(self.model).order_by(desc(eval(schema_type)))
        elif yes_or_no == 'no':
            obj = select(self.model).order_by(eval(schema_type))
        obj = obj.offset(self.page_num*2).limit(2)
        return obj
    
    def load_objects(self):
        session = self.new_session()
        obj = select(self.model)
        if self.order_by_profit_margin:
            obj = self.order_by_schema("self.model.profit_margin", self.order_by_profit_margin)
        elif self.order_by_cash_flow:
            obj = self.order_by_schema("self.model.cash_flow", self.order_by_cash_flow)
        else:
            if len(self.filters) > 0:
                for f in self.filters:
                    obj = obj.filter(f)
                    obj = obj.order_by(self.model.color).offset(self.page_num*2).limit(2)
            else:
                obj = obj.order_by(self.model.color).offset(self.page_num*2).limit(2)
        obj_dict = self.save_obj_as_dict(session, obj)
        return obj_dict
    
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
        if self.asking_multiple:
            self.filters.append(
                eval(f"""self.model.asking_multiple <= {self.asking_multiple}""")
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
            elif var == 'asking_multiple':
                self.asking_multiple = float(value)
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
        with ui.header().classes('bg-zinc-200'):
            with ui.row(align_items='center').classes('w-full justify-between items-center'):
                with ui.column().classes('col-3 w-full'):
                    with ui.row().classes('justify-center w-full max-lg:hidden'):
                        ui.button("Filter", color='black',
                        on_click=lambda: self.right_drawer.toggle()).props('outline')
                        ui.button("Show saved", color='black',
                        on_click=lambda: ui.navigate.to('/saves')).props('outline')
                    with ui.row().classes('justify-start w-full lg:hidden'):
                        with ui.button(icon='menu'):
                            with ui.menu():
                                ui.menu_item("Filter", on_click=lambda: self.dialog.open())
                                ui.menu_item("Show saved", on_click=lambda: ui.navigate.to('/saves'))
                ui.space()
                with ui.column().classes('col w-full'):
                    with ui.row(align_items='center').classes('w-full justify-evenly'):
                        with ui.column().classes('col'):
                            with ui.row().classes('w-full justify-center lg:text-4xl text-2xl font-serif'):
                                with ui.link(target='/').classes('no-underline'):
                                    ui.label('DATA VIZ').classes('text-dark')
                        with ui.column().classes('col-3'):
                            with ui.row().classes('w-full justify-center lg:text-4xl text-2xl font-serif'):
                                ui.label(self.page_title).classes('text-dark text-center')

    def filter_ui(self):
        with ui.row(wrap=False).classes('w-full justify-center my-10'):
            with ui.column():
                with ui.list().props('bordered separator'):
                    ui.item_label('Filters').props('header').classes('text-bold text-h6 flex justify-center')
                    ui.separator()
                    with ui.item():
                        with ui.item_section():
                            ui.number("Asking price", min=1,
                            validation=lambda value: "Provide proper number" if not 
                            self.validate_numbers(value, 'asking') else None).props('filled')
                    with ui.item():
                        with ui.item_section():
                            ui.number("Cash Flow", min=1,
                            validation=lambda value: "Provide proper number" if not 
                            self.validate_numbers(value, 'cash_flow') else None).props('filled')
                    with ui.item():
                        with ui.item_section():
                            ui.number("Asking Multiple", min=1,
                            validation=lambda value: "Provide proper number" if not 
                            self.validate_numbers(value, 'asking_multiple') else None).props('filled')
                    with ui.item():
                        with ui.item_section():
                            ui.button("Order by profit margin", color='zinc-700', icon='sort',
                            on_click=lambda: self.toggle_order("profit_margin")).props('outline')
                    with ui.item():
                        with ui.item_section():
                            ui.button("Order by cash flow", color='zinc-700', icon='sort',
                            on_click=lambda: self.toggle_order("cash_flow")).props('outline')
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
                            if mapper['name'] in excludes:
                                ui.item_label(row[mapper['field']])
                            else:
                                ui.item_label(self.float_formatter(row[mapper['field']]))
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
                    with ui.column().classes(f'border-{buis_color} mb-10'):
                        with ui.row(align_items='stretch').classes('w-full justify-center'):
                            with ui.list().props('separator').classes(f'w-full ring-4 ring-{buis_color}'):
                                ui.item_label(row['name']).props('header').classes(f'text-bold text-black bg-{buis_color}')
                                ui.separator()
                                self.make_a_business_card(row)

    def load_page_body(self):
        objects = self.load_objects()
        if len(objects) > 0:
            self.load_cards(objects)
            self.more_button.enable()
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

       