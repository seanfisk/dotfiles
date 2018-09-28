# -*- coding: utf-8 -*-
"""Detect and configure directory listing software."""

def configure(ctx):
    ctx.find_program('ls')
    ctx.find_program('exa', mandatory=False)

def build(ctx):
    if ctx.env.EXA:
        # Prefer exa
        ctx.env.SHELL_ALIASES['ls'] = ctx.shquote_cmd(ctx.env.EXA +
                                                      ['--classify'])
        ctx.env.SHELL_ALIASES['l'] = 'ls --long --git'
        ctx.env.SHELL_ALIASES['la'] = 'l --all'
    else:
        # If no exa, use real ls
        if ctx.env.MACOSX:
            # Colorize, human readable file sizes, classify
            ctx.env.SHELL_ALIASES['ls'] = ctx.shquote_cmd(ctx.env.LS +
                                                          ['-GhF'])
        elif ctx.env.LINUX:
            # Colorize, human readable file sizes, classify
            ctx.env.SHELL_ALIASES['ls'] = ctx.shquote_cmd(
                ctx.env.LS + ['--color=always', '-hF'])

        ctx.env.SHELL_ALIASES['l'] = 'ls -l'
        ctx.env.SHELL_ALIASES['la'] = 'l -a'
