import urllib

from functools import wraps
def login_required(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        user = self.current_user
        if not user:
            if self.request.method == "GET":
				redirection = {"redirect_url": self.request.url}
				self.redirect("/account/login?" + urllib.urlencode(redirection))
				return
            self.error(403)
        else:
            return method(self, *args, **kwargs)
    return wrapper
		