# -*- coding: utf-8 -*-
"""Base helpers and functions."""

from os.path import join
from shlex import quote as shquote

import waflib
from waflib.Configure import conf

@conf
def install_script(self, script_basename):
    """Install a script given the basename."""
    self.install_files(
        self.env.SCRIPTS_DIR,
        [join('scripts', script_basename)],
        chmod=waflib.Utils.O755)

@conf
def install_dotfile(self, node, **kwargs):
    """Install a dotfile node. Extra keywords are passed to ``install_as``."""
    # Strip the dotfiles/ directory (for both source and build nodes).
    relative_path_list = waflib.Node.split_path(node.relpath())[1:]
    relative_path_list[0] = '.' + relative_path_list[0]
    self.install_as(join(self.env.PREFIX, *relative_path_list), node, **kwargs)

@conf
def shquote_cmd(self, cmd): # pylint: disable=unused-argument
    """Shell-quote a command list.

    :param cmd: command list
    :type cmd: :class:`list`
    :return: quoted command
    :rtype: :class:`str`
    """
    return ' '.join(map(shquote, cmd))
