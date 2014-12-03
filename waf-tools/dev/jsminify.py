# -*- coding: utf-8 -*-
"""Set up tasks for the JavaScript minifier."""

# slimit is another choice which looks more full-featured than jsmin, but
# slimit hasn't had a release in a while.

# We can't name this file jsmin.py because of this import :/
from jsmin import jsmin
import waflib

def _minify_javascript(tsk):
    # Powerline doesn't like Unicode, so this needs to be all ASCII.
    encoding = 'ascii'
    tsk.outputs[0].write(jsmin(tsk.inputs[0].read(encoding=encoding)),
                         encoding=encoding)

waflib.TaskGen.declare_chain(
    name='jsmin',
    rule=_minify_javascript,
    ext_in='.cjson',
    ext_out='.json',
)
