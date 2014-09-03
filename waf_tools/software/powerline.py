"""Detect and configure Powerline."""

import os
from os.path import join
from pipes import quote as shquote


def configure(ctx):
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


def build(ctx):
    if not ctx.env.POWERLINE:
        return

    bash_powerline_node = ctx.path.find_or_declare('powerline.bash')
    ctx.env.SHELL_RC_NODES['bash'].append(bash_powerline_node)

    @ctx.rule(target=bash_powerline_node, always=True)
    def make_bash_powerline(tsk):
        bash_powerline_file = ctx.get_powerline_path(
            join('bindings', 'bash', 'powerline.sh'))
        contents = '''{powerline_daemon} --quiet
POWERLINE_BASH_CONTINUATION=1
POWERLINE_BASH_SELECT=1
source {bash_powerline_file}
'''\
        .format(
            powerline_daemon=shquote(tsk.env.POWERLINE_DAEMON),
            bash_powerline_file=shquote(bash_powerline_file),
        )

        with open(tsk.outputs[0].abspath(), 'w') as output_file:
            output_file.write(contents)

    zsh_powerline_node = ctx.path.find_or_declare('powerline.zsh')
    ctx.env.SHELL_RC_NODES['zsh'].append(zsh_powerline_node)

    @ctx.rule(target=zsh_powerline_node, always=True)
    def make_zsh_powerline(tsk):
        zsh_powerline_file = ctx.get_powerline_path(
            join('bindings', 'zsh', 'powerline.zsh'))
        contents = '''{powerline_daemon} --quiet
source {zsh_powerline_file}
'''\
        .format(
            powerline_daemon=shquote(tsk.env.POWERLINE_DAEMON),
            zsh_powerline_file=shquote(zsh_powerline_file),
        )
        with open(tsk.outputs[0].abspath(), 'w') as output_file:
            output_file.write(contents)

    # Template the Powerline config file with the path to the segments.
    in_node = ctx.path.find_resource([
        'dotfiles', 'config', 'powerline', 'config.json.in'])
    out_node = ctx.path.find_or_declare([
        'config', 'powerline', 'config.json'])
    ctx.env.DOTFILE_NODES.append(out_node)
    powerline_segments_path = join(ctx.env.PREFIX, '.config', 'powerline')
    ctx(features='subst',
        source=in_node,
        target=out_node,
        # TODO: Change this to use the Python json module.
        POWERLINE_SEGMENTS_PATH=powerline_segments_path)

    # Install Powerline configuration files
    # TODO: Change this to ctx.ant_glob(...) or something better than os.walk()
    for dirpath, dirnames, filenames in os.walk(join(
            'dotfiles', 'config', 'powerline')):
        for filename in filenames:
            # Don't find any files that were templated.
            if not filename.endswith('.in'):
                ctx.env.DOTFILE_NODES.append(ctx.path.find_resource(
                    join(dirpath, filename)))
