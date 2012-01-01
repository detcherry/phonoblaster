import logging
from calendar import timegm
from time import gmtime 
from django.utils import simplejson as json

from controllers.base import BaseHandler

class ApiNowHandler(BaseHandler):
	def get(self):
		time_now = str(timegm(gmtime()))
		data = {
			"time": time_now,
		}
		self.response.out.write(json.dumps(data))
		