#!/usr/bin/env python

from __future__ import absolute_import

import json
import urllib2

def check_comp_api(target, helper):
    baseurl = target.baseurl + 'comp-api/'
    with helper.checking('root'):
        page = urllib2.urlopen(baseurl)
        links = json.load(page)

    for item, url in links.items():
        with helper.checking(item):
            urllib2.urlopen(target.baseurl + url)

check_comp_api.name = "SRComp-HTTP"
