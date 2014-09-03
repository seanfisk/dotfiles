"""Helpers to find GNU utilities."""

from waflib.Configure import conf


@conf
def find_gnu_util(ctx, exe_name):
    """Search for a GNU utility, prefixed with 'g' on Mac OS X."""
    return ctx.find_program(
        ('g' if ctx.env.MACOSX else '') + exe_name, var=exe_name.upper())
