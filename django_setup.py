from google.appengine.dist import use_library
use_library('django', '1.2')
from django.conf import settings
settings.configure(INSTALLED_APPS=('empty',))
