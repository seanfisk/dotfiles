"""Detect and configure tmux."""

from pipes import quote as shquote
from os.path import join


def configure(ctx):
    ctx.find_program('tmux', mandatory=False)


def build(ctx):
    if not ctx.env.TMUX:
        return
    ctx.add_shell_rc_node(ctx.path.find_resource([
        'shell', 'tmux.sh']))

    # TODO: This doesn't really handle a case when zsh is not available.
    default_shell = 'zsh'
    # Workaround for Mac OS X pasteboard, see
    # https://github.com/ChrisJohnsen/tmux-MacOSX-pasteboard
    # Don't pass -l; we don't want a login shell.
    default_command = shquote(
        'reattach-to-user-namespace {}'.format(default_shell) if ctx.env.MACOSX
        else default_shell)
    in_node = ctx.path.find_resource(['dotfiles', 'tmux.conf.in'])
    out_node = in_node.change_ext(ext='.conf', ext_in='.conf.in')

    powerline_commands = ''
    if ctx.env.POWERLINE:
        # Powerline should be able to find this on the PATH. But just in
        # case it's not, and maybe to save a little bit on execution, tell
        # Powerline where it is with this environment variable.
        ctx.env.SHELL_ENV['POWERLINE_CONFIG_COMMAND'] = (
            ctx.env.POWERLINE_CONFIG_)
        tmux_powerline_file = ctx.get_powerline_path(
            join('bindings', 'tmux', 'powerline.conf'))
        powerline_commands = '''run-shell "{powerline_daemon} --quiet"
source "{tmux_powerline_file}"
'''\
        .format(
            powerline_daemon=ctx.shquote_cmd(ctx.env.POWERLINE_DAEMON),
            tmux_powerline_file=tmux_powerline_file,
        )

    ctx(features='subst',
        source=in_node,
        target=out_node,
        DEFAULT_COMMAND=default_command,
        POWERLINE_COMMANDS=powerline_commands)
    ctx.install_dotfile(out_node)

    if ctx.env.LSOF:
        # List my tmux sockets
        ctx.env.SHELL_ALIASES['mytmux'] = (
            shquote(ctx.env.LSOF[0]) +
            ' -u "$(id -un)" -a -U | grep \'^tmux\'')
