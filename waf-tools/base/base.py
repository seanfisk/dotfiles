# -*- coding: utf-8 -*-
"""Base helpers and functions."""

from os.path import join
from shlex import quote as shquote
import subprocess

import waflib
from waflib.Configure import conf

@conf
def concat_nodes(self, output_file, input_nodes): # pylint: disable=unused-argument
    """Write the contents of a list of nodes into an already-opened output
    file."""
    for input_node in input_nodes:
        print(file=output_file)
        with open(input_node.abspath()) as input_file:
            for line in input_file:
                output_file.write(line)

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
def dotfile_install_path(self, node):
    """Compute the install path of a dotfile node."""
    # Strip the dotfiles/ directory (for both source and build nodes).
    relative_path_list = waflib.Node.split_path(node.relpath())[1:]
    relative_path_list[0] = '.' + relative_path_list[0]
    return join(self.env.PREFIX, *relative_path_list)

@conf
def install_dotfile(self, node, **kwargs):
    """Install a dotfile node. Extra keywords are passed to ``install_as``."""
    self.install_as(self.dotfile_install_path(node), node, **kwargs)

@conf
def shquote_cmd(self, cmd): # pylint: disable=unused-argument
    """Shell-quote a command list.

    :param cmd: command list
    :type cmd: :class:`list`
    :return: quoted command
    :rtype: :class:`str`
    """
    return ' '.join(map(shquote, cmd))

@conf
def feed_to_shell(self, shell, cmd, out_node):
    """Feed a command to a shell, writing the output to a specified node.

    This is useful for commands like ``the-fuck --alias`` and ``brew
    command-not-found-init`` that do automatic shell detection. In these cases,
    we can't use, e.g.,

        bash -c 'cmd --opt arg'

    because this [apparently] causes the shell to exec directly rather than
    forking, which messes up the parent process detection. Instead, we are
    feeding the input via stdin.

    :param shell: shell to run, e.g. bash, zsh
    :type shell: :class:`str`
    :param cmd: command list
    :type cmd: :class:`list`
    :param out_node: node to which to write output
    :type out_node: waflib.Node.Node
    :return: exit code of the shell
    :rtype: :class:`int`
    """
    with open(out_node.abspath(), 'w') as output_file:
        proc = subprocess.Popen(
            self.env[shell.upper()], stdin=subprocess.PIPE, stdout=output_file,
            # Allows stdin and stdout to be text instead of bytes.
            universal_newlines=True)
        proc.communicate(self.shquote_cmd(cmd) + '\n')
    return proc.returncode
