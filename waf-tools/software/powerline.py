# -*- coding: utf-8 -*-
"""Detect and configure Powerline."""

import os
from os.path import join
from shlex import quote as shquote
import json

import waflib
from waflib.Configure import conf
import appdirs

POWERLINE_PACKAGE_NAME = 'powerline-status'

@conf
def get_powerline_path(self, relpath):
    """Get the absolute path to a file in the Powerline package given a
    relative path.
    """
    return self.cmd_and_log(
        self.env.DEFAULT_PYTHON + [
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
    def _print_disabled_msg(msg):
        ctx.msg('Checking for Powerline', msg, color='YELLOW')

    if ctx.options.disable_powerline:
        _print_disabled_msg('disabled')
        return

    if not ctx.env.DEFAULT_PYTHON:
        _print_disabled_msg('disabled, default Python not found')
        return

    # Using Unicode characters outside of the Basic Multilingual Plane in a
    # UCS-2 Python with Powerline has various issues. Python 3.3 makes UCS-4
    # mandatory. If we have a UCS-2 Python, disable Powerline. The solution to
    # this is to install a UCS-4 Python to '.local'.
    #
    # References:
    # - https://github.com/seanfisk/dotfiles/issues/8
    # - https://github.com/Lokaltog/powerline/issues/1213
    ret = ctx.exec_command(ctx.env.DEFAULT_PYTHON + [
        '-c', 'import sys; sys.exit(0 if sys.maxunicode > 0xFFFF else 1)'])
    if ret != 0:
        _print_disabled_msg('disabled, default Python is UCS-2')
        return

    # Don't look in the directory to which the script is going to be symlinked.
    # (see the build phase for justification on why this is done).
    powerline_render_paths = ctx.environ['PATH'].split(os.pathsep)
    powerline_render_paths.remove(ctx.env.SCRIPTS_DIR)

    # Set this variable to give us an easy way to tell if we have Powerline.
    ctx.env.HAS_POWERLINE = all([
        ctx.find_program('powerline-daemon', var='POWERLINE_DAEMON',
                         mandatory=False),
        # Since 2.0, Powerline no longer uses the POWERLINE_CONFIG environment
        # variable.
        ctx.find_program('powerline-config', var='POWERLINE_CONFIG',
                         mandatory=False),
        ctx.find_program(
            'powerline-render', var='POWERLINE_RENDER', mandatory=False,
            path_list=powerline_render_paths,
        ),
        # This program is used in our 'lint' task, but it should be the
        # powerline-lint associated with the Powerline package we are currently
        # using (e.g., not a dev package for this repo).
        ctx.find_program('powerline-lint', var='POWERLINE_LINT',
                         mandatory=False)
    ])
    # This is not always present, depending on the capabilities of the
    # Python/system.
    ctx.find_program('powerline', var='POWERLINE_CLIENT', mandatory=False)

    ctx.env.POWERLINE_SEGMENTS_PATH = join(
        ctx.env.PREFIX, '.config', 'powerline')

    ctx.env.POWERLINE_LOG_PATH = join(
        appdirs.user_log_dir(appname='powerline'),
        # This name is pretty arbitrary. We aren't expecting any other logs
        # in this directory.
        'main.log')

def build(ctx):
    if not ctx.env.HAS_POWERLINE:
        return

    # TODO zpython is disabled until we can figure out how to install/use it
    # properly.
    #
    # The Homebrew package for zpython is old. It still uses the zpython branch
    # of ZyX's zsh repo, <https://bitbucket.org/ZyX_I/zsh>. However, it seems
    # that ZyX is doing all new development in
    # <https://bitbucket.org/ZyX_I/zpython>. We're not really comfortable
    # installing from Homebrew until this is fixed. And we've not had luck
    # compiling zpython in its current state. Furthermore, since zpython
    # depends on both Zsh and Python, it needs to be compiled with both. This
    # is particularly important for Python, as in the past we've had zpython
    # use the system Python with an old version of Powerline while we were
    # using another Python with a newer Powerline. If zpython is ever
    # re-enabled, we need to institute a check to make sure that zpython's
    # Python and the default Python under which Powerline is installed are the
    # same interpreter.
    ctx.env.SHELL_ENV['POWERLINE_NO_ZSH_ZPYTHON'] = '1'

    # These are overrides for where Powerline executables should be found.
    # These are used in case virtualenvs have Powerline installed (most will).
    # We want the Powerline executables from the default Python to be used.

    # Both these environment variables specify full paths to the executables,
    # so according to Powerline docs they should not be quoted.
    # http://powerline.readthedocs.org/en/2.0/configuration/local.html#prompt-command
    ctx.env.SHELL_ENV['POWERLINE_CONFIG_COMMAND'] = ctx.env.POWERLINE_CONFIG[0]
    if ctx.env.POWERLINE_CLIENT:
        # Used for shell and tmux.
        ctx.env.SHELL_ENV['POWERLINE_COMMAND'] = ctx.env.POWERLINE_CLIENT[0]

    # While overriding some executables with absolute paths in environment
    # variables is possible, the powerline client (see 'scripts/powerline.c')
    # uses execvp() to run 'powerline-render' if it can't connect to the daemon
    # (with the shell and Python clients doing similar things). This means that
    # 'powerline-render' needs to be on the PATH in some way, shape, or form.
    # We override this by symlinking it into the scripts directory, which
    # admittedly is kind of a hack.
    ctx.symlink_as(join(ctx.env.SCRIPTS_DIR, 'powerline-render'),
                   ctx.env.POWERLINE_RENDER[0])

    ctx.env.PYENV_VIRTUALENV_DEFAULT_PACKAGES.append(
        'git+https://github.com/powerline/powerline.git'
        '@b40e45a0e72eaebe4160aa0c1b5666f698ac8ac5#egg={0}'.format(
            POWERLINE_PACKAGE_NAME))

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

    @ctx.rule(target=out_node,
              vars=['POWERLINE_SEGMENTS_PATH', 'POWERLINE_LOG_PATH'])
    def _make_powerline_config(tsk):
        with open(tsk.outputs[0].abspath(), 'w') as out_file:
            json.dump(
                {
                    'common': {
                        'paths': [tsk.env.POWERLINE_SEGMENTS_PATH],
                        'log_file': tsk.env.POWERLINE_LOG_PATH,
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
