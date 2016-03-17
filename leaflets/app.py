from tornado.web import Application
from tornado import ioloop, httpserver

from leaflets.etc import options
from leaflets.views import handlers, uimodules, LoginHandler


def setup_app():
    """Set the application up.

    :returns: the application instance
    """
    app = Application(
        [handler.get_url() for handler in handlers],
        debug=options.DEBUG,
        template_path=options.TEMPLATES,
        cookie_secret=options.SECRET_KEY,
        static_path=options.STATIC_FILES,
        xsrf_cookies=True,
        ui_methods=uimodules,
        login_url=LoginHandler.url,
    )
    return app


if __name__ == "__main__":
    import logging
    logging.basicConfig()

    app = setup_app()

    io_instance = ioloop.IOLoop.instance()

    http_server = httpserver.HTTPServer(app)
    http_server.listen(options.PORT)
    print('Starting application on port %d' % options.PORT)
    ioloop.IOLoop.current().start()

