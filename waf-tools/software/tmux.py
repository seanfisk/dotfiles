# -*- coding: utf-8 -*-
"""Detect and configure tmux."""

from shlex import quote as shquote
from os.path import join

def configure(ctx):
    # The TMUX environment variable is used by tmux.
    ctx.find_program('tmux', var='TMUX_', mandatory=False)
    if ctx.env.MACOSX and ctx.env.TMUX_:
        # Workaround for Mac OS X pasteboard, see:
        # https://github.com/ChrisJohnsen/tmux-MacOSX-pasteboard
        # If we have tmux on Mac OS X, then reattach-to-user-namespace is
        # mandatory.
        ctx.find_program(
            'reattach-to-user-namespace', var='REATTACH_TO_USER_NAMESPACE')

def build(ctx):
    if not ctx.env.TMUX_:
        return

    ctx.add_shell_rc_node(ctx.path.find_resource(['shell', 'tmux.sh']))

    # Don't pass -l; we don't want a login shell.
    # Prefer Zsh, but go with Bash if necessary.
    shell = ctx.env.ZSH or ctx.env.BASH
    # Not exactly sure about the quoting rules in this config file...
    default_command = shquote(ctx.shquote_cmd(
        (ctx.env.REATTACH_TO_USER_NAMESPACE + shell)
        if ctx.env.REATTACH_TO_USER_NAMESPACE
        else shell))

    in_node = ctx.path.find_resource(['dotfiles', 'tmux.conf.in'])
    out_node = in_node.change_ext(ext='.conf', ext_in='.conf.in')

    powerline_commands = []
    if ctx.env.HAS_POWERLINE:
        tmux_powerline_file = ctx.get_powerline_path(
            join('bindings', 'tmux', 'powerline.conf'))
        if not ctx.env.POWERLINE_DAEMON_LAUNCHD:
            powerline_commands.append(
                # Not exactly sure about the quoting rules in this config
                # file...
                'run-shell ' + shquote(ctx.shquote_cmd(
                    ctx.env.POWERLINE_DAEMON + ['--quiet'])))

        powerline_commands.append(
            'source-file ' + shquote(tmux_powerline_file))

    ctx(features='subst',
        source=in_node,
        target=out_node,
        DEFAULT_COMMAND=default_command,
        POWERLINE_COMMANDS='\n'.join(powerline_commands))
    ctx.install_dotfile(out_node)

    if ctx.env.LSOF:
        # List my tmux sockets
        ctx.env.SHELL_ALIASES['mytmux'] = (
            shquote(ctx.env.LSOF[0]) +
            ' -u "$(id -un)" -a -U | grep \'^tmux\'')
