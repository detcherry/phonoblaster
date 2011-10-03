import re
from datetime import datetime

from controllers.base import *

from google.appengine.ext import blobstore
from google.appengine.ext.blobstore import BlobInfo

from models.db.station import Station

class StationCreateHandler(BaseHandler):
	@login_required
	def get(self):
		if(self.checkIfAlreadyStationCreator()):
			self.additional_template_values = {
				"blobstore_url": blobstore.create_upload_url('/picture/upload')
			}
			self.render("../templates/station/create.html")
		else:
			self.redirect("/")
	
	@login_required
	def post(self):	
		picture_key = self.request.get("blob_key")
		thumbnail_key = self.request.get("thumbnail_blob_key")
		identifier = self.request.get("identifier").lower()
		website = self.request.get("website")
		description = self.request.get("description")

		#Small processing for the website url
		if website != "":
			match = re.search("(http://|https://)", website)
			if not match:
				website = "http://" + website

		notStationCreator = self.checkIfAlreadyStationCreator()
		pictureOk = self.checkBlobKey(picture_key)
		thumbnailOk = self.checkBlobKey(thumbnail_key)
		identifierOk = self.checkStationID(identifier)
		websiteOk = self.checkSize(website, 40)
		descriptionOk = self.checkSize(description, 141)
		
		if(notStationCreator):
			logging.info("Not station creator ")
		if(pictureOk):
			logging.info("Picture OK")
		if(thumbnailOk):
			logging.info("Thumbnail OK")
		if(identifierOk):
			logging.info("Identifier Ok")
		if(websiteOk):
			logging.info("Website Ok")
		if(descriptionOk):
			logging.info("Description Ok")
		
		if(notStationCreator and pictureOk and thumbnailOk and identifierOk and websiteOk and descriptionOk):
			self.saveStation(picture_key, thumbnail_key, identifier, website, description)
			self.redirect("/"+identifier+"/contributors")
		else:
			self.error(403)
	
	def checkIfAlreadyStationCreator(self):
		station = Station.all().filter("creator", self.current_user.key()).get()
		if not station:
			return True
		else:
			return False
	
	def checkBlobKey(self, blob_key):
		blobKeyOk = False
		
		if(blob_key):
			blob_info = BlobInfo.get(blob_key)
			if(blob_info):
				blobKeyOk = True
		
		return blobKeyOk
	
	def checkStationID(self, station_id):
		idOk = False
		match = re.search("[^a-zA-Z0-9_]", station_id)
		if not match:
			idOk = True
		
		stationAvailability = False		
		existingID = Station.all().filter("identifier",station_id).get()
		if not existingID:
			stationAvailability = True
		
		idSizeOk = self.checkSize(station_id, 20)
		
		if(idOk and stationAvailability and idSizeOk):
			return True
		else:
			return False
		
	def checkSize(self, string, size):
		sizeOk = False
		
		if(len(string) < size):
			sizeOk = True
		
		return sizeOk
		
	def saveStation(self, picture_key, thumbnail_key, identifier, website, description):
		station = Station(
			creator = self.current_user.key(),
			identifier = identifier,
			picture = picture_key,
			thumbnail = thumbnail_key,
			website = website,
			description = description,
			active = datetime.now(),
		)
		station.put()
		logging.info("Station %s saved" % (identifier))
		
		

application = webapp.WSGIApplication([
	(r"/station/create", StationCreateHandler),
], debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
    main()