import logging

from controllers.base import BaseHandler
from controllers.base import login_required

from google.appengine.api.taskqueue import Task

class UpgradeHandler(BaseHandler):
	def post(self):
		task = Task(
				url = "/taskqueue/upgrade",
				params = {'typeUpgrade':'buffer'},
				countdown = 1 ,
			)
		task.add(queue_name = "upgrade-queue")