# -*- coding: utf-8 -*-
"""Detect and configure devpi."""

from os.path import join

DEVPI_PYPI_URL = 'http://localhost:3141/root/pypi/+simple/'

def configure(ctx):
    ctx.find_program('devpi-server', var='DEVPI_SERVER', mandatory=False)

def build(ctx):
    if not ctx.env.DEVPI_SERVER:
        return

    if ctx.env.MACOSX:
        # Install a launchd plist for devpi on Mac OS X.
        out_nodes = [
            ctx.path.find_or_declare(['gen-config', filename]) for filename in
            [
                'net.devpi.plist',
                'supervisor-devpi.conf',
                'nginx-devpi.conf',
                'crontab',
                'devpi.service',
            ]
        ]
        plist_node = out_nodes[0]

        @ctx.rule(target=out_nodes, vars=['DEVPI_SERVER'])
        def _make_devpi_gen_config(tsk):
            return tsk.exec_command(tsk.env.DEVPI_SERVER + ['--gen-config'])

        ctx.install_as(
            join(ctx.env.PREFIX, 'Library', 'LaunchAgents', plist_node.name),
            plist_node)

    # Ugh... this is ugly. Unfortunately double extensions are not fun.
    for relpath_list in [['pip', 'pip.conf'], ['pydistutils.cfg']]:
        relpath_list = ['dotfiles'] + relpath_list
        out_node = ctx.path.find_or_declare(relpath_list)
        relpath_list[-1] += '.in'
        in_node = ctx.path.find_resource(relpath_list)
        ctx(features='subst',
            source=in_node,
            target=out_node,
            DEVPI_PYPI_URL=DEVPI_PYPI_URL)

        ctx.install_dotfile(out_node)
