# -*- coding: utf-8 -*-
"""Detect and configure RVM."""

from os.path import join

def configure(ctx):
    ctx.find_program(
        'rvm', path_list=[join(ctx.env.PREFIX, '.rvm', 'scripts')],
        mandatory=False)
    if ctx.env.RVM and ctx.env.RBENV:
        ctx.msg('Found both RVM and rbenv',
                'this combination is known to cause issues',
                color='YELLOW')

def build(ctx):
    if not ctx.env.RVM:
        return
    ctx.add_shell_rc_node(ctx.root.find_node(ctx.env.RVM[0]))
