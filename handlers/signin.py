#!/usr/bin/env python
# -*- coding: utf-8 -*-
import hashlib

import tornado.web
from base import BaseHandler
class SigninHandler(BaseHandler):
    def get(self):
        if self.get_current_user():
            self.redirect('/')
        self.render('signin.html')

    @tornado.gen.coroutine
    def post(self):
        username = self.get_argument('username', '')
        password = self.get_argument('password', '')
        if username == '' or password == '':
            self.append_message('请完整填写登录信息哦')
            self.render('signin.html')
            return
        token = hashlib.sha1(password + username.lower()).hexdigest()
        account = yield self.asyn_db.users.find_one({
            'username': username.lower(),
            'password': password,
            'token': token,
        })
        if not account:
            self.append_message('你是假的，数据库里面没有你')
        if self.messages:
            self.render('signin.html')
            return
        self.set_secure_cookie('token', token, expires_days=30)
        self.redirect(self.get_argument('next', '/'))
