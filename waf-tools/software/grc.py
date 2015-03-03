# -*- coding: utf-8 -*-
"""Detect and configure grc, the generic colouriser."""

import os.path

def configure(ctx):
    ctx.env.HAS_GRC = all([
        ctx.find_program('grc', mandatory=False),
        ctx.find_program('grcat', mandatory=False),
    ])

    if not ctx.env.HAS_GRC:
        return

    # Based on the rc file included with the grc brew formula; run
    # 'brew edit grc' to see it.
    grc_tool_names = [
        'as',
        'df',
        'diff',
        'dig',
        'ld',
        'make',
        'mount',
        'netstat',
        'ping',
        'ps',
        'traceroute',
        'traceroute6',
    ]
    # ifconfig has problems and hangs on OS X for some reason.
    if not ctx.env.MACOSX:
        grc_tool_names.append('ifconfig')

    ctx.env.GRC_TOOLS = []
    # Guarantee a stable build order by sorting.
    for name in sorted(grc_tool_names):
        path = ctx.find_program(name, mandatory=False)
        if path:
            ctx.env.GRC_TOOLS.append(path)

def build(ctx):
    if not ctx.env.HAS_GRC:
        return

    alias = 'colorify'
    ctx.env.SHELL_ALIASES[alias] = ctx.shquote_cmd(
        ctx.env.GRC + [
            '--stdout', '--stderr', # redirect both stdout and stderr
            # The default is '--color=on'. '--color=auto' will colorize only
            # when the output is a tty. However, we sometimes we like to pipe
            # to a pager which can accept color. If no color is wanted, we can
            # always run 'command <command>', etc.
        ])
    for path in ctx.env.GRC_TOOLS:
        name = os.path.basename(path[0])
        # Override the tool with an alias.
        ctx.env.SHELL_ALIASES[name] = ctx.shquote_cmd(['colorify'] + path)

    # configure doesn't have a path, but we'll create some aliases.

    # Running in the same directory.
    ctx.env.SHELL_ALIASES['configure'] = ctx.shquote_cmd([
        'colorify', './configure'])
    # Running in a subdirectory of the source directory.
    ctx.env.SHELL_ALIASES['uconfigure'] = ctx.shquote_cmd([
        'colorify', '../configure'])
