
# TODO: work out why I didn't just write these as tests and then use
#       nosetest to do this bit.

from copy import copy
import imp
import os
import sys

PREFIX = 'check_'

def _load_checks(dir_path, filename):
    file_path = os.path.join(dir_path, filename)

    saved_path = copy(sys.path)
    sys.path.append(dir_path)

    imported_library = imp.load_source(filename, file_path)

    sys.path = saved_path

    checks = []
    for name in dir(imported_library):
        if name.startswith(PREFIX):
            check = getattr(imported_library, name)
            if hasattr(check, 'name'):
                check_name = check.name
            else:
                check_name = name[len(PREFIX):].title()
            checks.append( (check_name, check) )

    return checks

def load_checks(root):
    root = os.path.realpath(root)

    checks = []
    for filename in sorted(os.listdir(root)):
        if filename.endswith('.py'):
            checks += _load_checks(root, filename)
    return checks
