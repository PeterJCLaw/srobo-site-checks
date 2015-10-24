#!/usr/bin/env python

from __future__ import absolute_import

import base64
import json
import urllib2

def check_voting(target, helper):
    url = target.baseurl + 'voting/'

    login_details = "{0}:{1}".format(target.username, target.password)
    base64string = base64.encodestring(login_details).strip()
    login_headers = {'Authorization': "Basic {0}".format(base64string)}
    request = urllib2.Request(url, headers = login_headers)
    with helper.checking('login'):
        page = urllib2.urlopen(request)
        content = page.read()
        assert 'sRAVEs' in content, "Login Failed"
