# -*- coding: utf-8 -*-
"""Detect and configure Firefox shell aliases."""

def configure(ctx):
    ctx.env.FIREFOX = ctx.osx_app_locations('Firefox')
    ctx.msg('Checking for Firefox',
            ctx.env.FIREFOX[0] if ctx.env.FIREFOX else False)

def build(ctx):
    if not ctx.env.FIREFOX:
        return

    ctx.env.SHELL_ALIASES['fx'] = ctx.shquote_cmd([
        'open', '-a', ctx.env.FIREFOX[0]])
