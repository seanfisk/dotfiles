"""Detect and manipulate paths.

This module specifically addresses the PATH, MANPATH, and INFOPATH variables.
"""

import os
import platform
from os.path import join
from pipes import quote as shquote
import subprocess

from waflib.Configure import conf


def configure(ctx):
    """Create our setup's "default" paths. These are paths that are used
    regardless of the existence of any other tools. However, these paths can
    include paths needed to find those tools.
    """
    ctx.env.PATH_VARS = ['PATH', 'MANPATH', 'INFOPATH']

    # Set up paths to check for "system" tools, like Python. The '.local' path
    # allows us to override the "system" tools as a user.
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
    ctx.add_to_path_var('PATH', join(ctx.env.PREFIX, 'bin'))

    # If rbenv and pyenv are installed to the home directory,
    # add_path_hierarchy will find their directories. If they are installed
    # using Homebrew, they will be found in /usr/local/.
    ctx.add_path_hierarchy(join(ctx.env.PREFIX, '.pyenv'))
    ctx.add_path_hierarchy(join(ctx.env.PREFIX, '.rbenv'))

    # System Python and Python user base.
    ctx.find_program(
        'python',
        var='SYSTEM_PYTHON',
        path_list=ctx.env.SYSTEM_PATHS,
        mandatory=False)
    if ctx.env.SYSTEM_PYTHON:
        # Just assume ascii; should be fine. This needs to be a string for Waf.
        user_base = str(subprocess.check_output([
            ctx.env.SYSTEM_PYTHON, '-m', 'site', '--user-base'])
            .decode('ascii').rstrip())
        ctx.add_path_hierarchy(user_base)

    # Emacs.app on Mac OS X contains some paths in some weird places.
    if ctx.env.MACOSX:
        emacs_app_contents = '/Applications/Emacs.app/Contents'

        # The bin directories look like this:
        #
        #     $ ls /Applications/Emacs.app/Contents/MacOS | grep bin
        #     bin-i386-10.5/
        #     bin-powerpc-10.4/
        #     bin-x86_64-10.5/
        #     bin-x86_64-10.7/
        #     bin-x86_64-10.9/
        #
        release, _, machine = platform.mac_ver()
        try:
            major, minor, patch = release.split('.')
        except ValueError:
            ctx.fatal("Couldn't determine Mac OS X version.")
        bin_dir_name = 'bin-{machine}-{release_major_minor}'.format(
            machine=machine,
            release_major_minor='{0}.{1}'.format(major, minor))
        ctx.add_to_path_var('PATH', join(
            emacs_app_contents, 'MacOS', bin_dir_name))

        # man and info directories
        resources_dir = join(emacs_app_contents, 'Resources')
        ctx.add_to_path_var('MANPATH', join(resources_dir, 'man'))
        ctx.add_to_path_var('INFOPATH', join(resources_dir, 'info'))

    # Add hierarchies.
    # Even though /usr/bin is probably already in the PATH, it is helpful to
    # add /usr so that INFOPATH gets correctly populated.
    for hier in ctx.env.SYSTEM_HIERARCHIES:
        ctx.add_path_hierarchy(hier)

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
            ('PATH', ctx.execute_in_clean_bash('echo $PATH')),
            ('MANPATH', ctx.execute_in_clean_bash('man --path')),
            ('INFOPATH', ctx.execute_in_clean_bash('echo $INFOPATH'))]:
        path_split = default_path_str.split(os.pathsep)
        if path_split != ['']:
            for path in path_split:
                ctx.add_to_path_var(var, path)

    # Write the paths to this current process' environment so that the
    # configuration uses these paths to find utilities (mostly important for
    # PATH, of course).
    ctx.write_paths_to_proc_env()


@conf
def add_to_path_var(ctx, var, path):
    """Add ``path`` to the context variable specified by ``var`` if the path
    exists."""
    if os.path.isdir(path):
        ctx.msg('Adding to ' + var, path)
        # append_unique is O(n) which sucks, but there aren't that many paths
        # and it's only run at configuration, so it doesn't really need to be
        # too performant. For a performant way (that we used before
        # simplifying), check out orderedset on PyPi.
        ctx.env.append_unique(var, path)


@conf
def execute_in_clean_bash(ctx, command):
    """Execute a command in the system Bash in a a "clean" environment."""
    # Only source /etc/profile in a clean environment. That should get us the
    # base paths (hopefully).
    profile_path = '/etc/profile'
    if not os.path.isfile(profile_path):
        ctx.fatal('Could not find profile file, {}'.format(profile_path))
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


@conf
def add_path_hierarchy(ctx, path):
    """Detect paths under a hierarchy and add them to the path variables."""
    ctx.add_to_path_var('PATH', join(path, 'bin'))
    ctx.add_to_path_var('PATH', join(path, 'sbin'))
    ctx.add_to_path_var('MANPATH', join(path, 'man'))
    ctx.add_to_path_var('MANPATH', join(path, 'share', 'man'))
    ctx.add_to_path_var('INFOPATH', join(path, 'share', 'info'))


@conf
def write_paths_to_proc_env(ctx):
    """Write the path variables in the context to the process' actual
    environment.
    """
    for var in ctx.env.PATH_VARS:
        os.environ[var] = os.pathsep.join(ctx.env[var])


@conf
def check_path_for_issues(ctx):
    # Check to see if os.pathsep is in any of the paths; that will make them
    # unusable.
    for path in ctx.env.PATH:
        if os.pathsep in path:
            ctx.fatal('Path cannot contain os.pathsep: ' + path)
