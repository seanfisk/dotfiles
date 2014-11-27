# -*- coding: utf-8 -*-
"""Detect and configure Wget and Aria2."""

def configure(ctx):
    ctx.find_program('aria2c', mandatory=False)
    ctx.find_program('wget')  # Wget is mandatory!!!

def build(ctx):
    # Even though Wget is mandatory, still add the wget alias here to keep
    # things together, and in case that changes.
    #
    # Use the --content-disposition flag to allow sites "to describe what the
    # name of a downloaded file should be."
    ctx.env.SHELL_ALIASES['wget'] = ctx.shquote_cmd(
        ctx.env.WGET + ['--content-disposition'])
