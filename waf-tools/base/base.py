# -*- coding: utf-8 -*-
"""Base helpers and functions."""

from os.path import join
from shlex import quote as shquote

import waflib
from waflib.Configure import conf

@conf
def install_script(self, node):
    """Install a script node to the scripts directory."""
    self.install_files(self.env.SCRIPTS_DIR, node, chmod=waflib.Utils.O755)

@conf
def install_subst_script(self, script_basename, **kwargs):
    """Install a script node to the scripts directory, substituting any extra
    variables and values given in the keyword arguments."""
    script_in_node = self.path.find_resource([
        'scripts', script_basename + '.in'])
    script_out_node = script_in_node.change_ext('')
    self(features='subst',
         target=script_out_node,
         source=script_in_node,
         chmod=waflib.Utils.O755,
         **kwargs)
    self.install_script(script_out_node)

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
