import logging, re

from datetime import datetime
from datetime import timedelta

from controllers.base import BaseHandler
from controllers.library.gaesessions import get_current_session
from controllers.library import oauthclient
from controllers.config import *
from controllers.library import twitter

from models.db.user import User
from models.api.user import UserApi

TWITTER_ACCESS_TOKEN_URL = "https://api.twitter.com/oauth/access_token"

class TwitterAuthorizeHandler(BaseHandler):
    def get(self):
		verifier = self.request.get("oauth_verifier")

		# Check if verifier (if not that means the user has canceled the Twitter login)
		if verifier:
			session = get_current_session()
			key = session.get('twitter_request_key')
			secret = session.get('twitter_request_secret')
			if key is None or secret is None:
				self.error(500)
				return
			
			# Exchange request token for access token (the one that will be stored)
			key, secret = oauthclient.ExchangeRequestTokenForAccessToken(
				TWITTER_CONSUMER_KEY,
				TWITTER_CONSUMER_SECRET,
				TWITTER_ACCESS_TOKEN_URL,
				verifier,
				key,
				secret
			)
			
			# Build the twitapi
			twitapi = twitter.Api(
				TWITTER_CONSUMER_KEY,
				TWITTER_CONSUMER_SECRET,
				key,
				secret,
				cache=None
			)
			
			# First we check if the user already exists in our database
			user = User.all().filter("twitter_access_token_key", key).get()
			if user:
				logging.info("User already exists")
				# If the user has been updated more than 24 hours ago, we update it (24 hours = 86 400 sec)
				if(user.updated < datetime.now() - timedelta(0,86400)):
					twituser = twitapi.VerifyCredentials()
					
					# Fetch the bigger thumbnail
					response = twitapi.GetBigProfileImage(screen_name = twituser.screen_name)
					regex = re.compile('href="(?P<image>.*)"')
					result = regex.search(response)
					image_url = result.groupdict()["image"]
					
					# Update the user information
					user.twitter_id = str(twituser.id)
					user.twitter_access_token_key = key
					user.twitter_access_token_secret = secret
					user.name = twituser.name
					user.username = twituser.screen_name
					user.thumbnail_url = image_url
					user.put()
					logging.info("@%s updated in datastore"%(user.username))
				else:
					logging.info("No need to update @%s"%(user.username))
			else:
				twituser = twitapi.VerifyCredentials()
				
				# Fetch the bigger thumbnail
				response = twitapi.GetBigProfileImage(screen_name = twituser.screen_name)
				regex = re.compile('href="(?P<image>.*)"')
				result = regex.search(response)
				image_url = result.groupdict()["image"]
				
				# Save the new user				
				user = User(
					twitter_id = str(twituser.id),
					twitter_access_token_key = key,
					twitter_access_token_secret = secret,
					name = twituser.name,
					username = twituser.screen_name,
					thumbnail_url = image_url,
				)
				user.put()
				logging.info("@%s saved in datastore"%(user.username))
			
			# Store the session and put a cookie as well
			session["username"] = str(user.username)

		self.redirect("/oauth/close")