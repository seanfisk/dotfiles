# -*- coding: utf-8 -*-
"""Detect and configure thefuck."""

import subprocess
from pipes import quote as shquote

def configure(ctx):
    ctx.find_program('thefuck', var='THEFUCK', mandatory=False)

def _make_alias(tsk):
    out_node = tsk.outputs[0]
    shell = out_node.suffix()[1:]
    with open(out_node.abspath(), 'w') as output_file:
        # thefuck does automatic shell detection, so run it in the specified
        # shell. Note that we are *not* using e.g.,
        #
        #     bash -c 'thefuck --alias'
        #
        # because this [apparently] causes the shell to exec directly rather
        # than forking, which messes up the parent process detection code of
        # thefuck. Instead, we are feeding the input via stdin.
        proc = subprocess.Popen(
            tsk.env[shell.upper()], stdin=subprocess.PIPE, stdout=output_file,
            # Allows stdin and stdout to be text instead of bytes.
            universal_newlines=True)
        proc.communicate(shquote(tsk.env.THEFUCK[0]) + ' --alias\n')
    return proc.returncode

def build(ctx):
    if not ctx.env.THEFUCK:
        return

    for shell in ctx.env.AVAILABLE_SHELLS:
        out_node = ctx.path.find_or_declare('thefuck.' + shell)
        ctx.add_shell_rc_node(out_node, shell)
        ctx(rule=_make_alias, target=out_node, vars=[shell.upper(), 'THEFUCK'])
