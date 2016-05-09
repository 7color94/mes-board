#!/usr/bin/env python
# -*- coding: utf-8 -*-
import hashlib

import tornado.web
from base import BaseHandler


class SignupHandler(BaseHandler):
    def get(self):
        self.render('signup.html')

    @tornado.gen.coroutine
    def post(self):
        username = self.get_argument('username', '')
        password = self.get_argument('password', '')
        repeat_password = self.get_argument('repeat-password', '')
        blog = self.get_argument('blog', '')
        if username == '' or password == '' or repeat_password == '':
            self.append_message('亲，三个表单必须都填写')
        if self.messages:
            self.render('signup.html')
            return
        if not self.check_username(username):
            self.append_message('亲，昵称不符合要求，请仔细核对')
        if password != repeat_password:
            self.append_message('你写错了吧，两次密码输入不一样诶')
        if self.messages:
            self.render('signup.html')
            return
        if self.db.users.find_one({'username': username.lower()}):
            self.append_message('昵称被别人抢走了，重选一个吧')
        if self.messages:
            self.render('signup.html')
            return
        token = hashlib.sha1(password + username.lower()).hexdigest()
        yield self.asyn_db.users.insert({
            'username': username.lower(),
            'password': password,
            'token': token,
            'blog': blog
        })
        self.set_secure_cookie('token', token, expires_days=30)
        self.redirect(self.get_argument('next', '/'))


class SignoutHandler(BaseHandler):
    def get(self):
        self.clear_all_cookies()
        self.redirect(self.get_argument('next', '/'))


class AboutHandler(BaseHandler):
    def get(self):
        self.render('about.html')