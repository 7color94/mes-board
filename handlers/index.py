#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time

import pymongo
import tornado.web
from user import UserHandler

from base import BaseHandler
from signin import SigninHandler
from signup import SignoutHandler, SignupHandler, AboutHandler

ISOTIMEFORMAT='%Y-%m-%d %X'

class IndexHandler(BaseHandler):
    def get(self):
        replies = self.db.boards.find().sort('reply_time',pymongo.DESCENDING)
        replies_count = self.db.boards.find().count()
        p = int(self.get_argument('p', 1))
        self.render(
            'index.html',
            replies=replies,
            replies_count=replies_count,
            p=p,
        )

    @tornado.gen.coroutine
    def post(self):
        content =self.get_argument('content', '')
        p = int(self.get_argument('p', 1))
        cur_time = time.strftime(ISOTIMEFORMAT, time.localtime( time.time()))
        author = self.get_current_user()["username"]
        ip = self.request.remote_ip
        content_html = self.make_html(content)
        index = self.db.boards.find().count()
        #print content, cur_time, author, ip, content_html, index
        yield self.asyn_db.boards.insert({
            'author': author,
            'content': content,
            'reply_time': cur_time,
            'ip': ip,
            'index': index+1,
            'content_html': content_html,
        })
        replies = self.db.boards.find().sort('reply_time',pymongo.DESCENDING)
        self.render(
            'index.html',
            replies=replies,
            replies_count=index+1,
            p=p,
        )


handlers = [
    (r"/", IndexHandler),
    (r"/signup", SignupHandler),
    (r"/signin", SigninHandler),
    (r"/signout", SignoutHandler),
    (r"/about", AboutHandler),
    (r"/user/(\w+)", UserHandler),
]