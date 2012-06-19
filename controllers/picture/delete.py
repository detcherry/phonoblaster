import logging
import json
import urllib
import webapp2

from google.appengine.ext.blobstore import BlobInfo

class PictureDeleteHandler(webapp2.RequestHandler):
	def delete(self, resource):
		logging.info("Picture delete request")
		
		blob_key = str(urllib.unquote(resource))
		
		if(blob_key):
			blob_info = BlobInfo.get(blob_key)
			blob_info.delete()
			
			logging.info("Picture deleted from blobstore")
			response = {
				"response": True,
			}
			
			self.response.out.write(json.dumps(response))
		
		else:
			logging.info("No blob key found")
			self.error(404)
