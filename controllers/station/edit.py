import re

from controllers.base import *

from google.appengine.ext import blobstore
from google.appengine.ext.blobstore import BlobInfo

from models.interface import config
from models.interface.station import InterfaceStation

from google.appengine.api import memcache

class StationEditHandler(BaseHandler):
	@login_required
	def get(self, station_id):
		self.station_proxy = InterfaceStation(station_identifier = station_id)
		self.current_station = self.station_proxy.station
		
		if not self.current_station:
			self.redirect("/error/404")
		else:
			if(self.station_proxy.is_creator(self.current_user.key())):
				self.additional_template_values = {
					"blobstore_url": blobstore.create_upload_url('/picture/upload'),
					"current_station": self.current_station,
				}
				self.render("../templates/station/edit.html")
			else:
				self.error(403)
	
	def post(self, station_id):
		self.station_proxy = InterfaceStation(station_identifier = station_id)
		self.current_station = self.station_proxy.station
		
		if not self.current_station:
			self.error(404)
		else:
			if(self.station_proxy.is_creator(self.current_user.key())):
				
				self.submitted_picture = self.request.get("blob_key")
				self.submitted_thumbnail = self.request.get("thumbnail_blob_key")
				self.submitted_identifier = self.request.get("identifier").lower()
				self.submitted_website = self.request.get("website")
				self.submitted_description = self.request.get("description")
				
				#Small processing for the website url
				if self.submitted_website != "":
					match = re.search("(http://|https://)", self.submitted_website)
					if not match:
						self.submitted_website = "http://" + self.submitted_website
				
				picture_ok = self.check_image(self.submitted_picture)
				thumbnail_ok = self.check_image(self.submitted_thumbnail)				
				id_ok = self.check_identifier(self.submitted_identifier)
				website_ok = self.check_size(self.submitted_website, 40)
				description_ok = self.check_size(self.submitted_description, 141)
				
				
				if(picture_ok and thumbnail_ok and id_ok and website_ok and description_ok):
					
					self.station_proxy.update_station(
						picture = self.submitted_picture,
						thumbnail = self.submitted_thumbnail,
						identifier = self.submitted_identifier,
						website = self.submitted_website,
						description = self.submitted_description,
					)
					
					self.redirect("/" + self.submitted_identifier)
				
				else:
					self.error(403)
			
			else:
				self.error(403)
	
	def check_image(self, image_blob_key):
		if(image_blob_key):
			blob_info = BlobInfo.get(image_blob_key)
			if blob_info:
				return True
			else:
				return False
		else:
			return True
			
	def check_size(self, string, size):
		size_ok = False
		if(len(string) < size):
			size_ok = True
		return size_ok		
	
	def check_identifier(self, submitted_identifier):
		if(submitted_identifier != self.current_station.identifier):
			id_ok = False
			match = re.search("[^a-zA-Z0-9_]", submitted_identifier)
			if not match:
				id_ok = True

			station_availability = False		
			existing_station = InterfaceStation(station_identifier = submitted_identifier).station
			if not existing_station:
				station_availability = True

			id_size_ok = self.check_size(submitted_identifier, 20)

			if(id_ok and station_availability and id_size_ok):
				return True
			else:
				return False
		else:
			return True

application = webapp.WSGIApplication([
	(r"/(\w+)/edit", StationEditHandler),
], debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
    main()