# -*- coding: utf-8 -*-
"""Detect and configure SQLite."""

def configure(ctx):
    ctx.find_program('sqlite3', var='SQLITE', mandatory=False)

def build(ctx):
    if not ctx.env.SQLITE:
        return
    ctx.env.SHELL_ALIASES['sqlite'] = ctx.shquote_cmd(
        # We used to use -header -column, but this cuts off values if the width
        # is too small.
        ctx.env.SQLITE + ['-line', '-nullvalue', 'NULL'])
