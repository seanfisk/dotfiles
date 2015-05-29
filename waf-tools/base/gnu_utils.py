# -*- coding: utf-8 -*-
"""Helpers to find GNU utilities."""

from waflib.Configure import conf

@conf
def find_gnu_util(self, exe_name, **kwargs):
    """Search for a GNU utility, prefixed with 'g' on Mac OS X."""
    return self.find_program(('g' if self.env.MACOSX else '') + exe_name,
                             var=exe_name.upper(), **kwargs)
