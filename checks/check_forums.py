#!/usr/bin/env python

from __future__ import absolute_import

import urllib
import urllib2

def check_forums(target, helper):
    baseurl = target.baseurl + 'forum/'
    with helper.checking('frontpage'):
        urllib2.urlopen(baseurl)

    login_url = baseurl + 'ucp.php?mode=login'
    login_data = urllib.urlencode({
        'login': 'Login',
        'username': target.username,
        'password': target.password,
    })
    with helper.checking('login'):
        page = urllib2.urlopen(login_url, login_data)
        content = page.read()
        assert 'You have been successfully logged in.' in content, "Login failed"
