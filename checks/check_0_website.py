#!/usr/bin/env python

from __future__ import absolute_import

import urllib2

def check_website(target, helper):
    with helper.checking('homepage'):
        urllib2.urlopen(target.baseurl)

    with helper.checking('/docs'):
        urllib2.urlopen(target.baseurl + 'docs')

    with helper.checking('/404'):
        urllib2.urlopen(target.baseurl + '404')

    with helper.checking('/nope/nope'):
        try:
            urllib2.urlopen(target.baseurl + 'nope/nope')
        except urllib2.HTTPError as e:
            if e.code != 404:
                raise
        else:
            raise Exception("Should get a 404 loading the /nope/nope page!")
