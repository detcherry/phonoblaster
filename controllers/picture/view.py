import logging
import urllib

from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.blobstore import BlobInfo

from google.appengine.api import memcache

class PictureViewHandler(blobstore_handlers.BlobstoreDownloadHandler):
	def get(self, resource):
		blob_key = str(urllib.unquote(resource))
		blob_info = BlobInfo.get(blob_key)
		
		if not blob_info:
			self.error(404)
		else:
			self.send_blob(blob_info)