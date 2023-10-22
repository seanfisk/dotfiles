# -*- coding: utf-8 -*-
"""Detect and configure gibo."""

import waflib

def configure(ctx):
    ctx.find_program('gibo', mandatory=False)

def build(ctx):
    # Auto-completion detection is programmed specifically for Homebrew.
    if not (ctx.env.GIBO and ctx.env.BREW):
        return

    gibo_brew_prefix = ctx.cmd_and_log(
        ctx.env.BREW + ['--prefix', 'gibo'],
        quiet=waflib.Context.STDOUT).rstrip()
    ctx.add_shell_rc_node(ctx.root.find_node([
        gibo_brew_prefix, 'etc', 'bash_completion.d', 'gibo']),
                          'bash')
    ctx.add_shell_rc_node(ctx.root.find_node([
        gibo_brew_prefix, 'share', 'zsh', 'site-functions', '_gibo']), 'zsh')
