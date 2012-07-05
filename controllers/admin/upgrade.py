import logging

from controllers.base import BaseHandler
from controllers.base import admin_required

from google.appengine.api.taskqueue import Task

class AdminUpgradeHandler(BaseHandler):
	@admin_required
	def get(self):
		self.render("admin/upgrade.html", None)
	
	@admin_required
	def post(self):
		task = Task(
			url = "/taskqueue/upgrade",
			countdown = 1 ,
		)
		task.add(queue_name = "upgrade-queue")