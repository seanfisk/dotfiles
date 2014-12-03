# -*- mode: python; coding: utf-8; -*-

"""Waf build file"""

import os
import fnmatch
from os.path import join
from shlex import quote as shquote

import waflib
from waflib.Configure import conf

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
    return [os.path.splitext(name)[0] for name in
            fnmatch.filter(os.listdir(dirpath), '*.py')]

# Script constants
WAF_BASE_TOOLS_DIR = 'waf-tools'
# Order matters here. All after 'platform_specific' are dependent on it. All
# after 'paths' are dependent on it. 'shells' is dependent upon 'brew'.
WAF_BASE_TOOLS = [
    'log',
    'git_files',
    'jsminify',
    'platform_specific',
    'paths',
    'brew',
    'gnu_utils',
    'shells',
    'rbenv_pyenv',
]
WAF_SOFTWARE_TOOLS_DIR = join(WAF_BASE_TOOLS_DIR, 'software')
# Here, the order should not matter. Each of the stages should be independent.
# However, we sort to guarantee a stable order for the build. Different orders
# returned from os.listdir() can cause data structures to be built in different
# ways and cause unnecessary builds.
WAF_SOFTWARE_TOOLS = sorted(_python_modules_in_dir(WAF_SOFTWARE_TOOLS_DIR))

# Context helpers
@conf
def load_tools(self):
    """Load project-specific base tools and software tools."""
    self.load(WAF_BASE_TOOLS, tooldir=WAF_BASE_TOOLS_DIR)
    self.load(WAF_SOFTWARE_TOOLS, tooldir=WAF_SOFTWARE_TOOLS_DIR)

@conf
def install_dotfile(self, node):
    """Install a dotfile node."""
    # Strip the dotfiles/ directory (for both source and build nodes).
    relative_path_list = waflib.Node.split_path(node.relpath())[1:]
    relative_path_list[0] = '.' + relative_path_list[0]
    self.install_as(join(self.env.PREFIX, *relative_path_list), node)

@conf
def install_script(self, script_basename):
    """Install a script given the basename."""
    self.install_files(
        join(self.env.PREFIX, 'bin'),
        [join('scripts', script_basename)],
        chmod=waflib.Utils.O755)

@conf
def shquote_cmd(self, cmd): # pylint: disable=unused-argument
    """Shell-quote a command list.

    :param cmd: command list
    :type cmd: :class:`list`
    :return: quoted command
    :rtype: :class:`str`
    """
    return ' '.join(map(shquote, cmd))

# @conf
# def ensure_loaded(self, tools):
#     """Load the tools if they are not yet loaded. This allows our own tools
#     to avoid loading tools on which they depend multiple times.
#     """
#     for tool in tools:
#         try:
#             waflib.Context.Context.tools[tool]
#         except KeyError:
#             self.load(
#                 tools, tooldir=WAF_BASE_TOOLS_DIR + WAF_SOFTWARE_TOOLS_DIR)

def options(ctx):
    # Call the options() function in each of the tools.
    load_tools(ctx)
    # Override the default prefix of '/usr/local'.
    default_prefix = os.path.expanduser('~')
    ctx.add_option(
        '--prefix', default=default_prefix,
        help='installation prefix [default: {}]'.format(repr(default_prefix)))

def configure(ctx):
    ctx.find_program('pylint')

    # Call the configure() function in each of the tools.
    ctx.load_tools()

    # We'd like to check for this, but it's an rbenv-managed gem.
    #ctx.find_program('lolcat', mandatory=False)

    # After configuration, do some maintenance on the paths.
    ctx.check_path_for_issues()

def build(ctx):
    # Write all previously-configured paths to this process' environment.
    ctx.write_paths_to_proc_env()

    # Set up shell environment to be modified by other tools.
    ctx.setup_shell_defaults()

    # Call the build() function in each of the software tools.
    ctx.load(WAF_SOFTWARE_TOOLS, tooldir=WAF_SOFTWARE_TOOLS_DIR)

    # Build and install rbenv and pyenv-related files.
    ctx.load(['rbenv_pyenv'])

    # Add platform-specific shell environment.
    ctx.load(['platform_specific'])

    # Build and install shell files.
    ctx.load(['shells'])

class LintContext(waflib.Build.BuildContext):
    """Context for the lint task."""
    cmd = 'lint'
    fun = 'lint'

def lint(ctx):
    """runs Pylint to check style/common errors"""
    # Pylint can take a while to run, so print a message.
    print('Running lint...')

    def _is_py_file(path):
        base, ext = os.path.splitext(os.path.basename(path))
        return ext == '.py' or base == 'wscript'

    # Waf will take care of colors on Windows with its ansiterm module.
    checkers_dir_path = ctx.path.find_dir('pylint-checkers').abspath()
    retcode = ctx.exec_command(
        ctx.env.PYLINT +
        ['--load-plugins',
         ','.join(_python_modules_in_dir(checkers_dir_path))] +
        list(filter(_is_py_file, ctx.get_git_files())),
        # Add the current directory so that we can find our checkers modules.
        # Add the Waf modules dir so that pylint can find those modules.
        env={
            'PYTHONPATH': os.pathsep.join([
                waflib.Context.waf_dir, checkers_dir_path]),
        })
    if retcode == 0:
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
