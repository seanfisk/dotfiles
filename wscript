# -*- mode: python; coding: utf-8; -*-

"""Waf build file"""

# Avoid having unnecessary public attributes in this file, else they will be
# picked up as Waf commands.

import os
import fnmatch
from os.path import join as _join
import itertools

import waflib

# Waf constants
APPNAME = 'dotfiles'
VERSION = '0.1'
top = '.' # pylint: disable=invalid-name
out = 'build' # pylint: disable=invalid-name

def _python_modules_in_dir(dirpath):
    """Find all Python modules within a directory.

    :param dirpath: path to directory
    :type dirpath: :class:`str`
    :return: list of Python module files
    :rtype: :class:`list` of :class:`str`
    """
    # Sort to guarantee a stable order for the build. Different orders returned
    # from os.listdir() can cause data structures to be built in different ways
    # and cause unnecessary builds.
    return sorted(os.path.splitext(name)[0] for name
                  in fnmatch.filter(os.listdir(dirpath), '*.py'))

# Script constants
WAF_TOOLS_DIR = 'waf-tools'
# Each of the dev tools are independent.
WAF_DEV_TOOLS_DIR = _join(WAF_TOOLS_DIR, 'dev')
WAF_DEV_TOOLS = _python_modules_in_dir(WAF_DEV_TOOLS_DIR)
# Order matters here. All after 'platform_specific' are dependent on it. All
# after 'paths' are dependent on it. 'shells' and 'rbenv_pyenv' are dependent
# upon 'brew'.
WAF_BASE_TOOLS_DIR = _join(WAF_TOOLS_DIR, 'base')
WAF_BASE_TOOLS = [
    'base',
    'platform_specific',
    'paths',
    'brew',
    'gnu_utils',
    'shells',
    'rbenv_pyenv',
    'logrotate',
]
WAF_SOFTWARE_TOOLS_DIR = _join(WAF_TOOLS_DIR, 'software')
# Each piece of software is independent.
WAF_SOFTWARE_TOOLS = _python_modules_in_dir(WAF_SOFTWARE_TOOLS_DIR)

def _load_tools(self):
    """Load all Waf tools."""
    self.load(WAF_DEV_TOOLS, tooldir=WAF_DEV_TOOLS_DIR)
    self.load(WAF_BASE_TOOLS, tooldir=WAF_BASE_TOOLS_DIR)
    self.load(WAF_SOFTWARE_TOOLS, tooldir=WAF_SOFTWARE_TOOLS_DIR)

# Context helpers
def options(ctx):
    # Call the options() function in each of the tools.
    _load_tools(ctx)
    # Override the default prefix of '/usr/local'.
    default_prefix = os.path.expanduser('~')
    ctx.add_option(
        '--prefix', default=default_prefix,
        help='installation prefix [default: %default]')

def configure(ctx):
    ctx.check_python_version(version=('3', '4'))

    ctx.find_program('pylint')

    # Call the configure() function in each of the tools.
    _load_tools(ctx)

    # We'd like to check for this, but it's an rbenv-managed gem.
    #ctx.find_program('lolcat', mandatory=False)

    # After configuration, check for issues.
    ctx.check_paths_for_issues()

def build(ctx):
    # Set up shell environment to be modified by other tools.
    ctx.setup_shell_defaults()

    # Call the build() function in each of the software tools.
    ctx.load(WAF_SOFTWARE_TOOLS, tooldir=WAF_SOFTWARE_TOOLS_DIR)

    # Build logrotate configuration file.
    ctx.load(['logrotate'])

    # Build and install rbenv and pyenv-related files.
    ctx.load(['rbenv_pyenv'])

    # Add platform-specific shell environment.
    ctx.load(['platform_specific'])

    # Build and install shell files.
    ctx.load(['shells'])

    if ctx.cmd == 'lint':
        ctx.add_post_fun(lint)

class LintContext(waflib.Build.BuildContext):
    """Context for the lint task."""
    cmd = 'lint'

def lint(ctx):
    """runs Pylint and powerline-lint to check style/common errors"""
    # Pylint can take a while to run, so print a message.
    ctx.to_log('Running pylint...\n')
    def _is_py_file(path):
        base, ext = os.path.splitext(os.path.basename(path))
        return ext == '.py' or base == 'wscript'
    # Waf will take care of colors on Windows with its ansiterm module.
    retcodes = ctx.exec_command(
        ctx.env.PYLINT + list(filter(_is_py_file, ctx.get_git_files())),
        # Add the current directory so that we can find our checkers modules.
        # Add the Waf modules dir so that pylint can find those modules.
        env={
            'PYTHONPATH': os.pathsep.join([
                ctx.srcnode.abspath(),
                waflib.Context.waf_dir,
            ]),
        })

    if ctx.env.POWERLINE_LINT:
        ctx.to_log('Running powerline-lint...\n')

        retcodes += ctx.exec_command(
            ctx.env.POWERLINE_LINT + list(itertools.chain.from_iterable(
                ['--config-path', path] for path in [
                    ctx.get_powerline_path('config_files'),
                    ctx.bldnode.find_dir([
                        'dotfiles', 'config', 'powerline']).abspath(),
                ])))

    if retcodes == 0:
        # http://patorjk.com/software/taag/#p=display&f=Small&t=PASSED
        ctx.log_success(r'''  ___  _   ___ ___ ___ ___
 | _ \/_\ / __/ __| __|   \
 |  _/ _ \\__ \__ \ _|| |) |
 |_|/_/ \_\___/___/___|___/
''')
    else:
        # http://patorjk.com/software/taag/#p=display&f=Small&t=FAILED
        ctx.log_failure(r'''  ___ _   ___ _    ___ ___
 | __/_\ |_ _| |  | __|   \
 | _/ _ \ | || |__| _|| |) |
 |_/_/ \_\___|____|___|___/
''')
