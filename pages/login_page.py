from nicegui import ui, app
#from supabase import create_client, Client
import config
from dateparser import parse
import helper_page as hp

#supabase: Client = create_client(config.supabase_url, config.supabase_key)


class Login_Page:
    def __init__(self) -> None:
        self.username: str = None
        self.password: str = None
        
    
    def login_backend(self):
        self.spinner.visible = True
        print(self.username, self.password)
        try:
            if (self.username == config.username) and (self.password == config.password): 
                print("Logged IN")
                app.storage.user['user'] = self.username
                app.storage.user['expires'] = parse("In 24 hours").isoformat()
                #{'user': self.username, 'on': True, 'expires': parse("In 24 hours").isoformat()}
                self.send_notif(
                    "Logged IN. You will be redirected shortly", 
                    n_type='positive', 
                )
                ui.navigate.to('/')
                return True
            else:
                self.send_notif(
                    "Wrong credentials", 
                    n_type='negative',
                )
                return None
        except Exception as e:
            self.send_notif(
                e, 
                n_type='negative',
            )
            return None
        finally:
            self.spinner.visible = False
            print(app.storage.user.get('user'))
       
            
    def send_notif(self, msg, n_type='info'):
        with self.content_col:
            ui.notification(
                msg, 
                close_button=True, 
                type=n_type, 
                position='top'
            )
        
        
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
                    ui.input(label='username').props('outlined stack-label')\
                    .classes('w-full').bind_value(self, 'username')
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