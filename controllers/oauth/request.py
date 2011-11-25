from controllers.config import *
from controllers.base import BaseHandler
from controllers.library import oauthclient
from controllers.library.gaesessions import get_current_session

TWITTER_REQUEST_TOKEN_URL = "https://api.twitter.com/oauth/request_token"
TWITTER_AUTHENTICATE_URL = "https://api.twitter.com/oauth/authenticate"

class TwitterRequestHandler(BaseHandler):
    def get(self):
        key, secret = oauthclient.RetrieveServiceRequestToken(TWITTER_REQUEST_TOKEN_URL,
                                                              TWITTER_CONSUMER_KEY,
                                                              TWITTER_CONSUMER_SECRET)
        session = get_current_session()
        if session.is_active():
            session.terminate()
        session['twitter_request_key'] = key
        session['twitter_request_secret'] = secret

        self.redirect(oauthclient.GenerateAuthorizeUrl(TWITTER_AUTHENTICATE_URL, key))