# -*- coding: utf-8 -*-
"""Detect and configure Chef."""

def configure(ctx):
    ctx.find_program('chef-client', var='CHEF_CLIENT', mandatory=False)

def build(ctx):
    if not ctx.env.CHEF_CLIENT:
        return
    # This isn't actually much shorter, but it matches our Windows PowerShell
    # alias. If we need to pass any "standard" options in the future (like '-A'
    # on Windows), we can do that here.
    ctx.env.SHELL_ALIASES['converge'] = ctx.shquote_cmd(ctx.env.CHEF_CLIENT)
