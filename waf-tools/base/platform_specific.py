# -*- coding: utf-8 -*-
"""Detect the system type and set variables."""

from os.path import join
import platform
import tempfile
import plistlib

from waflib.Configure import conf

SYSTEM_OS_MAPPING = {
    'Linux': 'LINUX',
    'Darwin': 'MACOSX',
}

# OS X only, uses launchd
@conf
def install_launch_agent(self, node):
    """Install a user-level launchd launch agent. OS X only.

    :param node: a node representing a plist
    :type node: waflib.Node.Node
    """
    if not self.env.MACOSX:
        raise NotImplementedError('Launch agents are only supported on OS X.')
    self.install_as(
        join(self.env.LAUNCH_AGENTS_DIR, node.name),
        node,
        # Set the mode. The file must be writable *only by the user* otherwise
        # launchd will not load it. Be conservative and zero the group and
        # other permissions.
        chmod=0o0600)

# OS X-focused command, but supported on all platforms
@conf
def plist_dump_node(self, obj, node): # pylint: disable=unused-argument
    """Dump an object's plist representation to an output node.

    :param obj: object to dump
    :type obj: :class:`object`
    :param node: node to which to write the plist
    :type node: :class:`waflib.Node.Node`
    """
    with open(node.abspath(), 'wb') as out_file:
        plistlib.dump( # plistlib.dump is Python >= 3.4
            obj, out_file,
            sort_keys=False, # Keep our own order.
        )

# OS X only
@conf
def osx_app_locations(self, app):
    """Return paths of app bundles matching a specific name. Always returns
    ``False`` on non-OS X systems.

    :param app: name of the application
    :type app: :class:`str`
    """
    if not self.env.MACOSX:
        return False
    # Inspired by: http://apple.stackexchange.com/a/129943
    return self.cmd_and_log([
        'mdfind', 'kMDItemContentType = "com.apple.application-bundle"'
        ' && kMDItemDisplayName = {}'.format(
            repr(app))]).splitlines()

def configure(ctx):
    try:
        ctx.env[SYSTEM_OS_MAPPING[platform.system()]] = True
    except KeyError:
        ctx.fatal('Unrecognized system.')

    if ctx.env.MACOSX:
        ctx.env.LAUNCH_AGENTS_DIR = join(
            ctx.env.PREFIX, 'Library', 'LaunchAgents')
    elif ctx.env.LINUX:
        ctx.find_program('gnome-open', var='GNOME_OPEN', mandatory=False)

    # Not sure this exactly fits in here, but it differs platform-to-platform.
    ctx.env.TEMP_DIR = tempfile.gettempdir()

def build(ctx):
    if ctx.env.MACOSX:
        # Human readable file sizes, classify, and color
        ctx.env.SHELL_ALIASES['ls'] = 'ls -hFG'

        # ssh-agent handling code is not needed in Mac OS X because it is
        # handled by the operating system. However, it is useful to have an
        # alias to restart it in case it gets killed.
        ctx.env.SHELL_ALIASES['restart-ssh-agent'] = (
            'launchctl start org.openbsd.ssh-agent')

        # Open Xcode project.
        ctx.env.SHELL_ALIASES['openx'] = 'env -i open *.xcodeproj'
    elif ctx.env.LINUX:
        # Colorize, human readable file sizes, classify
        ctx.env.SHELL_ALIASES['ls'] = 'ls --color=always -hF'
        if ctx.env.GNOME_OPEN:
            ctx.env.SHELL_ALIASES['open'] = ctx.shquote_cmd(ctx.env.GNOME_OPEN)
        ctx.add_shell_rc_node(
            ctx.path.find_resource(['shell', 'gnu-linux.bash']))

        # Swap Caps Lock and Control under X11
        ctx.install_dotfile(ctx.path.find_resource(['dotfiles', 'Xkbmap']))
