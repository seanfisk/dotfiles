# -*- coding: utf-8 -*-
"""Detect and configure shells. Beware; this one's the most complicated :)"""

import os
from os.path import join
from shlex import quote as shquote
from collections import OrderedDict

from waflib.Configure import conf

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

def configure(ctx):
    ctx.env.CONFIGURABLE_SHELLS = ['bash', 'zsh']
    avail_shells = []
    # Bash is mandatory!
    if ctx.find_bash():
        avail_shells.append('bash')
    if ctx.find_zsh(mandatory=False):
        avail_shells.append('zsh')
    ctx.env.AVAILABLE_SHELLS = avail_shells

@conf
def find_bash(self):
    """Find the Bash shell."""
    # Make this variable hidden so that it is not defined unless the version is
    # also correct.
    exe_path = self.find_program('bash', var='_BASH')

    required_major_version = '4'
    major_version = self.cmd_and_log(
        exe_path + ['-c', 'echo -n ${BASH_VERSINFO[0]}'])
    full_version = self.cmd_and_log(
        exe_path + ['-c', 'echo -n $BASH_VERSION'])
    version_ok = major_version == required_major_version

    self.msg('Checking for Bash version', full_version,
             color='GREEN' if version_ok else 'YELLOW')

    if version_ok:
        self.env.BASH = exe_path
    else:
        self.fatal('This configuration requires Bash {}.'.format(
            required_major_version))

    return exe_path

@conf
def find_zsh(self):
    """Find Z shell."""
    # Note: oh my zsh uses the 'ZSH' environment variable, and not for the path
    # to the shell. Don't let 'ZSH' get used in the find_program() call.
    #
    # Make this variable hidden so that it is not defined unless the version is
    # also correct.
    exe_path = self.find_program('zsh', var='_ZSH')

    required_major_version = '5'
    full_version = self.cmd_and_log(
        exe_path + ['-c', 'echo -n $ZSH_VERSION'])
    version_split = full_version.split('.')
    if len(version_split) != 3:
        self.fatal('Unrecognized Zsh version.')
    major_version = version_split[0]
    version_ok = major_version == required_major_version

    self.msg('Checking for Zsh version', full_version,
             color='GREEN' if version_ok else 'YELLOW')
    if version_ok:
        self.env.ZSH = exe_path
    else:
        self.fatal('This configuration requires Zsh {}.'.format(
            required_major_version))

    return exe_path

@conf
def add_shell_rc_node(self, node, shell=None):
    """Add the contents of node to the shell's generated rc file."""
    self.add_shell_node(node, 'rc', shell)

@conf
def add_shell_profile_node(self, node, shell=None):
    """Add the contents of node to the shell's generated profile file."""
    self.add_shell_node(node, 'profile', shell)

@conf
def add_shell_node(self, node, filetype, shell=None):
    """Add the contents of node to a shell's generated file."""
    for shell in [shell] if shell else self.env.AVAILABLE_SHELLS:
        self.env['{}_{}_NODES'.format(shell.upper(), filetype.upper())].append(
            node)

@conf
def setup_shell_defaults(self):
    """Set up shell defaults. Call this function before opening up the shell
    setups to other tools.
    """
    # Set variables to be used in the build process.

    # A mapping of environment variable name to value. The values are raw,
    # i.e., they will not be shell-quoted. If that is desired, it needs to be
    # done before insertion to the data structure. The order here is important,
    # as variables may use earlier variables in their values.
    self.env.SHELL_ENV = OrderedDict()
    # A mapping of alias name to command. The command is a [Python] string
    # which will be shell-quoted when written out. Don't forget to
    # pre-shell-quote any paths from the configure step. This is ordered just
    # to keep related aliases together in the generated file -- the order
    # should not really matter, though.
    self.env.SHELL_ALIASES = OrderedDict()
    # Use the list of configurable shells so that other tasks can add to
    # specific shells without getting errors.
    for shell in self.env.CONFIGURABLE_SHELLS:
        shell_up = shell.upper()
        # A mapping of shell to shell file nodes to include in the compiled rc
        # files.
        self.env[shell_up + '_RC_NODES'] = []
        # A mapping of shell to shell file nodes to include in the compiled
        # profile files.
        self.env[shell_up + '_PROFILE_NODES'] = []

    # Add some aliases for shells without all the customizations.
    self.env.SHELL_ALIASES['bash-basic'] = self.shquote_cmd(
        self.env.BASH + ['--noprofile', '--norc'])
    if self.env.ZSH:
        self.env.SHELL_ALIASES['zsh-basic'] = self.shquote_cmd(
            self.env.ZSH + ['--no-rcs'])

    # Key bindings
    #
    # There is apparently no way portable between Bash and Zsh to declare
    # subscripts to an associative array which have backslashes. In the past,
    # we used an intermediate `key' variable workaround to get consistent
    # quoting. However, now that we have the superb data structures of Python,
    # and the ability to change what goes in to them via configuration options,
    # we opted for the Python data structure.
    #
    # We use an OrderedDict to guarantee a stable order for the build.
    self.env.SHELL_KEYBINDINGS = OrderedDict([
        # Paging
        # Note: `|&' is Bash 4 and Zsh only.
        (r'\C-j', r' |& less\C-m'),
        # Executing last command.
        # This is equivalent to pressing C-p or the up arrow, then Enter.
        (r'\C-xp', r'\C-p\C-m'),
        # Up a directory, aliased to `u' for me. Note: `\ej' means `ESC+' then
        # `j' as opposed to `\M-j', which means `Meta' then `j'. I have both
        # Option keys on my Mac configured to send `ESC+' in iTerm2. Actually
        # sending Meta is apparently a relic of the past, and ESC+ should be
        # used now.
        (r'\ej', r'u\C-m'),
        # Lolcat keybindings. This would be nice to make part of the
        # configuration, but lolcat is an rbenv-managed gem, and that makes it
        # hard to do.
        (r'\C-xl', r' |& lolcat\C-m'),
        (r'\C-x\C-l', r' |& lolcat --force |& less -R\C-m'),
        (r'\C-xa', r' |& lolcat --animate\C-m'),
    ])

    # Include base profile nodes.
    self.add_shell_profile_node(self.path.find_resource([
        'shell', 'profile-base.sh']))

    # Prepare path variables.
    for var in self.env.PATH_VARS:
        # The backslashes make it a little more readable in the file
        # (at the cost of being readable here).
        self.env.SHELL_ENV[var] = '\\\n{}\n'.format((os.pathsep + '\\\n').join(
            map(shquote, self.env[var])))

    # This file comes first in the rc list. We don't want Bash or Zsh scripts
    # to load our entire configuration just to run. That would make them very
    # slow.
    exit_if_nonint_node = self.path.find_resource(
        ['shell', 'exit-if-noninteractive.sh'])
    self.add_shell_rc_node(exit_if_nonint_node)

    # Include zpython for zsh, if available.
    if self.env.ZPYTHON_MODULE_PATH:
        in_node = self.path.find_resource(['shell', 'zpython.zsh.in'])
        out_node = self.path.find_or_declare('zpython.zsh')
        self.env.ZSH_RC_NODES.append(out_node)
        self(features='subst',
             target=out_node,
             source=in_node,
             ZPYTHON_MODULE_PATH=shquote(self.env.ZPYTHON_MODULE_PATH))

    if not self.env.POWERLINE:
        # No powerline; enable basic prompt.

        # Include the prompt file for Bash.
        self.env.BASH_RC_NODES.append(self.path.find_resource([
            'shell', 'prompt.bash']))

        # Turn on our Oh My Zsh theme for Zsh.
        zsh_theme = 'bira-simple'
    else:
        # No Oh My Zsh theme needed if we are using Powerline.
        zsh_theme = ''

    # Include default rc nodes.
    self.env.BASH_RC_NODES.append(
        self.path.find_resource(['shell', 'rc-base.bash']))

    if self.env.ZSH:
        in_node = self.path.find_resource(['shell', 'rc-base.zsh.in'])
        out_node = self.path.find_or_declare('rc-base.zsh')
        self.env.ZSH_RC_NODES.append(out_node)
        self(features='subst',
             target=out_node,
             source=in_node,
             ZSH_THEME=shquote(zsh_theme))

@conf
def build_shell_env(self):
    """Build the shell environment. Do it after all the tools are configured so
    that each tool has an opportunity to modify the environment.
    """
    out_node = self.path.find_or_declare('env.sh')

    for shell in self.env.AVAILABLE_SHELLS:
        # Insert this before all the other nodes so that they may modify the
        # shell environment. Useful for rbenv/pyenv.
        self.env['{}_PROFILE_NODES'.format(shell.upper())].insert(0, out_node)

    @self.rule(target=out_node, vars=['SHELL_ENV'])
    def _make_shell_env(tsk):
        with open(tsk.outputs[0].abspath(), 'w') as out_file:
            print('# Shell environment\n', file=out_file)
            for name, value in self.env.SHELL_ENV.items():
                print('export {}={}'.format(name, value), file=out_file)

@conf
def build_shell_aliases(self):
    """Build shell aliases. Do it after all the tools are configured so that
    each tool has an opportunity to add aliases.
    """
    in_node = self.path.find_resource(['shell', 'aliases.sh'])
    out_node = self.path.find_or_declare('aliases.sh')
    self.add_shell_rc_node(out_node)

    @self.rule(target=out_node, source=in_node, vars=['SHELL_ALIASES'])
    def _make_aliases(tsk):
        with open(tsk.outputs[0].abspath(), 'w') as out_file:
            with open(tsk.inputs[0].abspath()) as in_file:
                for line in in_file:
                    out_file.write(line)
            print('\n# Tool aliases\n', file=out_file)
            for alias, command in tsk.env.SHELL_ALIASES.items():
                print(
                    'alias {}={}'.format(alias, shquote(command)),
                    file=out_file)

@conf
def build_shell_keybindings(self):
    """Build keybindings. Do it after all the tools are configured so that each
    tool has an opportunity to add keybindings.
    """
    def _make_bash_keys(tsk):
        with open(tsk.outputs[0].abspath(), 'w') as out_file:
            for key, binding in tsk.env.SHELL_KEYBINDINGS.items():
                # It is supposed to turn out like this:
                # bind '"\C-j": " 2>&1 | less\C-m"'
                print('bind ' + shquote('"{}": "{}"'.format(key, binding)),
                      file=out_file)

    def _make_zsh_keys(tsk):
        with open(tsk.outputs[0].abspath(), 'w') as out_file:
            for key, binding in tsk.env.SHELL_KEYBINDINGS.items():
                print(
                    'bindkey -s {} {}'.format(shquote(key), shquote(binding)),
                    file=out_file)

    for shell in self.env.AVAILABLE_SHELLS:
        out_node = self.path.find_or_declare('keys.' + shell)
        self.add_shell_rc_node(out_node, shell)
        rule = locals()['_make_{}_keys'.format(shell)]
        self(rule=rule, target=out_node, vars=['SHELL_KEYBINDINGS'])

@conf
def build_shell_locals(self):
    """Build local profile and rc configurations."""
    for filetype in ['profile', 'rc']:
        node = self.path.find_resource(join(LOCAL_DIR, filetype + '.sh'))
        if node:
            self.add_shell_node(node, filetype)

def build(ctx):
    ctx.build_shell_env()

    # Source in .bashrc in the .bash_profile. Needs to happen after the shell
    # environment.
    ctx.env.BASH_PROFILE_NODES.append(ctx.path.find_resource([
        'shell', 'sourcebashrc.bash']))

    ctx.build_shell_aliases()
    ctx.build_shell_keybindings()
    ctx.build_shell_locals()

    # Finally, build shell files

    shell_nodes = []
    for shell in ctx.env.AVAILABLE_SHELLS:
        for filetype in ['rc', 'profile']:
            filename = '{}.{}'.format(filetype, shell)
            env_var_name = '{}_{}_NODES'.format(
                shell.upper(), filetype.upper())
            in_nodes = ctx.env[env_var_name]
            out_node = ctx.path.find_or_declare(filename)
            shell_nodes.append(out_node)
            @ctx.rule(target=out_node, source=in_nodes, vars=[env_var_name])
            def _concat(tsk):
                output_node = tsk.outputs[0]
                with open(output_node.abspath(), 'w') as output_file:
                    final_filename = SHELL_FILE_NAMES[output_node.name]
                    print('# ' + final_filename, file=output_file)
                    ctx.concat_nodes(output_file, tsk.inputs)

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

    # Symlink Oh My Zsh
    ctx.symlink_as(os.path.abspath(join(ctx.env.PREFIX, '.oh-my-zsh')),
                   # Make sure to abspath the source, otherwise it will create
                   # a relative link.
                   os.path.abspath(join('shell', 'oh-my-zsh')))
