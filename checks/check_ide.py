#!/usr/bin/env python

from __future__ import absolute_import

import json
import urllib2

def check_ide(target, helper):
    baseurl = target.baseurl + 'ide/'
    with helper.checking('frontpage'):
        urllib2.urlopen(baseurl)

    login_url = baseurl + 'control.php/auth/authenticate'
    login_data = json.dumps({
        'username': target.username,
        'password': target.password,
    })
    with helper.checking('login'):
        page = urllib2.urlopen(login_url, login_data)
        data = json.load(page)
        error = data.get('error')
        if error:
            raise Exception(error)

check_ide.name = 'IDE'
