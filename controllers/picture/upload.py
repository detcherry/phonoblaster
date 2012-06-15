from __future__ import with_statement

import logging
import webapp2
import urllib
import json

from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.blobstore import BlobInfo
from google.appengine.ext import blobstore

from google.appengine.api import images
from google.appengine.api import files

class PictureUploadHandler(blobstore_handlers.BlobstoreUploadHandler):
	def post(self):
		logging.info("Picture upload request")
		upload_files = self.get_uploads("picture")
		blob_info = upload_files[0]
		self.redirect("/picture/%s/process" % blob_info.key())
		
class PictureProcessHandler(webapp2.RequestHandler):
	def get(self, resource):
		logging.info("Picture process request")
		self.blob_key = str(urllib.unquote(resource))
		self.blob_info = BlobInfo.get(self.blob_key)

		if(self.blobIsPicture()):
			if(self.sizeIsOk()):
				self.image_url = "/picture/" + self.blob_key + "/view"
				self.thumbnail = self.generateThumbnail()
				self.thumbnail_blob_key = str(self.saveThumbnail())
				self.thumbnail_url = "/picture/" + self.thumbnail_blob_key + "/view"

				response = {
					"response": True,
					"blob_full": self.blob_key,
					"src_full": self.image_url,
					"blob_thumb": self.thumbnail_blob_key,
					"src_thumb": self.thumbnail_url,
				}
			else:
				self.blob_info.delete()
				response = {
					"response": False,
					"error": 1,
					"message": "Picture too big: > 1 Mo. Please retry.",
				}				
		else:
			self.blob_info.delete()
			response = {
				"response": False,
				"error": 2,
				"message": "Only .jpeg, .jpg, .png, .gif pictures. Please retry.",
			}

		logging.info("We generate another blobstore url in case the user would like to change his picture")
		response["blobstore_url"] = blobstore.create_upload_url('/picture/upload')

		self.response.out.write(json.dumps(response))
	
	def blobIsPicture(self):		
		image_types = ('image/jpeg', 'image/jpg', 'image/png', 'image/gif')

		if(self.blob_info.content_type in image_types):
			logging.info("File is a jpeg, jpg, png or gif image")
			return True
		else:
			logging.info("File is not an image (jpeg, jpg, png or gif)")
			return False

	# Size must be below 1 octet = 1 048 576 octets
	def sizeIsOk(self):
		if(self.blob_info.size < 1048576):
			logging.info("Image size below 1 Mo")
			return True
		else:
			logging.info("Image size above 1 Mo")
			return False

	def generateThumbnail(self):
		img = images.Image(blob_key = self.blob_key)

		#Necessary to perform at least one transformation to get the actual image data (and therefore its width and height)
		img.im_feeling_lucky()
		img.execute_transforms()

		if(img.width < img.height):
			#We have to crop the image along the vertical axis
			left_x = 0.0
			top_y = 0.5 * (1 - float(img.width)/float(img.height))
		else:
			#We have to crop the image along the horizontal axis
			left_x = 0.5 * (1 - float(img.height)/float(img.width))
			top_y = 0.0

		right_x = 1.0 - left_x
		bottom_y = 1.0 - top_y

		logging.info("We crop the image with these dimensions: left = %f, right = %f, top = %f, bottom = %f" % (left_x, right_x, top_y, bottom_y))
		#The output encoding is PNG (default app engine)
		img.crop(left_x, top_y, right_x, bottom_y)

		img.resize(width = 100, height = 100)
		thumbnail = img.execute_transforms()
		logging.info("image width and height resized to 100px")

		return thumbnail

	def saveThumbnail(self):
		#Thumbnail insertion in the blobstore
		file_name = files.blobstore.create(mime_type='image/png')
		with files.open(file_name, 'a') as f:
			f.write(self.thumbnail)
		files.finalize(file_name)

		# Sometimes the blob key is None...
		thumbnail_blob_key = files.blobstore.get_blob_key(file_name)

		# We have to make it wait til it works!
		for i in range(1,10):	
			if(thumbnail_blob_key):
				return thumbnail_blob_key
			else:
				logging.info("Thumbnail blob key is still None")
				time.sleep(0.05)
				thumbnail_blob_key = files.blobstore.get_blob_key(file_name)