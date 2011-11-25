from controllers.base import BaseHandler
from controllers.library.gaesessions import get_current_session
from django.utils import simplejson

class TwitterLogoutHandler(BaseHandler):
    def get(self):
        session = get_current_session()
        if session.is_active():
            session.terminate()
        self.response.out.write(simplejson.dumps({"loggedout": True}))