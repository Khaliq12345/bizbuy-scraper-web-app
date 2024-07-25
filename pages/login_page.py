from nicegui import ui, app
from supabase import create_client, Client
import config
from dateparser import parse
import helper_page as hp

supabase: Client = create_client(config.supabase_url, config.supabase_key)


class Login_Page:
    def __init__(self) -> None:
        self.email: str = None
        self.password: str = None
    
    def login_backend(self):
        self.spinner.visible = True
        try:
            supabase.auth.sign_in_with_password({
                'email': self.email,
                'password': self.password
            })
            print("Logged IN")
            app.storage.user['user'] = {'user': self.email, 'on': True, 'expires': parse("In 24 hours").isoformat()}
            ui.notification("Logged IN. You will be redirected shortly", close_button=True, type='positive', position='top')
            ui.navigate.to('/')
            return True
        except:
            ui.notification("Wrong credentials", close_button=True, type='negative', position='top')
            app.storage.user['user'] = {}
            return None
        finally:
            self.spinner.visible = False
            print(app.storage.user['user'])
        
    def page_body(self):
        with ui.element('div').classes('grid grid-rows-4 grid-flow-col w-full h-screen'):
            with ui.element('div').classes('row-span-2 row-start-2'):
                with ui.element('div').classes('grid grid-cols-4 w-full'):
                    self.content_col = ui.column(align_items='center').classes('col-span-2 col-start-2 gap-1')
    
    def content_ui(self):
        with self.content_col:
            with ui.element('div').classes('w-100 border-4 border-slate-600 rounded-lg'):
                ui.item_label("LOGIN").classes('p-5').classes('flex justify-center w-full text-bold')
                self.spinner = ui.spinner(size='10px', type='dots').classes('flex justify-center w-full')
                self.spinner.visible = False
                with ui.item():
                    ui.input(label='email').props('outlined stack-label')\
                    .classes('w-full').bind_value(self, 'email')
                with ui.item():
                    ui.input(label='Password', password=True, password_toggle_button=True)\
                    .props('outlined stack-label').classes('w-full').bind_value(self, 'password')
                with ui.item().classes('flex justify-center w-full'):
                    ui.button("Login").props('unelevated')\
                    .classes('rounded-lg').on_click(
                        self.login_backend)
            
    def main(self):
        ui.colors(
            primary='#393E46'
        )
        ui.query('body').style(
            'background-color: #929AAB;'
        )
        if hp.is_still_login():
            ui.navigate.to('/')
        else:
            self.page_body()
            self.content_ui()