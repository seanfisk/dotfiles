# -*- coding: utf-8 -*-
"""Detect and configure Blue Medora-related software."""

from os.path import join
from shlex import quote as shquote

def configure(ctx):
    locs = ctx.osx_app_locations('SelectStarter')
    ctx.env.SELECTSTARTER = locs[0] if locs else False
    ctx.msg('Checking for SelectStarter', ctx.env.SELECTSTARTER)

def build(ctx):
    if not ctx.env.SELECTSTARTER:
        return

    ctx.env.SHELL_ALIASES['ss'] = shquote(join(
        ctx.env.SELECTSTARTER, 'Contents', 'MacOS', 'SelectStarter'))
