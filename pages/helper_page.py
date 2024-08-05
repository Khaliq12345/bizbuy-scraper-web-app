from dateparser import parse
from nicegui import app
from nicegui import ui
from static import *
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import config
from model import Saved

#Backend-------------------------------
async def new_session():
    engine = create_async_engine(config.db_url)
    async_session = sessionmaker(bind=engine, class_=AsyncSession)
    return async_session

def get_color_name(row):
    match row['color_name']:
        case 'success':
            return 'green-400'
        case 'warning':
            return 'yellow-400'
        case 'danger':
            return 'red-400'

def float_formatter(value):
    try:
        return f'${value:,}'
    except ValueError:
        return value

def logout_now():
    app.storage.user['user'] = None
    app.storage.user['expires'] = None
    ui.navigate.to('/login')

def is_still_login():
    match app.storage.user.get('user'):
        case None:
            return False
        case _:
            expiresIn = parse(app.storage.user.get('expires'))
            if expiresIn > parse('now'):
                return True
            else:
                app.storage.user['user'] = None
                app.storage.user['expires'] = None
                return False

async def save_buisess(page_obj, row: dict):
    page_obj.spinner.visible = True
    try:
        if row.get('_sa_instance_state'):
            del row['_sa_instance_state']            
        async_session = await new_session()
        async with async_session() as session:
            s1 = Saved(**row)
            async with session.begin():
                session.add(s1)
            await session.commit()
        ui.notification(f"{row['name']} Saved", 
        close_button=True, timeout=3)
    except Exception as e:
        print(e)
    finally:
        page_obj.spinner.visible = False

#Frontend------------------------------      
                         
def make_a_business_card(page_obj, row):
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
                            ui.item_label(float_formatter(row[mapper['field']]))
    ui.separator().classes('my-2')
    with ui.element('div').classes('flex justify-around mb-2'):
        ui.button("Save Buisness", color='secondary', icon='save').props('outline').on_click(
            lambda: save_buisess(page_obj, row)
        )
        if page_obj.page_title == 'All Saved':
            ui.button("Remove Buisness", color='red', icon='delete').props('outline').on_click(
                lambda: page_obj.remove_buisess(row)
            )

def load_cards(page_obj, objects):
    with page_obj.body:
        with ui.row().classes('justify-center grid grid-cols-2 max-lg:grid-cols-1 md:container md:mx-auto'):
            for idx, row in enumerate(objects):
                buis_color = get_color_name(row)
                with ui.column().classes(f'border-{buis_color} mb-10'):
                    with ui.row(align_items='stretch').classes('w-full justify-center'):
                        with ui.list().props('separator').classes(f'w-full ring-4 ring-{buis_color} rounded-lg'):
                            with ui.link(target=row['buis_link'], new_tab=True).classes('no-underline'):
                                ui.item_label(row['name']).props('header').classes(f'text-bold text-black bg-{buis_color}')
                            ui.separator()
                            make_a_business_card(page_obj, row)
          
def header(page_obj):
    with ui.header().classes('bg-zinc-200'):
        with ui.row(align_items='center').classes('w-full justify-between items-center'):
            with ui.column().classes('col-3 w-full'):
                with ui.row().classes('justify-center w-full max-lg:hidden'):
                    with ui.button_group().props('outline').classes('rounded-lg'):
                        if page_obj.page_title != 'Scraper':
                            ui.button("Filter",
                            on_click=lambda: page_obj.right_drawer.toggle()).props('outline color="black"')
                        ui.button("Show saved",
                        on_click=lambda: ui.navigate.to('/saves')).props('outline color="black"')
                        ui.button("Scraper",
                        on_click=lambda: ui.navigate.to('/scrape')).props('outline color="black"')
                        
                with ui.row().classes('justify-start w-full lg:hidden'):
                    with ui.button(icon='menu'):
                        with ui.menu():
                            if page_obj.page_title != 'Scraper':
                                ui.menu_item("Filter", on_click=lambda: page_obj.dialog.open())
                            ui.menu_item("Show saved", on_click=lambda: ui.navigate.to('/saves'))
                            ui.menu_item("Scraper", on_click=lambda: ui.navigate.to('/scrape'))
            ui.space()      
            with ui.column().classes('col w-full'):
                with ui.row(align_items='center').classes('w-full justify-evenly'):
                    with ui.column().classes('col'):
                        with ui.row().classes('w-full justify-center lg:text-4xl text-2xl font-serif'):
                            with ui.link(target='/').classes('no-underline'):
                                ui.label('DATA VIZ').classes('text-dark')
                    with ui.column().classes('col'):
                        with ui.row().classes('w-full justify-center lg:text-4xl text-2xl font-serif'):
                            ui.label(page_obj.page_title).classes('text-dark text-center')
                    with ui.column().classes('col-1'):
                        with ui.row().classes('w-full justify-center'):
                            page_obj.spinner = ui.spinner(size='lg')
                            page_obj.spinner.visible = False
            with ui.column().classes('col-1 w-full'):
                ui.button("Logout").props('unelevated outline color="black"')\
                .classes('rounded-lg').on_click(
                    lambda: logout_now()
                )