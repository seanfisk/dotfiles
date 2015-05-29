# -*- coding: utf-8 -*-
"""Detect and configure GNU coreutils."""

def configure(ctx):
    ctx.find_gnu_util('realpath', mandatory=False)

def build(ctx):
    if not ctx.env.REALPATH:
        return
    # The BSD utils are missing the extremely useful realpath utility. Create a
    # shorter alias which always points to the functional GNU version.
    ctx.env.SHELL_ALIASES['rp'] = ctx.shquote_cmd(ctx.env.REALPATH)
