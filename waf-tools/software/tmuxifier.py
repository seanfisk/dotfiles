# -*- coding: utf-8 -*-
"""Detect and configure tmuxifier."""

import os

def configure(ctx):
    # Don't conflict with the TMUXIFIER environment variable, which tmuxifier
    # sets to its base directory.
    if ctx.find_program('tmuxifier', var='TMUXIFIER_', mandatory=False):
        session_name = 'default'
        ctx.start_msg("Checking for tmuxifier '{}' session".format(
            session_name))
        has_default_session = session_name in ctx.cmd_and_log(
            ctx.env.TMUXIFIER_ + ['list-sessions']).splitlines()
        if has_default_session:
            ctx.env.TMUXIFIER_DEFAULT_SESSION = session_name
        ctx.end_msg(has_default_session)


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

    for shell in ctx.env.AVAILABLE_SHELLS:
        out_node = ctx.path.find_or_declare('tmuxifier.' + shell)
        ctx.add_shell_rc_node(out_node, shell)
        ctx(rule=_make_tmuxifier_file, target=out_node, vars=['TMUXIFIER_'])
