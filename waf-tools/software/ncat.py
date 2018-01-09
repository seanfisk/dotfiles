# -*- coding: utf-8 -*-
"""Detect and configure Ncat."""

def configure(ctx):
    ctx.find_program('ncat', mandatory=False)

def build(ctx):
    if not ctx.env.NCAT:
        return
    ctx.env.SHELL_ALIASES['tcping'] = ctx.shquote_cmd(ctx.env.NCAT + [
        '--verbose',
        '-z',  # Zero-I/O mode, report connection status only
        '--wait', '0.1',  # seconds
    ])
