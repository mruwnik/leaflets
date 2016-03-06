import momoko
from tornado.web import RequestHandler, Application, url
from tornado import ioloop, httpserver, gen

from leaflets.etc import options


class MainHandler(RequestHandler):
    @gen.coroutine
    def get(self):
        conn = yield self.application.db.connect()  #self.connection()
        result = yield conn.execute('select 1')
        print(result)
        self.render('sandra.html')


def setup_app():
    """Set the application up.

    :returns: the application instance
    """
    app = Application([
            url(r"/", MainHandler),
        ],
        debug=options.DEBUG,
        template_path=options.TEMPLATES,
    )

    io_instance = ioloop.IOLoop.instance()

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
    return app


if __name__ == "__main__":
    import logging
    logging.basicConfig()

    app = setup_app()
    http_server = httpserver.HTTPServer(app)
    http_server.listen(options.PORT)
    print('Starting application on port %d' % options.PORT)
    ioloop.IOLoop.current().start()

