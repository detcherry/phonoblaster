import logging

from controllers.base import BaseHandler
from controllers.base import login_required

from google.appengine.api.taskqueue import Task

class AdminUpgradeHandler(BaseHandler):
	def get(self):
		self.render("admin/dbupgrade.html", None)
	
	def post(self):
		task = Task(
			url = "/taskqueue/upgrade",
			countdown = 1 ,
		)
		task.add(queue_name = "upgrade-queue")