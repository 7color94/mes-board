#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tornado.web
from base import BaseHandler


class UserHandler(BaseHandler):
    @tornado.web.authenticated
    @tornado.gen.coroutine
    def get(self, username):
        account = yield self.asyn_db.users.find_one({
            'username': username.lower(),
        })
        self.render('user.html', account=account)
