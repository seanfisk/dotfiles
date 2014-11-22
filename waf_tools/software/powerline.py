"""Detect and configure Powerline."""

from os.path import join
from pipes import quote as shquote
import json

import waflib
from waflib.Configure import conf


@conf
def get_powerline_path(ctx, relpath):
    return ctx.cmd_and_log(
        ctx.env.SYSTEM_PYTHON + [
            '-c',
            'from pkg_resources import resource_filename; '
            "print(resource_filename('powerline', {}))"
            .format(repr(relpath))],
        # Don't print out the command or its output.
        quiet=waflib.Context.BOTH).rstrip()


def options(ctx):
    # Add a command-line option to explicity disable Powerline.
    ctx.add_option('--disable-powerline', action='store_true', default=False,
                   help='Explicitly disable Powerline')


def configure(ctx):
    if ctx.options.disable_powerline:
        ctx.msg('Checking for Powerline', 'disabled', color='YELLOW')
        return

    # We assume that Powerline is installed under the system Python. We
    # don't allow Waf to look in pyenv paths, so that's a decent
    # assumption.
    if not ctx.env.SYSTEM_PYTHON:
        ctx.fatal('Powerline must be installed under the system Python.')

    ctx.find_program('powerline-daemon', var='POWERLINE_DAEMON',
                     mandatory=False)
    # Powerline actually uses the POWERLINE_CONFIG environment variable, which
    # Waf will then detect. Change ours to avoid this.
    ctx.find_program('powerline-config', var='POWERLINE_CONFIG_',
                     mandatory=False)

    # Set this variable to give us an easy way to tell if we have Powerline.
    ctx.env.POWERLINE = (
        bool(ctx.env.POWERLINE_DAEMON) and bool(ctx.env.POWERLINE_CONFIG_))

    ctx.env.POWERLINE_SEGMENTS_PATH = join(
        ctx.env.PREFIX, '.config', 'powerline')


def build(ctx):
    if not ctx.env.POWERLINE:
        return

    ctx.env.PYENV_VIRTUALENV_DEFAULT_PACKAGES.append('powerline-status==1.2')

    bash_powerline_node = ctx.path.find_or_declare('powerline.bash')
    ctx.env.BASH_RC_NODES.append(bash_powerline_node)

    @ctx.rule(target=bash_powerline_node, vars=['POWERLINE_DAEMON'])
    def make_bash_powerline(tsk):
        bash_powerline_file = ctx.get_powerline_path(
            join('bindings', 'bash', 'powerline.sh'))
        tsk.outputs[0].write('''{powerline_daemon} --quiet
POWERLINE_BASH_CONTINUATION=1
POWERLINE_BASH_SELECT=1
source {bash_powerline_file}
'''\
        .format(
            powerline_daemon=ctx.shquote_cmd(tsk.env.POWERLINE_DAEMON),
            bash_powerline_file=shquote(bash_powerline_file),
        ))

    zsh_powerline_node = ctx.path.find_or_declare('powerline.zsh')
    ctx.env.ZSH_RC_NODES.append(zsh_powerline_node)

    @ctx.rule(target=zsh_powerline_node, vars=['POWERLINE_DAEMON'])
    def make_zsh_powerline(tsk):
        zsh_powerline_file = ctx.get_powerline_path(
            join('bindings', 'zsh', 'powerline.zsh'))
        tsk.outputs[0].write('''{powerline_daemon} --quiet
source {zsh_powerline_file}
'''\
        .format(
            powerline_daemon=ctx.shquote_cmd(tsk.env.POWERLINE_DAEMON),
            zsh_powerline_file=shquote(zsh_powerline_file),
        ))

    # Instead of templating the config file and dealing with possible escaping
    # issues, we just dump it with the json module.
    out_node = ctx.path.find_or_declare([
        'dotfiles', 'config', 'powerline', 'config.json'])

    @ctx.rule(target=out_node, vars=['POWERLINE_SEGMENTS_PATH'])
    def make_powerline_config(tsk):
        with open(tsk.outputs[0].abspath(), 'w') as out_file:
            json.dump(
                {
                    'common': {
                        'paths': [tsk.env.POWERLINE_SEGMENTS_PATH],
                    },
                    'ext': {
                        'shell': {'theme': 'sean'},
                        'tmux': {'theme': 'sean'},
                    },
                },
                out_file,
                # No spaces, 'cuz that extra 10 bytes is gonna kill me...
                separators=(',', ':'),
                # Dammit, I just added a bunch more bytes to *this* file!
            )

    ctx(source=ctx.path.ant_glob(
        'dotfiles/config/powerline/**/*.cjson') + [out_node])

    # Install segments file.
    ctx.install_dotfile(ctx.path.find_resource([
        'dotfiles', 'config', 'powerline', 'powerline_sean_segments.py']))


# Install Powerline configuration files after processing.
@waflib.TaskGen.extension('.json')
def process_json(tsk_gen, node):
    tsk_gen.bld.install_dotfile(node)
