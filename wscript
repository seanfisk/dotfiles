#!/usr/bin/env python
# -*- mode: python; coding: utf-8; -*-

# Waf build file
# Keep this file Python 2/3 single-source compatible

import os
from os.path import join
import platform
import subprocess
# Python 2/3 compat -- this is shlex.quote in Python 3
from pipes import quote as shquote
from collections import OrderedDict

import six
import waflib
from waflib.Configure import conf

# Waf constants
APPNAME = 'dotfiles'
VERSION = '0.1'
top = '.'
out = 'build'

# Script constants
SYSTEM = platform.system()
MACOSX = SYSTEM == 'Darwin'
LINUX = SYSTEM == 'Linux'
DEVPI_PYPI_URL = 'http://localhost:4040/root/pypi/+simple/'
PATH_VARS = ['PATH', 'MANPATH', 'INFOPATH']
PROCESS_PROGRAMS = ['ps', 'pgrep', 'pkill', 'htop', 'lsof', 'pstree']
SHELLS = ['bash', 'zsh']
# I couldn't come up with a good name for this variable, but you'll get the
# point.
SHELL_FILE_NAMES = {
    'rc.bash': '.bashrc',
    'rc.zsh': '.zshrc',
    'profile.bash': '.bash_profile',
    'profile.zsh': '.zprofile',
    'logout.bash': '.bash_logout',
    'logout.zsh': '.zlogout',
}
LOCAL_DIR = join('shell', 'local')

# Options
def options(ctx):
    # Override the default prefix of '/usr/local'.
    default_prefix = os.path.expanduser('~')
    ctx.add_option(
        '--prefix', default=default_prefix,
        help='installation prefix [default: {}]'.format(repr(default_prefix)))

# Configuration
## Paths

@conf
def add_to_path_var(ctx, var, path):
    if os.path.isdir(path):
        ctx.msg('Adding to ' + var, path)
        # append_unique is O(n) which sucks, but there aren't that many paths
        # and it's only run at configuration, so it doesn't really need to be
        # too performant. For a performant way (that we used before
        # simplifying), check out orderedset on PyPi.
        ctx.env.append_unique(var, path)


@conf
def execute_in_clean_bash(ctx, command):
    # Only source /etc/profile in a clean environment. That should get us the
    # base paths (hopefully).
    profile_file = '/etc/profile'
    return ctx.cmd_and_log([
        'env', '-i', 'bash', '--norc', '--noprofile', '-c',
        ("if [[ -s '{profile_file}' ]]; then source '{profile_file}'; fi; "
        '{command}').format(profile_file=profile_file, command=command)])\
              .rstrip('\n')


@conf
def add_path_hierarchy(ctx, path):
    ctx.add_to_path_var('PATH', join(path, 'bin'))
    ctx.add_to_path_var('PATH', join(path, 'sbin'))
    ctx.add_to_path_var('MANPATH', join(path, 'man'))
    ctx.add_to_path_var('MANPATH', join(path, 'share', 'man'))
    ctx.add_to_path_var(
        'INFOPATH', join(path, 'share', 'info'))


@conf
def add_system_default_paths(ctx):
    # To get the system defaults, we execute Bash in a clean environment,
    # sourcing only the system's shell profile.
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


@conf
def write_paths_to_env(ctx):
    for var in PATH_VARS:
        os.environ[var] = os.pathsep.join(ctx.env[var])


@conf
def setup_default_paths(ctx):
    # Set up paths to check for "system" tools, like Python. The '.local' path
    # allows us to override the "system" tools as a user.
    system_hierarchies = [
        join(ctx.env.PREFIX, '.local'),
        '/usr/local',
        '/usr',
    ]

    ctx.env.SYSTEM_PATHS = [join(hier, 'bin') for hier in system_hierarchies]

    # Initialize paths. Higher-priority paths come first.
    for var in PATH_VARS:
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
            ctx.env.SYSTEM_PYTHON, '-m', 'site', '--user-base']).\
            decode('ascii').rstrip())
        ctx.add_path_hierarchy(user_base)

    # Emacs.app on Mac OS X contains some paths in some weird places.
    if MACOSX:
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

    # I don't think this is valid anymore.
    # See this post for some more info (haha):
    # <http://unix.stackexchange.com/questions/22329/gnu-texinfo-directory-search-method>

    # Add hierarchies.
    # Even though /usr/bin is probably already in the PATH, it is helpful to
    # add /usr so that INFOPATH gets correctly populated.
    for hier in system_hierarchies:
        ctx.add_path_hierarchy(hier)

    # Finally, add system-default paths.
    ctx.add_system_default_paths()

    # Write the paths to this current process' environment so that the
    # configuration uses these paths to find utilities (mostly important for
    # PATH, of course).
    ctx.write_paths_to_env()


## Shells

@conf
def check_bash(ctx):
    # Make this variable hidden so that it is not defined unless the version is
    # also correct.
    exe_path = ctx.find_program('bash', var='_BASH')

    required_major_version = '4'
    major_version = ctx.cmd_and_log([
        exe_path, '-c', 'echo -n ${BASH_VERSINFO[0]}'])
    full_version = ctx.cmd_and_log([
        exe_path, '-c', 'echo -n $BASH_VERSION'])
    version_ok = major_version == required_major_version

    ctx.msg('Checking for Bash version', full_version,
            color='GREEN' if version_ok else 'YELLOW')

    if version_ok:
        ctx.env.BASH = exe_path
    else:
        ctx.fatal('This configuration requires Bash {0}.'.format(
            required_major_version))


@conf
def check_zsh(ctx):
    # oh my zsh uses the 'ZSH' environment variable, and not for the path to
    # the shell.

    # Make this variable hidden so that it is not defined unless the version is
    # also correct.
    exe_path = ctx.find_program('zsh', var='_ZSHELL')

    required_major_version = '5'
    full_version = ctx.cmd_and_log([
        exe_path, '-c', 'echo -n $ZSH_VERSION'])
    version_split = full_version.split('.')
    if len(version_split) != 3:
        ctx.fatal('Unrecognized Zsh version.')
    major_version = version_split[0]
    version_ok = major_version == required_major_version

    ctx.msg('Checking for Zsh version', full_version,
            color='GREEN' if version_ok else 'YELLOW')
    if version_ok:
        ctx.env.ZSHELL = exe_path
    else:
        ctx.fatal('This configuration requires Zsh {0}.'.format(
            required_major_version))


@conf
def check_path_for_issues(ctx):
    # Check to see if os.pathsep is in any of the paths; that will make them
    # unusable.
    for path in ctx.env.PATH:
        if os.pathsep in path:
            ctx.fatal('Path cannot contain os.pathsep: ' + path)


@conf
def find_clipboard_programs(ctx):
    if MACOSX:
        for action in ['copy', 'paste']:
            path = ctx.find_program('pb' + action)
            ctx.env[action.upper() + '_COMMAND'] = path
    elif LINUX:
        xclip_path = ctx.find_program('xclip', mandatory=False)
        if xclip_path:
            base_cmd_list = [xclip_path, '-sel', 'c']
            ctx.env.COPY_COMMAND = ' '.join(base_cmd_list + ['-in'])
            ctx.env.PASTE_COMMAND = ' '.join(base_cmd_list + ['-out'])


@conf
def find_gnu_util(ctx, exe_name):
    """Search for a GNU utility, prefixed with 'g' on Mac OS X."""
    return ctx.find_program(
        ('g' if MACOSX else '') + exe_name, var=exe_name.upper())


@conf
def find_powerline(ctx):
    # We assume that Powerline is installed under the system Python. We
    # don't allow Waf to look in pyenv paths, so that's a decent
    # assumption.
    if not ctx.env.SYSTEM_PYTHON:
        ctx.fatal('Powerline must be installed under the system Python.')

    ctx.find_program('powerline-daemon', var='POWERLINE_DAEMON',
                     mandatory=False)
    # Powerline actually uses the $POWERLINE_CONFIG environment variable, which
    # Waf will then detect. Change ours to avoid this.
    ctx.find_program('powerline-config', var='_POWERLINE_CONFIG',
                     mandatory=False)

    # Set this variable to give us an easy way to tell if we have Powerline.
    ctx.env.POWERLINE = (
        bool(ctx.env.POWERLINE_DAEMON) and bool(ctx.env._POWERLINE_CONFIG))


def configure(ctx):
    # Paths (further sections can modify paths too)
    ctx.setup_default_paths()

    # Shells
    ctx.check_bash(mandatory=False)
    ctx.check_zsh(mandatory=False)

    # Editor
    ctx.find_program('emacsclient', mandatory=False)
    ctx.find_program('e-sink', var='E_SINK', mandatory=False)

    # Version control
    ctx.find_program('git', mandatory=False)
    ctx.find_program('hg', mandatory=False)
    ctx.find_program('hub', mandatory=False)

    # Programming language version management
    ctx.find_program('pyenv', mandatory=False)
    ctx.find_program('rbenv', mandatory=False)

    # Download utilities
    ctx.find_program('aria2c', mandatory=False)
    ctx.find_program('wget')  # Wget is mandatory!!!

    # Powerline
    ctx.find_powerline(mandatory=False)

    # Other utilities
    ctx.find_clipboard_programs()
    ctx.find_program('fasd', mandatory=False)
    ctx.find_program('ssh', mandatory=False)
    ctx.find_program('devpi-ctl', var='DEVPI_CTL', mandatory=False)
    ctx.find_program('qpdf', mandatory=False)
    for prog in PROCESS_PROGRAMS:
        ctx.find_program(prog, mandatory=False)
    ctx.find_program('tmux', mandatory=False)
    ctx.find_program('ack', mandatory=False)
    ctx.find_program('ag', mandatory=False)
    ctx.find_program('ohcount', mandatory=False)
    ctx.find_program('mktemp', mandatory=False)
    ctx.find_gnu_util('wc', mandatory=False)
    ctx.find_gnu_util('numfmt', mandatory=False)
    # We'd like to check for this, but it's an rbenv-managed gem.
    #ctx.find_program('lolcat', mandatory=False)

    if LINUX:
        ctx.find_program('gnome-open', var='GNOME_OPEN', mandatory=False)

    # After configuration, do some maintenance on the paths.
    ctx.check_path_for_issues()


# Build

def concatenate(tsk):
    output_node = tsk.outputs[0]
    with open(output_node.abspath(), 'w') as output_file:
        final_filename = SHELL_FILE_NAMES[output_node.name]
        six.print_('# {}'.format(final_filename), file=output_file)
        for input_node in tsk.inputs:
            six.print_(file=output_file)
            with open(input_node.abspath()) as input_file:
                for line in input_file:
                    output_file.write(line)


def make_rbenv_pyenv_file(tsk):
    # The generated code loads pyenv and rbenv into the shell session. We need
    # to load this in the rc file because it loads up shell functions. For
    # example, `pyenv shell' is only available when this `eval' command is run
    # *within the shell*.
    output_node = tsk.outputs[0]
    # The tool is determined by the basename without the extension.
    # The shell is determined by the output file's extension. suffix() returns
    # the extension with a preceding dot, so strip it off.
    tool, ext = os.path.splitext(output_node.name)
    shell = ext[1:]
    path = tsk.env[tool.upper()]
    with open(output_node.abspath(), 'w') as output_file:
        # Instead of running pyenv and rbenv to generate code and eval'ing it
        # every time, just generate it now and source it. Because we aren't
        # running it from within a shell, we need to tell rbenv and pyenv what
        # shell for which to generate the code. Otherwise, they determine it
        # through ps or $SHELL, $SHELL is just plain wrong, because that is the
        # login shell, which is not necessarily the shell that is running.
        ret = tsk.exec_command(
            [path, 'init', '-', shell], stdout=output_file)

    return ret


def make_fasd_cache(tsk):
    out_node = tsk.outputs[0]
    shell = out_node.suffix()[1:]
    init_args = ['posix-alias', '{}-hook'.format(shell)] + [
        '{0}-{1}'.format(arg, shell)
        for arg in ['ccomp', 'ccomp-install']]
    if shell == 'zsh':
        init_args += ['{0}-{1}'.format(arg, shell)
                      for arg in ['wcomp', 'wcomp-install']]
    with open(out_node.abspath(), 'w') as output_file:
        ret = tsk.exec_command(
            [tsk.env.FASD, '--init'] + init_args,
            stdout=output_file)
    return ret


def get_powerline_path(ctx, relpath):
    # Just assume ascii; should be fine. This needs to be a str for Waf.
    return str(subprocess.check_output([
        ctx.env.SYSTEM_PYTHON, '-c',
        'from pkg_resources import resource_filename; '
        "print(resource_filename('powerline', {0}))".\
        format(repr(relpath))]).decode('ascii').rstrip())


def build(ctx):
    ctx.write_paths_to_env()

    # List of dotfile nodes from the dotfiles/ directory to install.
    dotfile_nodes = []
    # A mapping of environment variable name to value. The values are raw,
    # i.e., they will not be shell-quoted. If that is desired, it needs to be
    # done before insertion to the data structure.
    shenv = OrderedDict()
    # A mapping of alias name to command. The command is a [Python] string
    # which will be shell-quoted when written out. Don't forget to
    # pre-shell-quote any paths from the configure step.
    aliases = OrderedDict()
    # A mapping of shell to shell file nodes to include in the compiled rc
    # files.
    rc_nodes = dict(
        bash=[],
        zsh=[],
    )
    # A mapping of shell to shell file nodes to include in the compiled profile files.
    profile_nodes = dict(
        bash=[],
        zsh=[],
    )
    # A list of scripts in the script/ directory to install to $PREFIX/bin.
    scripts = []
    # Shell key bindings
    #
    # There is apparently no way portable between Bash and Zsh to declare
    # subscripts to an associative array which have backslashes. In the past,
    # we used an intermediate `key' variable workaround to get consistent
    # quoting. However, now that we have the superb data structures of Python,
    # and the ablility to change what goes in to them via configuration
    # options, we opted for the Python data structure.
    keybindings = {
        # Paging
        # Note: `|&' is Bash 4 and Zsh only.
        r'\C-j': r' |& less\C-m',
        # Executing last command.
        # This is equivalent to pressing C-p or the up arrow, then Enter.
        r'\C-xp': r'\C-p\C-m',
        # Up a directory, aliased to `u' for me. Note: `\ej' means `ESC+' then
        # `j' as opposed to `\M-j', which means `Meta' then `j'. I have both
        # Option keys on my Mac configured to send `ESC+' in iTerm2. Actually
        # sending Meta is apparently a relic of the past, and ESC+ should be
        # used now.
        r'\ej': r'u\C-m',
        # Lolcat keybindings. This would be nice to make part of the
        # configuration, but lolcat is an rbenv-managed gem, and that makes it
        # hard to do.
        r'\C-xl': r' |& lolcat\C-m',
        r'\C-x\C-l': r' |& lolcat --force |& less -R\C-m',
        r'\C-xa': r' |& lolcat --animate\C-m',
    }

    # Include default profile nodes.
    for shell in SHELLS:
        profile_nodes[shell].append(ctx.path.find_resource([
            'shell', 'profile.sh']))

    # Prepare path variables.
    for var in PATH_VARS:
        # The backslashes make it a little more readable in the file
        # (at the cost of being readable here).
        shenv[var] = '\\\n{}\n'.format((os.pathsep + '\\\n').join(
            shquote(path) for path in ctx.env[var]))

    # This file comes first in the rc list. We don't want Bash or Zsh scripts to
    # load our entire configuration just to run. That would make them very
    # slow.
    exit_if_nonint_node = ctx.path.find_resource(
        ['shell', 'exit-if-noninteractive.sh'])
    for shell in SHELLS:
        rc_nodes[shell].append(exit_if_nonint_node)

    # Include default rc nodes.
    for shell in SHELLS:
        name = 'rc.{}'.format(shell)
        rc_nodes[shell].append(ctx.path.find_resource(['shell', name]))

    # Build files that load rbenv and pyenv
    for shell in SHELLS:
        for prefix in ['rb', 'py']:
            tool = prefix + 'env'
            path = ctx.env[tool.upper()]
            if path:
                out_node = ctx.path.find_or_declare(
                    '{0}.{1}'.format(tool, shell))
                rc_nodes[shell].append(out_node)
                ctx(rule=make_rbenv_pyenv_file,
                    target=out_node,
                    always=True)

    # Platform-specific configuration
    if MACOSX:
        # Human readable file sizes, classify, and color
        aliases['ls'] = 'ls -hFG'
        # Homebrew deletes (Tex)Info manuals unless you bar it from doing
        # so. Heck yes I want these, I use Emacs!
        shenv['HOMEBREW_KEEP_INFO'] = 'true'

        # ssh-agent handling code is not needed in Mac OS X because it is
        # handled by the operating system.

        # Open Xcode project.
        aliases['openx'] = 'env -i open *.xcodeproj'
    elif LINUX:
        # Colorize, human readable file sizes, classify
        aliases['ls'] = 'ls --color=always -hF'
        if ctx.env.GNOME_OPEN:
            aliases['open'] = shquote(ctx.env.GNOME_OPEN)
        for shell in SHELLS:
            rc_nodes[shell].append(
            ctx.path.find_resource(['shell', 'gnu-linux.bash']))

        # Swap Caps Lock and Control under X11
        dotfile_nodes.append(ctx.path.find_resource(['dotfiles', 'Xkbmap']))

    # Editor
    if ctx.env.EMACSCLIENT:
        editor = 'emacsclient --alternate-editor='
        if ctx.env.E_SINK:
            scripts.append('e')
        else:
            aliases['e'] = 'emacsclient --no-wait'
    else:
        editor = 'nano'
    shenv['EDITOR'] = shquote(editor)

    # Clipboard interaction
    if ctx.env.COPY_COMMAND and ctx.env.PASTE_COMMAND:
        aliases['copy'] = shquote(ctx.env.COPY_COMMAND)
        aliases['paste'] = shquote(ctx.env.PASTE_COMMAND)

        # aria2 might be available, wget is always available
        downloader = shquote(ctx.env.ARIA2C or ctx.env.WGET)
        # Download from clipboard
        aliases['dl'] = downloader + ' "$(paste)"'
        # Download to clipboard
        aliases['dltc'] = (
            shquote(ctx.env.WGET) + ' --no-verbose --output-document=- "$(paste)" '
            '| copy')

    # Various utilities
    zsh_theme = ''
    if ctx.env.POWERLINE:
        bash_powerline_node = ctx.path.find_or_declare('powerline.bash')
        rc_nodes['bash'].append(bash_powerline_node)
        @ctx.rule(target=bash_powerline_node, always=True)
        def make_bash_powerline(tsk):
            bash_powerline_file = get_powerline_path(
                ctx, join('bindings', 'bash', 'powerline.sh'))
            contents = '''{powerline_daemon} --quiet
POWERLINE_BASH_CONTINUATION=1
POWERLINE_BASH_SELECT=1
source {bash_powerline_file}
'''.format(
    powerline_daemon=shquote(tsk.env.POWERLINE_DAEMON),
    bash_powerline_file=shquote(bash_powerline_file),
)
            with open(tsk.outputs[0].abspath(), 'w') as output_file:
                output_file.write(contents)

        zsh_powerline_node = ctx.path.find_or_declare('powerline.zsh')
        rc_nodes['zsh'].append(zsh_powerline_node)
        @ctx.rule(target=zsh_powerline_node, always=True)
        def make_zsh_powerline(tsk):
            zsh_powerline_file = get_powerline_path(
                ctx, join('bindings', 'zsh', 'powerline.zsh'))
            contents = '''{powerline_daemon} --quiet
source {zsh_powerline_file}
'''.format(
    powerline_daemon=shquote(tsk.env.POWERLINE_DAEMON),
    zsh_powerline_file=shquote(zsh_powerline_file),
)
            with open(tsk.outputs[0].abspath(), 'w') as output_file:
                output_file.write(contents)

        # Install Powerline configuration files
        for dirpath, dirnames, filenames in os.walk(join(
                'dotfiles', 'config', 'powerline')):
            for filename in filenames:
                dotfile_nodes.append(ctx.path.find_resource(
                    join(dirpath, filename)))
    else:
        # No powerline, enable basic prompt.
        zsh_theme = 'bira-simple'
        for shell in SHELLS:
            rc_nodes[shell].append(ctx.path.find_resource([
                'shell', 'prompt.{}'.format(shell)]))

    if ctx.env.FASD:
        # See here for all the options: https://github.com/clvv/fasd#install
        for shell in SHELLS:
            out_node = ctx.path.find_or_declare('fasd.{}'.format(shell))
            rc_nodes[shell].append(out_node)
            ctx(rule=make_fasd_cache, target=out_node, always=True)

    if ctx.env.QPDF:
        scripts.append('pdf-merge')
        aliases['pdf-join'] = 'pdf-merge'

    if ctx.env.DEVPI_CTL:
        for relative_path in [join('pip', 'pip.conf'), 'pydistutils.cfg']:
            in_node = ctx.path.find_resource([
                'dotfiles', relative_path + '.in'])
            out_node = ctx.path.find_or_declare(relative_path)
            ctx(features='subst',
                source=in_node,
                target=out_node,
                DEVPI_PYPI_URL=DEVPI_PYPI_URL)

            # Make the path relative to the dotfiles/ directory so that it
            # matches the other elements.
            dotfile_nodes.append(out_node)

    if ctx.env.SSH:
        dotfile_nodes.append(ctx.path.find_resource(
            ['dotfiles', 'ssh', 'config']))

    if ctx.env.TMUX:
        for shell in SHELLS:
            rc_nodes[shell].append(ctx.path.find_resource([
                'shell', 'tmux.sh']))

        default_shell = 'zsh'
        # Workaround for Mac OS X pasteboard, see
        # https://github.com/ChrisJohnsen/tmux-MacOSX-pasteboard
        # Don't pass -l; we don't want a login shell.
        default_command = shquote(
            'reattach-to-user-namespace {}'.format(default_shell) if MACOSX
            else default_shell)
        in_node = ctx.path.find_resource(['dotfiles', 'tmux.conf.in'])
        out_node = ctx.path.find_or_declare('tmux.conf')

        powerline_commands = ''
        if ctx.env.POWERLINE:
            # Powerline should be able to find this on the PATH. But just in
            # case it's not, and maybe to save a little bit on execution, tell
            # Powerline where it is with this environment variable.
            shenv['POWERLINE_CONFIG_COMMAND'] = ctx.env._POWERLINE_CONFIG
            tmux_powerline_file = get_powerline_path(
                ctx, join('bindings', 'tmux', 'powerline.conf'))
            powerline_commands = '''run-shell "{powerline_daemon} --quiet"
source "{tmux_powerline_file}"
'''.format(
    powerline_daemon=shquote(ctx.env.POWERLINE_DAEMON),
    tmux_powerline_file=tmux_powerline_file,
)

        ctx(features='subst',
            source=in_node,
            target=out_node,
            DEFAULT_COMMAND=default_command,
            POWERLINE_COMMANDS=powerline_commands)
        dotfile_nodes.append(out_node)

        if ctx.env.LSOF:
            # List my tmux sockets
            aliases['mytmux'] = (
                shquote(ctx.env.LSOF) +
                ' -u "$(id -un)" -a -U | grep \'^tmux\'')

    if ctx.env.GIT:
        quoted_git = shquote(ctx.env.GIT)
        aliases['gt'] = quoted_git + ' status'
        aliases['gobuddygo'] = quoted_git + ' push'
        aliases['cometome'] = quoted_git + ' pull'

        dotfile_nodes += [ctx.path.find_resource(['dotfiles', name])
                          for name in ['gitconfig', 'gitignore_global']]

        if ctx.env.WC and ctx.env.NUMFMT:
            # Find size of the working tree in a git repo.
            # See here for sources of approaches:
            # http://serverfault.com/questions/351598/get-total-files-size-from-a-file-containing-a-file-list
            aliases['git-working-tree-size'] = (
                'git ls-files -z | {wc} --bytes --files0-from=- | '
                '{numfmt} --to=iec-i --suffix=B').format(
                    wc=shquote(ctx.env.WC),
                    numfmt=shquote(ctx.env.NUMFMT))
            # Another approach, using GNU stat and awk:
            #
            # git ls-files -z | while read -d $'\0' filename;
            # do $STAT -c '%s' "$filename"; done |
            # awk '{total+=$1} END {print total}

        if ctx.env.HUB:
            # Hub's alias command `hub alias -s' produces really simple output,
            # which is basically this.
            aliases['git'] = 'hub'

    if ctx.env.HG:
        dotfile_nodes.append(ctx.path.find_resource(['dotfiles', 'hgrc']))

    if ctx.env.ACK:
        # Just 'less' is fine; we don't need to pass 'less -R' to get colors to
        # work.
        aliases['ackp'] = shquote(ctx.env.ACK) + ' --pager=less'
        if ctx.env.GIT:
            # Note: by default `git ls-files' only shows tracked files.
            aliases['ackg'] = 'git ls-files | {} --files-from=-'.format(
                shquote(ctx.env.ACK))
            aliases['ackpg'] = 'git ls-files | ackp --files-from=-'
        dotfile_nodes.append(ctx.path.find_resource(['dotfiles', 'ackrc']))

    if ctx.env.AG:
        # Just 'less' is fine; we don't need to pass 'less -R' to get colors to
        # work.
        aliases['agp'] = shquote(ctx.env.AG) + ' --pager less'
        # ag doesn't support `--files-from'. Too bad.

    if ctx.env.OHCOUNT and ctx.env.GIT:
        scripts.append('git-count-lines')

    # Process programs
    #
    # All these programs support a -u argument specifying the user. For ps,
    # pgrep, and pkill it is effective user id (euid). For htop and lsof this
    # is unspecified. In most of my cases, euid and ruid will be the same
    # anyway.
    #
    # There are two different versions of pstree:
    # - http://freecode.com/projects/pstree, used on my Mac OS X
    # - http://psmisc.sourceforge.net/, used on most GNU/Linux machines
    # But they both support the -u flag!
    #
    # Note: `id -un' was used since `whoami' has been obsoleted and is not
    # POSIX.
    for prog in PROCESS_PROGRAMS:
        prog_path = ctx.env[prog.upper()]
        aliases['my' + prog] = shquote(prog_path) + ' -u "$(id -un)"'

    # Build shell environment. Do it after all the tools are configured so that
    # each tool has an opportunity to modify the environment.
    shenv_node = ctx.path.find_or_declare('env.sh')
    for shell in SHELLS:
        profile_nodes[shell].append(shenv_node)
    # Always build this file, since it depends values in the build script.
    @ctx.rule(target=shenv_node, always=True)
    def mkshenv(tsk):
        with open(tsk.outputs[0].abspath(), 'w') as out_file:
            six.print_('# Shell environment\n', file=out_file)
            for name, value in six.iteritems(shenv):
                six.print_('export {0}={1}'.format(name, value), file=out_file)

    # Source in .bashrc in the .bash_profile. Needs to happen after the shell
    # environment.
    profile_nodes['bash'].append(ctx.path.find_resource([
        'shell', 'sourcebashrc.bash']))

    # Build aliases. Do it after all the tools are configured so that each tool
    # has an opportunity to add aliases.
    aliases_in_node = ctx.path.find_resource(['shell', 'aliases.sh'])
    aliases_out_node = ctx.path.find_or_declare('aliases.sh')
    for shell in SHELLS:
        rc_nodes[shell].append(aliases_out_node)
    # Always build this file, since it depends on the build script.
    @ctx.rule(target=aliases_out_node, source=aliases_in_node, always=True)
    def mkaliases(tsk):
        with open(tsk.outputs[0].abspath(), 'w') as out_file:
            with open(tsk.inputs[0].abspath()) as in_file:
                for line in in_file:
                    out_file.write(line)
            six.print_('\n# Tool aliases\n', file=out_file)
            for alias, command in six.iteritems(aliases):
                six.print_(
                    'alias {0}={1}'.format(alias, shquote(command)),
                    file=out_file)

    # Build keybindings. Do it after all the tools are configured so that
    # each tool has an opportunity to add keybindings.
    def make_bash_keys(tsk):
        with open(tsk.outputs[0].abspath(), 'w') as out_file:
            for key, binding in six.iteritems(keybindings):
                # It is supposed to turn out like this:
                # bind '"\C-j": " 2>&1 | less\C-m"'
                six.print_(
                    'bind ' + shquote('"{0}": "{1}"'.format(key, binding)),
                    file=out_file)

    def make_zsh_keys(tsk):
        with open(tsk.outputs[0].abspath(), 'w') as out_file:
            for key, binding in six.iteritems(keybindings):
                six.print_(
                    'bindkey -s {0} {1}'.format(
                        shquote(key), shquote(binding)),
                    file=out_file)

    for shell in SHELLS:
        out_node = ctx.path.find_or_declare('keys.{}'.format(shell))
        rc_nodes[shell].append(out_node)
        # Always build this file, since it depends on the build script.
        rule = locals()['make_{}_keys'.format(shell)]
        ctx(rule=rule, target=out_node, always=True)

    # Local profile and rc configurations.
    local_profile_path = join(LOCAL_DIR, 'profile.sh')
    if os.path.isfile(local_profile_path):
        for shell in SHELLS:
            profile_nodes[shell].append(ctx.path.find_resource(
                local_profile_path))

    local_rc_path = join(LOCAL_DIR, 'rc.sh')
    if os.path.isfile(local_rc_path):
        for shell in SHELLS:
            rc_nodes[shell].append(ctx.path.find_resource(local_rc_path))

    # Finally, build shell files

    shell_nodes = []
    for shell in SHELLS:
        for filetype in ['rc', 'profile']:
            name = '{0}.{1}'.format(filetype, shell)
            filetype_node_list = locals()[filetype + '_nodes']
            in_nodes = filetype_node_list[shell]
            out_node = ctx.path.find_or_declare(name)
            shell_nodes.append(out_node)
            ctx(rule=concatenate,
                target=out_node,
                source=in_nodes,
                always=True)

    # Install files
    #
    # Note: These functions only have an effect when Waf is called with
    # 'install' or 'uninstall'.

    # Install shell files
    for node in shell_nodes:
        ctx.install_as(join(ctx.env.PREFIX, SHELL_FILE_NAMES[node.name]), node)

    logout_zsh_name = 'logout.zsh'
    ctx.install_as(
        join(ctx.env.PREFIX, SHELL_FILE_NAMES[logout_zsh_name]),
        join('shell', logout_zsh_name))

    # Install other dotfiles
    dotfiles_dir_node = ctx.path.find_dir('dotfiles')
    for node in dotfile_nodes:
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
        [join('scripts', basename) for basename in scripts],
        chmod=waflib.Utils.O755)
