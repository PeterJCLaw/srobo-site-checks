#!/usr/bin/env python

from __future__ import absolute_import

import base64
import json
import urllib2

def check_userman(target, helper):
    baseurl = target.baseurl + 'userman/'
    with helper.checking('frontpage'):
        urllib2.urlopen(baseurl)

    login_url = baseurl + 'user/' + target.username
    login_details = "{0}:{1}".format(target.username, target.password)
    base64string = base64.encodestring(login_details).strip()
    login_headers = {'Authorization': "Basic {0}".format(base64string)}
    request = urllib2.Request(login_url, headers = login_headers)
    with helper.checking('login'):
        page = urllib2.urlopen(request)
        data = json.load(page)
        username = data.get('username')
        if not username:
            raise Exception("Failed to get username from returned data: {0}.".format(data))

        if username != target.username:
            raise Exception("Got wrong username: {0}.".format(username))
