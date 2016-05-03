import os
import tornado.web
from handler import CollectionHandler


def make_app():
    return tornado.web.Application([
        (r'/(.*)', CollectionHandler),
    ], debug=bool(int(
        os.environ.get('DEBUG', '0')
        ))
    )

if __name__ == "__main__":
    app = make_app()
    app.listen(int(os.environ.get('TORNADO_SERVER_PORT', '8888')))
    tornado.ioloop.IOLoop.current().start()