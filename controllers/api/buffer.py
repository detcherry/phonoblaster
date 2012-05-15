import logging
import re
import django_setup
from django.utils import simplejson as json

from google.appengine.api.taskqueue import Task

from controllers import config
from controllers.base import BaseHandler
from controllers.base import login_required

from models.api.station import StationApi

class ApiBufferHandler(BaseHandler):
	def get(self):
		#return buffer and timestamp of station
		pass

	@login_required
	def put(self):
		#put new track in buffer
		pass

	@login_required
	def post(self):
		#change position of a track from old_position to new position
		pass

	@login_required
	def delete(self):
		#delete track from buffer at position track_position
		pass