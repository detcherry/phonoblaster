import urllib

from controllers.base import *

from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.blobstore import BlobInfo

class PictureViewHandler(blobstore_handlers.BlobstoreDownloadHandler):
	def get(self, resource):
		blob_key = str(urllib.unquote(resource))
		blob_info = BlobInfo.get(blob_key)
		
		if not blob_info:
			self.error(404)
		else:
			self.send_blob(blob_info)	

application = webapp.WSGIApplication([
	(r"/picture/view/([^/]+)?", PictureViewHandler),
], debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
    main()