from controllers.library.gaesessions import SessionMiddleware

def webapp_add_wsgi_middleware(app):
    app = SessionMiddleware(app, 
							cookie_key="loginwithtwittertestapp_loginwithtwittertestapp_loginwithtwittertestapp_foobar",
							no_datastore=True,
							cookie_only_threshold=0)
    return app
