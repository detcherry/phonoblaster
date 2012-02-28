import logging

from controllers.base import BaseHandler
from controllers.base import admin_required

from models.api.admin import AdminApi

class AdminDashboardHandler(BaseHandler):
	@admin_required
	def get(self):
		admin_proxy = AdminApi()
		
		template_values = {
			"number_of_stations": admin_proxy.number_of_stations,
			"number_of_users": admin_proxy.number_of_users,
		}
		
		self.render("admin/dashboard.html", template_values)