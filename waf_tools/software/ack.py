# -*- coding: utf-8 -*-
"""Detect and configure Ack and Ag."""

def configure(ctx):
    ctx.find_program('ack', mandatory=False)
    ctx.find_program('ag', mandatory=False)

def build(ctx):
    if ctx.env.ACK:
        # Just 'less' is fine; we don't need to pass 'less -R' to get colors to
        # work.
        ctx.env.SHELL_ALIASES['ackp'] = ctx.shquote_cmd(
            ctx.env.ACK + ['--pager=less'])
        ctx.install_dotfile(ctx.path.find_resource(['dotfiles', 'ackrc']))

        if ctx.env.GIT:
            # Note: by default `git ls-files' only shows tracked files.
            ctx.env.SHELL_ALIASES['ackg'] = (
                'git ls-files | {} --files-from=-'.format(
                    ctx.shquote_cmd(ctx.env.ACK)))
            ctx.env.SHELL_ALIASES['ackpg'] = (
                'git ls-files | ackp --files-from=-')

    if ctx.env.AG:
        # Just 'less' is fine; we don't need to pass 'less -R' to get colors to
        # work.
        ctx.env.SHELL_ALIASES['agp'] = ctx.shquote_cmd(
            ctx.env.AG + ['--pager less'])
        # ag doesn't support `--files-from'. Too bad.
