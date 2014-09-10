#!/usr/bin/env python
# -*- mode: python; coding: utf-8; -*-

# Waf build file
#
# Keep this file and all Waf tools Python 2/3 single-source compatible (using
# six when necessary).

import os
import fnmatch
from os.path import join

import waflib
from waflib.Configure import conf

# Waf constants
APPNAME = 'dotfiles'
VERSION = '0.1'
top = '.'
out = 'build'

def _python_modules_in_dir(dirpath):
    return [os.path.splitext(name)[0] for name in
            fnmatch.filter(os.listdir(dirpath), '*.py')]

# Script constants
WAF_BASE_TOOLS_DIR = 'waf_tools'
# Order matters here. All after 'platform_specific' are dependent on it. All
# after 'paths' are dependent on it.
WAF_BASE_TOOLS = [
    'jsminify',
    'platform_specific',
    'paths',
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
def load_tools(ctx):
    """Load project-specific base tools and software tools."""
    ctx.load(WAF_BASE_TOOLS, tooldir=WAF_BASE_TOOLS_DIR)
    ctx.load(WAF_SOFTWARE_TOOLS, tooldir=WAF_SOFTWARE_TOOLS_DIR)


@conf
def install_dotfile(ctx, node):
    """Install a dotfile node."""
    # Strip the dotfiles/ directory (for both source and build nodes).
    relative_path_list = waflib.Node.split_path(node.relpath())[1:]
    relative_path_list[0] = '.' + relative_path_list[0]
    ctx.install_as(join(ctx.env.PREFIX, *relative_path_list), node)


@conf
def install_script(ctx, script_basename):
    """Install a script given the basename."""
    ctx.install_files(join(ctx.env.PREFIX, 'bin'),
        [join('scripts', script_basename)],
        chmod=waflib.Utils.O755)


# @conf
# def ensure_loaded(ctx, tools):
#     """Load the tools if they are not yet loaded. This allows our own tools
#     to avoid loading tools on which they depend multiple times.
#     """
#     for tool in tools:
#         try:
#             waflib.Context.Context.tools[tool]
#         except KeyError:
#             ctx.load(
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

    # Build and install shell files.
    ctx.load(['shells'])
