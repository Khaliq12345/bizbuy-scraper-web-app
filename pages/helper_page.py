from dateparser import parse
from nicegui import app

def is_still_login():
    match app.storage.user['user'].get('user'):
        case None:
            return False
        case _:
            expiresIn = parse(app.storage.user['user'].get('expires'))
            if expiresIn > parse('now'):
                return True
            else:
                app.storage.user['user'] = {}
                return False