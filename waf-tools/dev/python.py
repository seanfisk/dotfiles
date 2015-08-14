# -*- coding: utf-8 -*-

"""Check for Python version.

Waf has a built-in module to check for Python. This module differs from it in
the following ways:

- The Waf module finds the Python executable and checks that. This module
  checks the version of the currently-running Python interpreter.
- The Waf module checks for a minimum Python version. This module allows the
  user to provide their own comparison function.
- This module ignores environment variable hints.
- This module only checks the version of Python.
"""

import sys
import platform
import operator

from waflib.Configure import conf

@conf
def check_python_version(self, impl=None, version=(), cmp_=operator.ge):
    """Check for Python version. Very loosely based upon
    :meth:`waflib.Tools.python.check_python_version()`, but simplified and
    designed to check the currently running interpreter.

    :param impl: Python implementation as returned by
        :func:`platform.python_implementation()`
    :type impl: :class:`str`
    :param version: Partial or full version tuple as returned by
        :func:`platform.python_version_tuple()`
    :type version: :class:`tuple` of :class:`str`
    :param cmp_: Comparison operator for the version
    :type cmp_: :class:`func`
    """
    meets_requirements = (
        (impl is None or platform.python_implementation() == impl) and
        (version == () or cmp_(platform.python_version_tuple(), version)))
    required_version_string = '.'.join(version)
    required_name = (impl or 'Python') + (' ' if version else '') + (
        required_version_string)
    found_name = '{0} {1}'.format(
        platform.python_implementation(), platform.python_version())
    self.msg('Checking for ' + required_name,
             found_name if meets_requirements else False)
    if not meets_requirements:
        self.fatal('Expecting {0}, found {1}'.format(
            required_name, found_name))

    # Set the PYTHON configuration variable if successful. It is set as a list
    # following the lead of find_program() in Waf 1.8.
    self.env.PYTHON = [sys.executable]
