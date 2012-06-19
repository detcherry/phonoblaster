import logging
import json

from google.appengine.ext import blobstore
from google.appengine.api.taskqueue import Task

from controllers import config
from controllers.picture.upload import PictureHandler
from models.api.station import StationApi

class ApiBackgroundHandler(PictureHandler):
	def post(self, shortname):
		self.blobstore_url = blobstore.create_upload_url('/api/' + shortname + "/background")
		
		self.station_proxy = StationApi(shortname)
		if(self.station_proxy.station):
			self.process()
	
	def save(self, image):		
		image_url = "/picture/" + str(image.key()) + "/view"
		thumbnail_blob_key = self.save_thumbnail(image) 
		thumbnail_url = "/picture/" + str(thumbnail_blob_key) + "/view"
		
		self.station_proxy.update_background(image_url, thumbnail_url)					
		
		data = {
			"entity": "background",
			"event": "new",
			"content": image_url,
		}
		
		task = Task(
			url = "/taskqueue/multicast",
			params = {
				"station": config.VERSION + "-" + self.station_proxy.station.shortname,
				"data": json.dumps(data)
			}
		)
		task.add(queue_name="worker-queue")
		
		self.response.out.write(json.dumps({
			"response": True,
			"src_full": image_url,
			"src_thumb": thumbnail_url,
			"blobstore_url": self.blobstore_url,
		}))