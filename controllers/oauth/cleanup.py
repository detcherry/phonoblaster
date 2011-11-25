from controllers.base import BaseHandler
from controllers.library.gaesessions import delete_expired_sessions

# Cleanup expired sessions at regular intervals
class TwitterCleanupHandler(BaseHandler):
    def get(self):
        while not delete_expired_sessions():
            pass