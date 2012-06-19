from __future__ import with_statement

import logging
import urllib
import json

from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.blobstore import BlobInfo
from google.appengine.ext import blobstore

from google.appengine.api import images
from google.appengine.api import files

class PictureHandler(blobstore_handlers.BlobstoreUploadHandler):
	def process(self):
		logging.info("Picture upload request")
		uploaded_files = self.get_uploads("picture")
		
		self.json = {}
		
		if(len(uploaded_files) > 0):
			file = uploaded_files[0]
			self.check_type(file)
			
		else:
			logging.info("No image")
			self.response.out.write(json.dumps({
				"response": False,
				"error": 3,
				"message": "No picture uploaded. Please retry.",
				"blobstore_url": self.blobstore_url,
			}))
	
	# File must be jpeg, jpg, png or gif
	def check_type(self, file):
		image_types = ('image/jpeg', 'image/jpg', 'image/png', 'image/gif')

		if(file.content_type in image_types):
			logging.info("File is a jpeg, jpg, png or gif image")
			image = file
			
			self.check_size(image)
		
		else:
			logging.info("File is not an image (jpeg, jpg, png or gif)")
			
			file.delete()
			logging.info("File deleted from blobstore")
			
			self.response.out.write(json.dumps({
				"response": False,
				"error": 2,
				"message": "Only .jpeg, .jpg, .png, .gif pictures. Please retry.",
				"blobstore_url": self.blobstore_url,
			}))
	
	# Size must be below 1 octet = 1 048 576 octets
	def check_size(self, image):
		if(image.size < 1048576):
			logging.info("Image size below 1 Mo")
			self.save(image)
			
		else:
			logging.info("Image size above 1 Mo")
			
			image.delete()
			logging.info("Image deleted from blobstore")
			
			self.response.out.write(json.dumps({
				"response": False,
				"error": 1,
				"message": "Picture too big: > 1 Mo. Please retry.",
				"blobstore_url": self.blobstore_url,
			}))
	
	def generate_thumbnail(self, image):
		img = images.Image(blob_key = image.key())

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
		logging.info("Image width and height resized to 100px")

		return thumbnail
	
	def save_thumbnail(self, image):
		thumbnail = self.generate_thumbnail(image)
		
		# Thumbnail insertion in the blobstore
		file_name = files.blobstore.create(mime_type='image/png')
		with files.open(file_name, 'a') as f:
			f.write(thumbnail)
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
		
		return thumbnail_blob_key


class PictureUploadHandler(PictureHandler):
	def post(self):
		self.blobstore_url = blobstore.create_upload_url("/picture/upload")
		self.process()

	def save(self, image):
		image_url = "/picture/" + str(image.key()) + "/view"
		thumbnail_blob_key = self.save_thumbnail(image) 
		thumbnail_url = "/picture/" + str(thumbnail_blob_key) + "/view"

		self.response.out.write(json.dumps({
			"response": True,
			"src_full": image_url,
			"src_thumb": thumbnail_url,
			"blobstore_url": self.blobstore_url,
		}))