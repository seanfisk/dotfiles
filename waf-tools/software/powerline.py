# -*- coding: utf-8 -*-
"""Detect and configure Powerline."""

from os.path import join
from shlex import quote as shquote
import json

import waflib
from waflib.Configure import conf

@conf
def get_powerline_path(self, relpath):
    """Get the absolute path to a file in the Powerline package given a
    relative path.
    """
    return self.cmd_and_log(
        self.env.SYSTEM_PYTHON + [
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

    def _make_bash_powerline(tsk):
        tsk.outputs[0].write('''{powerline_daemon} --quiet
POWERLINE_BASH_CONTINUATION=1
POWERLINE_BASH_SELECT=1
source {powerline_file}
'''\
        .format(
            powerline_daemon=ctx.shquote_cmd(tsk.env.POWERLINE_DAEMON),
            powerline_file=shquote(ctx.get_powerline_path(join(
                'bindings', 'bash', 'powerline.sh'))),
        ))

    def _make_zsh_powerline(tsk):
        tsk.outputs[0].write('''{powerline_daemon} --quiet
source {powerline_file}
'''\
        .format(
            powerline_daemon=ctx.shquote_cmd(tsk.env.POWERLINE_DAEMON),
            powerline_file=shquote(ctx.get_powerline_path(join(
                'bindings', 'zsh', 'powerline.zsh'))),
        ))

    for shell in ctx.env.AVAILABLE_SHELLS:
        out_node = ctx.path.find_or_declare('powerline.' + shell)
        ctx.add_shell_rc_node(out_node, shell)
        rule = locals()['_make_{}_powerline'.format(shell)]
        ctx(rule=rule, target=out_node, vars=['POWERLINE_DAEMON'])

    # Instead of templating the config file and dealing with possible escaping
    # issues, we just dump it with the json module.
    out_node = ctx.path.find_or_declare([
        'dotfiles', 'config', 'powerline', 'config.json'])

    @ctx.rule(target=out_node, vars=['POWERLINE_SEGMENTS_PATH'])
    def _make_powerline_config(tsk):
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

@waflib.TaskGen.extension('.json')
def process_json(tsk_gen, node):
    """Install Powerline configuration files after processing."""
    tsk_gen.bld.install_dotfile(node)
