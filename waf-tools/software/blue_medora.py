# -*- coding: utf-8 -*-
"""Detect and configure Blue Medora-related software."""

from os.path import join
from shlex import quote as shquote

def configure(ctx):
    locs = ctx.osx_app_locations('Frontier Services')
    ctx.env.FRONTIER_SERVICES = locs[0] if locs else False
    ctx.msg('Checking for Frontier Services', ctx.env.FRONTIER_SERVICES)

def build(ctx):
    if not ctx.env.FRONTIER_SERVICES:
        return

    ctx.env.SHELL_ALIASES['fr'] = shquote(join(
        ctx.env.FRONTIER_SERVICES, 'Contents', 'MacOS', 'Frontier Services'))
