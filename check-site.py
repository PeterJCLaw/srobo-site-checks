#!/usr/bin/env python

from __future__ import print_function

import argparse
import base64
import contextlib
from collections import namedtuple, OrderedDict
from BeautifulSoup import BeautifulSoup
from getpass import getpass
import json
import sys
import urllib
import urllib2

DEFAULT_HOST = 'www.studentrobotics.org'
URL_TEMPLATE = "https://{0}/"
FAIL = '\033[91m'
ENDC = '\033[0m'

Target = namedtuple('Target', ['host', 'baseurl', 'username', 'password'])

class CheckHelper(object):
    def __init__(self, inner, indent):
        self._inner = inner
        self._indent = indent
        self._first_time = True

    def checking(self, desc):
        if self._first_time:
            print()
            self._first_time = False
        return self._inner.checking(desc, self._indent)

    @property
    def was_called(self):
        return not self._first_time

class Checker(object):
    def __init__(self, checks):
        self._checks = checks

    @contextlib.contextmanager
    def checking(self, desc, indent = ''):

        print("{0}Checking {1}...".format(indent, desc), end=' ')
        sys.stdout.flush()
        check_helepr = CheckHelper(self, indent + '  ')
        try:
            yield check_helepr
        except Exception as e:
            print(FAIL, e, ENDC, end = '')
            self._fail_count += 1
        else:
            if not check_helepr.was_called:
                # If the helper was called then there are children,
                # each of which has already reported their status.
                # There's no summary mechanism yet so we only print
                # anything here if there were no children and we
                # can be sure of the result.
                print("PASS", end = '')

        if not check_helepr.was_called:
            # Just a top level item, need to print a newline
            print()
        else:
            sys.stdout.flush()

    def run_checks(self, target):
        self._fail_count = 0
        for title, check_handler in self._checks:
            with self.checking(title) as helper:
                check_handler(target, helper)
        return self._fail_count

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

def check_comp_api(target, helper):
    baseurl = target.baseurl + 'comp-api/'
    with helper.checking('root'):
        page = urllib2.urlopen(baseurl)
        links = json.load(page)

    for item, url in links.items():
        with helper.checking(item):
            urllib2.urlopen(target.baseurl + url)

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

parser = argparse.ArgumentParser()
parser.add_argument("--host",
                    default=DEFAULT_HOST,
                    help="The host to check (default: {0})".format(DEFAULT_HOST))
parser.add_argument("--password",
                    help="The password for the given user. If not provided " \
                         "on the command line the user will be prompted for it")
parser.add_argument("username",
                    help="The username to login with (where applicable)")
args = parser.parse_args()

passwd = args.password or getpass("Password for {0}@{1}: ".format(args.username, args.host))

checker = Checker([
    ('Website', check_website),
    ('SRComp-HTTP', check_comp_api),
    ('Forums', check_forums),
    ('IDE', check_ide),
    ('Userman', check_userman),
])

baseurl = URL_TEMPLATE.format(args.host)
target = Target(args.host, baseurl, args.username, passwd)
fail_count = checker.run_checks(target)

exit(fail_count)
