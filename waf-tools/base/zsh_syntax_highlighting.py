# -*- coding: utf-8 -*-
"""Detect and configure Zsh syntax highlighting."""

from os.path import join

import waflib
from waflib.Errors import WafError

def configure(ctx):
    prefix = False
    if ctx.env.BREW:
        try:
            prefix = join(
                ctx.cmd_and_log(
                    ctx.env.BREW + ['--prefix', 'zsh-syntax-highlighting'],
                    quiet=waflib.Context.STDOUT).rstrip(),
                'share', 'zsh-syntax-highlighting')
        except WafError:
            pass
    ctx.msg('Checking for zsh-syntax-highlighting', prefix)
    ctx.env.ZSH_SYNTAX_HIGHLIGHTING_PREFIX = prefix

def build(ctx):
    if not (ctx.env.ZSH and ctx.env.ZSH_SYNTAX_HIGHLIGHTING_PREFIX):
        return

    # We can't simply dump the contents of zsh-syntax-highlighting.zsh into our
    # .zshrc because that file looks for files in its own directory.
    out_node = ctx.path.find_or_declare('zsh-syntax-highlighting.zsh')
    ctx.add_shell_rc_node(out_node, 'zsh')
    @ctx.rule(target=out_node, vars='ZSH_SYNTAX_HIGHLIGHTING_PREFIX')
    def _make_syntax_file(tsk):
        with open(tsk.outputs[0].abspath(), 'w') as out_file:
            out_file.write(ctx.shquote_cmd(['source', join(
                tsk.env.ZSH_SYNTAX_HIGHLIGHTING_PREFIX,
                'zsh-syntax-highlighting.zsh')]))
    # This adds this environment variable to other shells (e.g., Bash), too,
    # but whatever.
    ctx.env.SHELL_ENV['ZSH_HIGHLIGHT_HIGHLIGHTERS_DIR'] = join(
        ctx.env.ZSH_SYNTAX_HIGHLIGHTING_PREFIX, 'highlighters')
