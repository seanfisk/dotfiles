# -*- coding: utf-8 -*-
"""Detect and configure thefuck."""

def configure(ctx):
    ctx.find_program('thefuck', var='THEFUCK', mandatory=False)

def _make_alias(tsk):
    out_node = tsk.outputs[0]
    shell = out_node.suffix()[1:]
    return tsk.generator.bld.feed_to_shell(
        shell, tsk.env.THEFUCK + ['--alias'], out_node)

def build(ctx):
    if not ctx.env.THEFUCK:
        return

    for shell in ctx.env.AVAILABLE_SHELLS:
        out_node = ctx.path.find_or_declare('thefuck.' + shell)
        ctx.add_shell_rc_node(out_node, shell)
        ctx(rule=_make_alias, target=out_node, vars=[shell.upper(), 'THEFUCK'])
