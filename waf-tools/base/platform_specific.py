# -*- coding: utf-8 -*-
"""Detect the system type and set variables."""

import platform

SYSTEM_OS_MAPPING = {
    'Linux': 'LINUX',
    'Darwin': 'MACOSX',
}

def configure(ctx):
    try:
        ctx.env[SYSTEM_OS_MAPPING[platform.system()]] = True
    except KeyError:
        ctx.fatal('Unrecognized system.')

    if ctx.env.LINUX:
        ctx.find_program('gnome-open', var='GNOME_OPEN', mandatory=False)

def build(ctx):
    if ctx.env.MACOSX:
        # Human readable file sizes, classify, and color
        ctx.env.SHELL_ALIASES['ls'] = 'ls -hFG'

        # ssh-agent handling code is not needed in Mac OS X because it is
        # handled by the operating system. However, it is useful to have an
        # alias to restart it in case it gets killed.
        ctx.env.SHELL_ALIASES['restart-ssh-agent'] = (
            'launchctl start org.openbsd.ssh-agent')

        # Open Xcode project.
        ctx.env.SHELL_ALIASES['openx'] = 'env -i open *.xcodeproj'
    elif ctx.env.LINUX:
        # Colorize, human readable file sizes, classify
        ctx.env.SHELL_ALIASES['ls'] = 'ls --color=always -hF'
        if ctx.env.GNOME_OPEN:
            ctx.env.SHELL_ALIASES['open'] = ctx.shquote_cmd(ctx.env.GNOME_OPEN)
        ctx.add_shell_rc_node(
            ctx.path.find_resource(['shell', 'gnu-linux.bash']))

        # Swap Caps Lock and Control under X11
        ctx.install_dotfile(ctx.path.find_resource(['dotfiles', 'Xkbmap']))
