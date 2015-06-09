# -*- coding: utf-8 -*-
"""Detect and configure thefuck."""

import os
import subprocess
from pipes import quote as shquote

def configure(ctx):
    ctx.find_program('thefuck-alias', var='THEFUCK_ALIAS', mandatory=False)

def _make_alias(tsk):
    out_node = tsk.outputs[0]
    shell = out_node.suffix()[1:]
    with open(out_node.abspath(), 'w') as output_file:
        # thefuck-alias does automatic shell detection, so run it in the
        # specified shell. Note that we are *not* using e.g., 'bash -c
        # thefuck-alias', because this [apparently] causes the shell to exec
        # directly rather than forking, which messes up the parent process
        # detection code of thefuck-alias. Instead, we are feeding the input
        # via stdin.
        proc = subprocess.Popen(
            tsk.env[shell.upper()], stdin=subprocess.PIPE, stdout=output_file,
            # Allows stdin and stdout to be text instead of bytes.
            universal_newlines=True)
        proc.communicate(shquote(tsk.env.THEFUCK_ALIAS[0]) + '\n')
    return proc.returncode

def build(ctx):
    if not ctx.env.THEFUCK_ALIAS:
        return

    for shell in ctx.env.AVAILABLE_SHELLS:
        out_node = ctx.path.find_or_declare('thefuck.' + shell)
        ctx.add_shell_rc_node(out_node, shell)
        ctx(rule=_make_alias, target=out_node, vars=[
            shell.upper(), 'THEFUCK_ALIAS'])
