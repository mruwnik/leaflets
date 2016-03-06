from tornado.web import RequestHandler, Application, url
from etc import options
from tornado import ioloop, httpserver


class MainHandler(RequestHandler):
    def get(self):
        self.render('sandra.html')


if __name__ == "__main__":
    import logging
    logging.basicConfig()

    app = Application([
            url(r"/", MainHandler),
        ],
        debug=options.DEBUG,
        template_path=options.TEMPLATES,
    )

    io_instance = ioloop.IOLoop.instance()

    http_server = httpserver.HTTPServer(app)
    http_server.listen(options.PORT)
    io_instance.start()

