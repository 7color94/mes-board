#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tornado.web
import re

class BaseHandler(tornado.web.RequestHandler):

    @property
    def asyn_db(self):
        return self.application.asyn_db

    @property
    def db(self):
        return self.application.db

    def get_current_user(self):
        token = self.get_secure_cookie('token')
        user = self.db.users.find_one({
            'token': token
        })
        if user and user['username'] == None:
            return None
        return user

    @property
    def messages(self):
        if not hasattr(self, '_messages'):
            self._messages = []
        return self._messages

    def get_message(self):
        msg = self.messages
        self._messages = []
        return msg

    def append_message(self, msg):
        self.messages.append(msg)

    def make_html(self, content):
        '''
        <span class="list-reply">@ sukai: </span>
        <span class="reply-content">这条是回复dffffff</span>
        '''
        content_html = ''
        pos = 0
        try:
            pos = content.index('@')
            to_user = content[0:pos]
            content_html = '<span class="list-reply">@' + to_user + ': </span>'
            content_html += '<span class="reply-content">' + content[pos+1:] + '</span>'
        except:
            content_html = '<span class="reply-content">' + content + '</span>'
        return content_html

    def check_username(self, username):
        if len(username) > 11:
            return False
        if not re.match('^[0-9a-zA-Z]+$', username):
            return False
        return True

    def get_user_count(self):
        return self.db.users.find().count()

    def get_boards_count(self):
        return self.db.boards.find().count()
