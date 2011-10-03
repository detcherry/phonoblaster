import re

from controllers.station.root import *

from google.appengine.ext import blobstore
from google.appengine.ext.blobstore import BlobInfo

class StationEditHandler(RootStationHandler):
	def get(self, station_id):
		self.current_station = Station.all().filter("identifier", station_id).get()
		
		if not self.current_station:
			self.error(404)
		else:
			if(self.current_station.creator.key() == self.current_user.key()):
				self.additional_template_values = {
					"blobstore_url": blobstore.create_upload_url('/picture/upload')
				}
				self.render("../../templates/station/edit.html")
			else:
				self.error(403)
	
	def post(self, station_id):
		logging.info("trying to edit the station")
		self.current_station = Station.all().filter("identifier", station_id).get()
		
		if not self.current_station:
			self.error(404)
		else:
			if(self.current_station.creator.key() == self.current_user.key()):
				self.new_picture = self.request.get("blob_key")
				self.new_thumbnail = self.request.get("thumbnail_blob_key")
				self.new_identifier = self.request.get("identifier").lower()
				self.new_website = self.request.get("website")
				self.new_description = self.request.get("description")
				
				self.checkPicture()
				self.checkThumbnail()
				idOk = self.checkIdentifier()
				websiteOk = self.checkSize(self.new_website, 40)
				descriptionOk = self.checkSize(self.new_description, 141)
				
				if(idOk and websiteOk and descriptionOk):
					self.current_station.website = self.new_website
					self.current_station.description = self.new_description
					self.current_station.put()
					self.redirect("/"+self.new_identifier)
					
				else:
					self.error(403)
			else:
				self.error(403)
	
				
	def checkPicture(self):
		if(self.new_picture):
			blob_info = BlobInfo.get(self.new_picture)
			if blob_info:
				self.current_station.picture = self.new_picture
			
	def checkThumbnail(self):
		if(self.new_thumbnail):
			blob_info = BlobInfo.get(self.new_thumbnail)
			if blob_info:
				self.current_station.thumbnail = self.new_thumbnail
	
	def checkIdentifier(self):
		if(self.new_identifier != self.current_station.identifier):
			idOk = False
			match = re.search("[^a-zA-Z0-9_]", self.new_identifier)
			if not match:
				idOk = True

			stationAvailability = False		
			existingID = Station.all().filter("identifier", self.new_identifier).get()
			if not existingID:
				stationAvailability = True

			idSizeOk = self.checkSize(self.new_identifier, 20)

			if(idOk and stationAvailability and idSizeOk):
				self.current_station.identifier = self.new_identifier
				return True
			else:
				return False
		else:
			return True

	def checkSize(self, string, size):
		sizeOk = False
		if(len(string) < size):
			sizeOk = True
		return sizeOk
		
	

application = webapp.WSGIApplication([
	(r"/(\w+)/edit", StationEditHandler),
], debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
    main()