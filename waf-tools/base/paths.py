# -*- coding: utf-8 -*-
"""Detect and manipulate paths.

This module specifically addresses the PATH, MANPATH, and INFOPATH variables.
"""

import os
from os.path import join
import platform
from shlex import quote as shquote

from waflib.Configure import conf

@conf
def check_paths_for_issues(self):
    """Check to see if :data:`os.pathsep` is in any of the paths; that will
    make them unusable.
    """
    for var in self.env.PATH_VARS:
        for path in self.env[var]:
            if os.pathsep in path:
                self.fatal('Path cannot contain os.pathsep: ' + path)

def configure(ctx):
    """Create our setup's "default" paths. These are paths that are used
    regardless of the existence of any other tools. However, these paths can
    include paths needed to find those tools.
    """
    ctx.env.PATH_VARS = ['PATH', 'MANPATH', 'INFOPATH']

    # Set up paths to check for "system" tools. The '.local' path allows us to
    # override the "system" tools as a user.
    ctx.env.SYSTEM_HIERARCHIES = [
        join(ctx.env.PREFIX, '.local'),
        '/usr/local',
        '/usr',
    ]

    ctx.env.SYSTEM_PATHS = [
        join(hier, 'bin') for hier in ctx.env.SYSTEM_HIERARCHIES]

    # Initialize paths. Higher-priority paths come first.
    for var in ctx.env.PATH_VARS:
        ctx.env[var] = []

    # Add script directory.
    ctx.env.SCRIPTS_DIR = join(ctx.env.PREFIX, 'bin')
    _add_to_path_var(ctx, 'PATH', ctx.env.SCRIPTS_DIR)

    # If rbenv and pyenv are installed to the home directory,
    # add_path_hierarchy will find their directories. If they are installed
    # using Homebrew, they will be found in /usr/local/.
    _add_path_hierarchy(ctx, join(ctx.env.PREFIX, '.pyenv'))
    _add_path_hierarchy(ctx, join(ctx.env.PREFIX, '.rbenv'))

    # Add tmuxifier.
    _add_path_hierarchy(ctx, join(ctx.env.PREFIX, '.tmuxifier'))

    # Find the default Python, used for installing and running various
    # utilities.
    python = ctx.find_program(
        'python',
        var='DEFAULT_PYTHON',
        path_list=ctx.env.SYSTEM_PATHS,
        mandatory=False)
    if python:
        # If this is the system Python, add the user base. If it is not the
        # system Python, the user base should be '~/.local', which is already
        # on the paths.
        _add_path_hierarchy(ctx, ctx.cmd_and_log(
            python + ['-m', 'site', '--user-base']).rstrip())

    # Emacs.app on Mac OS X contains some paths in some weird places.
    if ctx.env.MACOSX:
        emacs_app_contents = '/Applications/Emacs.app/Contents'

        # The bin directories look like this:
        #
        #     $ ls /Applications/Emacs.app/Contents/MacOS | grep bin
        #     bin-i386-10_5/
        #     bin-powerpc-10_4/
        #     bin-x86_64-10_5/
        #     bin-x86_64-10_7/
        #     bin-x86_64-10_9/
        #

        # Pylint complains about this line for no good reason.
        release, _, machine = platform.mac_ver() # pylint: disable=unpacking-non-sequence
        try:
            major, minor, _ = release.split('.')
        except ValueError:
            ctx.fatal("Couldn't determine Mac OS X version.")
        bin_dir_name = 'bin-{machine}-{major}_{minor}'.format(
            machine=machine,
            major=major,
            minor=minor)
        _add_to_path_var(ctx, 'PATH', join(
            emacs_app_contents, 'MacOS', bin_dir_name))

        # man and info directories
        resources_dir = join(emacs_app_contents, 'Resources')
        _add_to_path_var(ctx, 'MANPATH', join(resources_dir, 'man'))
        _add_to_path_var(ctx, 'INFOPATH', join(resources_dir, 'info'))

    # Linuxbrew
    linuxbrew_path = os.path.expanduser('~/.linuxbrew')
    if ctx.env.LINUX and os.path.isdir(linuxbrew_path):
        ctx.env.LINUXBREW_PATH = linuxbrew_path
        _add_path_hierarchy(ctx, linuxbrew_path)

    # Add hierarchies.
    # Even though /usr/bin is probably already in the PATH, it is helpful to
    # add /usr so that INFOPATH gets correctly populated.
    for hier in ctx.env.SYSTEM_HIERARCHIES:
        _add_path_hierarchy(ctx, hier)

    # Finally, add system-default paths.
    #
    # To get the system defaults, we execute the system Bash in a clean
    # environment, sourcing only the system's shell profile.
    #
    # There is no guarantee that this will work. Here are some caveats:
    #
    # - A child processes typically inherits the environment from its parent.
    #   If the shell's parent typically changes a path variable, this will not
    #   be detected.
    # - If some joker decides to set paths in /etc/bash.bashrc, this will not
    #   be detected.
    #
    for var, default_path_str in [
            ('PATH', _execute_in_clean_bash(ctx, 'echo $PATH')),
            ('MANPATH', _execute_in_clean_bash(ctx, 'man --path')),
            ('INFOPATH', _execute_in_clean_bash(ctx, 'echo $INFOPATH'))]:
        path_split = default_path_str.split(os.pathsep)
        if path_split != ['']:
            for path in path_split:
                _add_to_path_var(ctx, var, path)

    # Write the paths to Waf's configuration environment so that the remainder
    # of the configuration uses these paths to find utilities. This is
    # primarily important for PATH. In Waf 1.8, the configuration context
    # gained its own clone of the environment, so we write to that instead of
    # the process's environment (os.environ). At this point, we have found it
    # unnecessary to also write the the process's environment during the
    # configuration phase (all important operations use the configuration
    # environment, or absolute paths) and the build phase (all operations use
    # absolute paths discovered in the configuration phase).
    for var in ctx.env.PATH_VARS:
        ctx.environ[var] = os.pathsep.join(ctx.env[var])

def _execute_in_clean_bash(ctx, command):
    """Execute a command in the system Bash in a a "clean" environment."""
    # Only source /etc/profile in a clean environment. That should get us the
    # base paths (hopefully).
    profile_path = '/etc/profile'
    if not os.path.isfile(profile_path):
        ctx.fatal('Could not find profile file: ' + profile_path)
    return ctx.cmd_and_log(
        [
            '/bin/bash', '--norc', '--noprofile', '-c',
            'source {profile_path}; {command}'.format(
                profile_path=shquote(profile_path),
                command=command,
            )
        ],
        # Clean environment (roughly equivalent to 'env -i command')
        env={},
    ).rstrip('\n')

def _add_to_path_var(ctx, var, path):
    """Add ``path`` to the context variable specified by ``var`` if the path
    exists."""
    if os.path.isdir(path):
        ctx.msg('Adding to ' + var, path)
        # append_unique is O(n) which sucks, but there aren't that many paths
        # and it's only run at configuration, so it doesn't really need to be
        # too performant. For a performant way (that we used before
        # simplifying), check out orderedset on PyPi.
        ctx.env.append_unique(var, path)

def _add_path_hierarchy(ctx, path):
    """Detect paths under a hierarchy and add them to the path variables."""
    _add_to_path_var(ctx, 'PATH', join(path, 'bin'))
    _add_to_path_var(ctx, 'PATH', join(path, 'sbin'))
    _add_to_path_var(ctx, 'MANPATH', join(path, 'man'))
    _add_to_path_var(ctx, 'MANPATH', join(path, 'share', 'man'))
    _add_to_path_var(ctx, 'INFOPATH', join(path, 'share', 'info'))
