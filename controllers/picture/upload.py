from __future__ import with_statement

import logging
import urllib

from controllers.base import *

from django.utils import simplejson

from google.appengine.ext import blobstore
from google.appengine.ext.blobstore import BlobInfo
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import images
from google.appengine.api import files

class PictureUploadHandler(blobstore_handlers.BlobstoreUploadHandler):
	def post(self):
		logging.info("Picture upload request")
		upload_files = self.get_uploads("picture")
		blob_info = upload_files[0]
		self.redirect("/picture/process/%s" % blob_info.key())
	
class PictureProcessHandler(BaseHandler):
	@login_required
	def get(self, resource):
		logging.info("Picture process request")
		self.blob_key = str(urllib.unquote(resource))
		self.blob_info = BlobInfo.get(self.blob_key)
		
		if(self.blobIsPicture()):
			if(self.sizeIsOk()):
				self.image_url = images.get_serving_url(self.blob_key)
				self.thumbnail = self.generateThumbnail()
				self.thumbnail_blob_key = str(self.saveThumbnail())
				self.thumbnail_url = images.get_serving_url(self.thumbnail_blob_key)
				self.formatURLSForLocalhost()
	
				jsonResponse = {
					"blob_key": self.blob_key,
					"image_url": self.image_url,
					"thumbnail_blob_key": self.thumbnail_blob_key,
					"thumbnail_url": self.thumbnail_url,
				}
			else:
				self.blob_info.delete()
				jsonResponse = {
					"upload_error":"Picture is too big"
				}				
		else:
			self.blob_info.delete()
			jsonResponse = {
				"upload_error":"File is not a picture. Only JPEG, PNG, GIF."
			}
		
		logging.info("We generate another blobstore url in case the user would like to change his picture")
		jsonResponse["blobstore_url"] = blobstore.create_upload_url('/picture/upload')
		
		self.response.out.write(simplejson.dumps(jsonResponse))
	
	
	def blobIsPicture(self):
		image_types = ('image/jpeg', 'image/jpg', 'image/png', 'image/gif')
		
		if(self.blob_info.content_type in image_types):
			logging.info("Th file is a jpeg, jpg, png or gif")
			return True
		else:
			logging.info("The file is not an image (jpeg, jpg, png or gif)")
			return False

	def sizeIsOk(self):
		if(self.blob_info.size < 716800):
			logging.info("The image size is below 700Ko")
			return True
		else:
			logging.info("The image size is above 700Ko")
			return False
	
	#If local development, we have to transform http://localhost:8080/ into http://localho.st:8080/
	def formatURLSForLocalhost(self):
		if(self.image_url.startswith("http://local")):
			url_beginning = self.image_url[0:14]
			url_end = self.image_url[14:]
			self.image_url = url_beginning + "." + url_end;
		
		if(self.thumbnail_url.startswith("http://local")):
			url_beginning = self.thumbnail_url[0:14]
			url_end = self.thumbnail_url[14:]
			self.thumbnail_url = url_beginning + "." + url_end;
	
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
		
		
		
application = webapp.WSGIApplication([
	(r"/picture/upload", PictureUploadHandler),
	(r"/picture/process/([^/]+)?", PictureProcessHandler),
], debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
    main()