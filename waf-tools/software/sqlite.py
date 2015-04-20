# -*- coding: utf-8 -*-
"""Detect and configure SQLite."""

def configure(ctx):
    ctx.find_program('sqlite3', var='SQLITE', mandatory=False)

def build(ctx):
    if not ctx.env.SQLITE:
        return
    ctx.env.SHELL_ALIASES['sqlite'] = ctx.shquote_cmd(
        ctx.env.SQLITE + ['-header', '-column', '-nullvalue', 'NULL'])
