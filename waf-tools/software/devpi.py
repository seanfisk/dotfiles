# -*- coding: utf-8 -*-
"""Detect and configure devpi."""

import subprocess

def options(ctx):
    # Add a command-line option to explicity disable devpi.
    ctx.add_option('--disable-devpi', action='store_true', default=False,
                   help='Explicitly disable devpi')

def configure(ctx):
    if ctx.options.disable_devpi:
        ctx.msg('Checking for devpi', 'disabled', color='YELLOW')
        return

    if ctx.find_program('devpi-server', var='DEVPI_SERVER', mandatory=False):
        ctx.env.DEVPI_HOST = 'localhost' # devpi default
        ctx.env.DEVPI_PORT = 3141 # devpi default

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

        @ctx.rule(target=out_nodes, vars=[
            'DEVPI_SERVER', 'DEVPI_HOST', 'DEVPI_PORT'])
        def _make_devpi_gen_config(tsk):
            return tsk.exec_command(
                tsk.env.DEVPI_SERVER + [
                    '--gen-config',
                    '--host', tsk.env.DEVPI_HOST,
                    '--port', str(tsk.env.DEVPI_PORT),
                ],
                stdout=subprocess.DEVNULL)

        ctx.install_launch_agent(plist_node)

    devpi_pypi_url = 'http://{}:{}/root/pypi/+simple/'.format(
        ctx.env.DEVPI_HOST, ctx.env.DEVPI_PORT)
    # Ugh... this is ugly. Unfortunately double extensions are not fun.
    for relpath_list in [['pip', 'pip.conf'], ['pydistutils.cfg']]:
        relpath_list = ['dotfiles'] + relpath_list
        out_node = ctx.path.find_or_declare(relpath_list)
        relpath_list[-1] += '.in'
        in_node = ctx.path.find_resource(relpath_list)
        ctx(features='subst',
            source=in_node,
            target=out_node,
            DEVPI_PYPI_URL=devpi_pypi_url)

        ctx.install_dotfile(out_node)
