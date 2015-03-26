#!/usr/bin/env python

from __future__ import print_function

import contextlib
from collections import namedtuple
import sys

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
