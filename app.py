#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os

import tornado.httpserver
import tornado.ioloop
import tornado.web
from tornado.options import define, options
import pymongo
import motor

from urls import handlers

version = sys.version_info[0]
if version < 3:
    reload(sys)
    sys.setdefaultencoding('utf-8')

define('port', default=9800, help='run tornado app on the given port', type=int)


class App(tornado.web.Application):
    def __init__(self):
        settings = dict(
            static_path = os.path.join(os.path.dirname(__file__), "static"),
            template_path = os.path.join(os.path.dirname(__file__), "templates"),
            cookie_secret = "ajkfdlkfkdsofidsofjohsdk;eoport",
            autoescape = None,
            xsrf_cookies = True,
            debug = True,
            login_url = "/signin",
        )
        super(App, self).__init__(handlers, **settings)
        self.db = pymongo.Connection('localhost', 27017)['MsgBoard']
        self.db.boards.create_index([('index', -1)])
        self.asyn_db = motor.MotorClient('localhost', 27017)['MsgBoard']


def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(App())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    print 'Development server running on "http://localhost:%s"' % options.port
    print('Quit the server with Control+C')
    main()
