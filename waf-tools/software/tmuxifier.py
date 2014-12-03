# -*- coding: utf-8 -*-
"""Detect and configure tmuxifier."""

import os

def configure(ctx):
    # Don't conflict with the TMUXIFIER environment variable, which tmuxifier
    # sets to its base directory.
    ctx.find_program('tmuxifier', var='TMUXIFIER_', mandatory=False)

def _make_tmuxifier_file(tsk):
    out_node = tsk.outputs[0]
    shell = os.path.splitext(out_node.name)[1][1:]
    with open(out_node.abspath(), 'w') as out_file:
        ret = tsk.exec_command(
            tsk.env.TMUXIFIER_ + ['init', '-', shell], stdout=out_file)

    return ret

def build(ctx):
    if not ctx.env.TMUXIFIER_:
        return

    ctx.env.SHELL_ALIASES['mux'] = ctx.shquote_cmd(ctx.env.TMUXIFIER_)

    for shell in ctx.env.AVAILABLE_SHELLS:
        out_node = ctx.path.find_or_declare('tmuxifier.' + shell)
        ctx.add_shell_rc_node(out_node, shell)
        ctx(rule=_make_tmuxifier_file, target=out_node, vars=['TMUXIFIER_'])
