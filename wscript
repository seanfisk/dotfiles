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
WAF_BASE_TOOLS = ['platform_specific', 'paths', 'gnu_utils', 'shells']
WAF_SOFTWARE_TOOLS_DIR = join(WAF_BASE_TOOLS_DIR, 'software')
# Here, the order should not matter. Each of the stages should be independent.
WAF_SOFTWARE_TOOLS = _python_modules_in_dir(WAF_SOFTWARE_TOOLS_DIR)


# Context helpers
@conf
def load_tools(ctx):
    ctx.load(WAF_BASE_TOOLS, tooldir=WAF_BASE_TOOLS_DIR)
    ctx.load(WAF_SOFTWARE_TOOLS, tooldir=WAF_SOFTWARE_TOOLS_DIR)


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

    # Create list of dotfile nodes from the dotfiles/ directory to install.
    ctx.env.DOTFILE_NODES = []
    # Create list of scripts in the script/ directory to install to
    # $PREFIX/bin.
    ctx.env.SCRIPTS = []

    # Set up shell environment to be modified by other tools.
    ctx.setup_shell_defaults()

    # Call the build() function in each of the software tools.
    ctx.load(WAF_SOFTWARE_TOOLS, tooldir=WAF_SOFTWARE_TOOLS_DIR)

    # Build and install shell files.
    ctx.load(['shells'])

    # Install other dotfiles
    dotfiles_dir_node = ctx.path.find_dir('dotfiles')
    for node in ctx.env.DOTFILE_NODES:
        if node.is_src():
            relative_path = node.path_from(dotfiles_dir_node)
        elif node.is_bld():
            relative_path = node.bldpath()
        else:
            ctx.fatal('Dotfile node is not in source nor build directory.')
        ctx.install_as(join(ctx.env.PREFIX, '.' + relative_path), node)

    # Install scripts
    ctx.install_files(
        join(ctx.env.PREFIX, 'bin'),
        [join('scripts', basename) for basename in ctx.env.SCRIPTS],
        chmod=waflib.Utils.O755)
