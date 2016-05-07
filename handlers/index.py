#!/usr/bin/env python
# -*- coding: utf-8 -*-

import hashlib
import time

import tornado.web
from tornado import gen
import pymongo

from . import BaseHandler

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


class AboutHandler(BaseHandler):
    def get(self):
        self.render('about.html')


class UserHandler(BaseHandler):
    @tornado.web.authenticated
    @tornado.gen.coroutine
    def get(self, username):
        account = yield self.asyn_db.users.find_one({
            'username': username.lower(), 
        })
        self.render('user.html', account=account)


handlers = [
    (r"/", IndexHandler),
    (r"/signup", SignupHandler),
    (r"/signin", SigninHandler),
    (r"/signout", SignoutHandler),
    (r"/about", AboutHandler),
    (r"/user/(\w+)", UserHandler),
]