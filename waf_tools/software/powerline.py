"""Detect and configure Powerline."""

from os.path import join
from pipes import quote as shquote

import waflib


def options(ctx):
    # Add a command-line option to explicity disable Powerline.
    ctx.add_option('--disable-powerline', action='store_true', default=False,
                   help='Explicitly disable Powerline')


def configure(ctx):
    if ctx.options.disable_powerline:
        ctx.msg('Checking for Powerline', 'disabled', color='YELLOW')
        return

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
    ctx.env.BASH_RC_NODES.append(bash_powerline_node)

    @ctx.rule(target=bash_powerline_node, vars=['POWERLINE_DAEMON'])
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
    ctx.env.ZSH_RC_NODES.append(zsh_powerline_node)

    @ctx.rule(target=zsh_powerline_node, vars=['POWERLINE_DAEMON'])
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
        'dotfiles', 'config', 'powerline', 'config.cjson.in'])
    out_node = in_node.change_ext(ext='.cjson', ext_in='.cjson.in')
    powerline_segments_path = join(ctx.env.PREFIX, '.config', 'powerline')
    ctx(features='subst',
        source=in_node,
        target=out_node,
        # TODO: Change this to use the Python json module.
        POWERLINE_SEGMENTS_PATH=powerline_segments_path)

    ctx(source=ctx.path.ant_glob(
        'dotfiles/config/powerline/**/*.cjson') + [out_node])

    # Install segments file.
    ctx.install_dotfile(ctx.path.find_resource([
        'dotfiles', 'config', 'powerline', 'powerline_sean_segments.py']))


# Install Powerline configuration files after processing.
@waflib.TaskGen.extension('.json')
def process_json(tsk_gen, node):
    tsk_gen.bld.install_dotfile(node)
