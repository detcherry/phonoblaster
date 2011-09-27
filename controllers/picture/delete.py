from controllers.base import *

from django.utils import simplejson

from google.appengine.ext.blobstore import BlobInfo

class PictureDeleteHandler(BaseHandler):
	@login_required
	def post(self):
		logging.info("Picture delete request")
		picture_blob_key = self.request.get("blob_key")
		logging.info("Picture blob key: %s" %(picture_blob_key))
		
		if(picture_blob_key):
			blob_info = BlobInfo.get(picture_blob_key)
			blob_info.delete()
			logging.info("Picture deleted from the blobstore")
			jsonResponse = {
				"response":"picture deleted"
			}
		else:
			logging.info("No blob key found")
			jsonResponse = {
				"response":"no blob key found"
			}
		self.response.out.write(simplejson.dumps(jsonResponse))

application = webapp.WSGIApplication([
	(r"/picture/delete", PictureDeleteHandler),
], debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
    main()