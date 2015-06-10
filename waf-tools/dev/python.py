# -*- coding: utf-8 -*-

"""Check for Python version.

Waf has some built-in ways to check for Python version.
However, the Python version only checks for a *minimum* version whereas we want
an exact version. The module test is OK, but relies on Waf Python
infrastructure (which we are not using). Our checks are simpler and ignore
environment variable hints, but they should get the job done.
"""

import sys
import platform

from waflib.Configure import conf

@conf
def check_python_version(self, impl=None, version=()):
    """Check for Python version. Very loosely based upon
    :meth:`waflib.Tools.python.check_python_version()`, but simplified and
    designed to check the currently running interpreter.

    :param impl: Python implementation as returned by
        :func:`platform.python_implementation()`
    :type impl: :class:`str`
    :param version: Partial or full version tuple as returned by
        :func:`platform.python_version_tuple()`
    :type version: :class:`tuple` of :class:`str`
    """
    meets_requirements = (
        (impl is None or platform.python_implementation() == impl) and
        platform.python_version_tuple()[:len(version)] == version)
    required_version_string = '.'.join(version)
    required_name = '{}{}{}'.format(
        impl or 'Python', ' ' if version else '', required_version_string)
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
