# -*- coding: utf-8 -*-
"""Detect and configure Firefox shell aliases."""

def configure(ctx):
    locs = ctx.osx_app_locations('Firefox')
    ctx.msg('Checking for Firefox', locs[0] if locs else False)
    ctx.env.FIREFOX = locs[0]

def build(ctx):
    if not ctx.env.FIREFOX:
        return

    ctx.env.SHELL_ALIASES['fx'] = ctx.shquote_cmd([
        'open', '-a', ctx.env.FIREFOX])
