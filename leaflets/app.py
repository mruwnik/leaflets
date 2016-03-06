import momoko
from tornado.web import Application, url
from tornado import ioloop, httpserver

from leaflets.etc import options
from leaflets.views.auth import LoginHandler
from leaflets.views.base import BaseHandler
from leaflets.views import uimodules


def setup_app():
    """Set the application up.

    :returns: the application instance
    """
    app = Application(
        [
            url(r"/", BaseHandler),
            url(r'/login', LoginHandler, name='login'),
        ],
        debug=options.DEBUG,
        template_path=options.TEMPLATES,
        cookie_secret=options.SECRET_KEY,
        xsrf_cookies=True,
        ui_methods=uimodules,
    )
    return app


def attach_database(io_instance, app):
    app.db = momoko.Pool(
        dsn='dbname={name} user={user} password={password} host={host} port={port}'.format(
            name=options.DB_NAME,
            user=options.DB_USER,
            password=options.DB_PASSWORD,
            host=options.DB_HOST,
            port=options.DB_PORT
        ),
        size=1,
        ioloop=io_instance,
    )


if __name__ == "__main__":
    import logging
    logging.basicConfig()

    app = setup_app()

    io_instance = ioloop.IOLoop.instance()
    attach_database(io_instance, app)

    http_server = httpserver.HTTPServer(app)
    http_server.listen(options.PORT)
    print('Starting application on port %d' % options.PORT)
    ioloop.IOLoop.current().start()

