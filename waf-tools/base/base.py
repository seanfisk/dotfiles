# -*- coding: utf-8 -*-
"""Base helpers and functions."""

from os.path import join
from shlex import quote as shquote

import waflib
from waflib.Configure import conf

@conf
def install_dotfile(self, node):
    """Install a dotfile node."""
    # Strip the dotfiles/ directory (for both source and build nodes).
    relative_path_list = waflib.Node.split_path(node.relpath())[1:]
    relative_path_list[0] = '.' + relative_path_list[0]
    self.install_as(join(self.env.PREFIX, *relative_path_list), node)

@conf
def shquote_cmd(self, cmd): # pylint: disable=unused-argument
    """Shell-quote a command list.

    :param cmd: command list
    :type cmd: :class:`list`
    :return: quoted command
    :rtype: :class:`str`
    """
    return ' '.join(map(shquote, cmd))
