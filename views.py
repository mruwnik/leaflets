import os

from tornado.web import RequestHandler, Application, url
from tornado import ioloop, httpserver


class MainHandler(RequestHandler):
    def get(self):
        self.render('sandra.html')


app = Application([
            url(r"/", MainHandler),
        ],
        debug=True,
        template_path='templates',
    )


if __name__ == "__main__":
    import logging
    logging.basicConfig()
    http_server = httpserver.HTTPServer(app)
    port = int(os.environ.get("PORT", 5000))
    http_server.listen(port)
    ioloop.IOLoop.instance().start()

