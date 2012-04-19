import logging

from controllers.base import BaseHandler
from controllers.base import admin_required

from google.appengine.api.taskqueue import Task

class DBUpgradeHandler(BaseHandler):
	@admin_required
	def get(self):
		self.render("admin/dbupgrade.html",{})

	@admin_required
	def post(self):
		logging.info("Upgrading database")

		task = Task(
				url = "/taskqueue/upgrade",
				params = {},
			)
		task.add(queue_name = "upgrade-queue")
		logging.info("Task Upgrade put in the queue")