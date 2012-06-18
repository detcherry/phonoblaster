import logging
import json

from google.appengine.api.taskqueue import Task

from controllers import config
from controllers.picture.upload import PictureUploadHandler
from models.api.station import StationApi

class ApiBackgroundHandler(PictureUploadHandler):
	def post(self, shortname):
		self.station_proxy = StationApi(shortname)
		if(self.station_proxy.station):
			self.process()
	
	def save(self, image):
		image_url = "/picture/" + str(image.key()) + "/view"
		thumbnail_blob_key = self.save_thumbnail(image) 
		thumbnail_url = "/picture/" + str(thumbnail_blob_key) + "/view"
		
		self.station_proxy.update_background(image_url, thumbnail_url)				

		response = {
			"response": True,
			"src_full": image_url,
			"src_thumb": thumbnail_url,
		}
		
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