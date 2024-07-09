from nicegui import ui
import ultraimport
from model import Buisness, Saved
home = ultraimport('pages/home.py')

@ui.page('/')
def home_page():
    home_p = home.BuisnessPage(Buisness, 'All Buisness')
    home_p.header()
    home_p.main()
    with ui.footer(fixed=False).classes('bg-zinc-700'):
        ui.label("Footer")

@ui.page('/saves')
def saves_page():
    home_p = home.BuisnessPage(Saved, 'All Saved')
    home_p.header()
    home_p.main()
    with ui.footer(fixed=False).classes('bg-zinc-700'):
        ui.label("Footer")

ui.run(port=4000)