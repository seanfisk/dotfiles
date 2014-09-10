"""Detect and configure rbenv and pyenv."""

import os
from os.path import join
import subprocess
from pipes import quote as shquote


try:
    from subprocess import DEVNULL  # Python 3
except ImportError:
    DEVNULL = open(os.devnull, 'wb')  # Python 2


def configure(ctx):
    ctx.find_program('rbenv', mandatory=False)
    ctx.find_program('pyenv', mandatory=False)

    # Check for pyenv-virtualenv. In the Homebrew install, pyenv-virtualenv is
    # an actual executable and is also accessible as a subcommand. However,
    # when installing as a pyenv plugin it is only accessible as a subcommand.
    # The value of env variable is just a Boolean since we may not have an
    # actual executable.
    ctx.env.PYENV_VIRTUALENV = False
    if ctx.env.PYENV:
        ret = subprocess.call(
            [ctx.env.PYENV, 'virtualenv-init', '-'],
            stdout=DEVNULL,
            stderr=DEVNULL,
        )
        ctx.env.PYENV_VIRTUALENV = ret == 0

        ctx.env.PYENV_ROOT = subprocess.check_output(
            [ctx.env.PYENV, 'root']).decode('ascii').rstrip()

    ctx.msg('Checking for pyenv-virtualenv', ctx.env.PYENV_VIRTUALENV)

    # Set up a list of Python packages to install into a default pyenv
    # virtualenv using pyenv hooks. Create the list regardless of the
    # availability of pyenv so that other files don't get errors.
    ctx.env.PYENV_VIRTUALENV_DEFAULT_PACKAGES = ['ipython']


def _make_rbenv_pyenv_file(tsk):
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
    tool_path = tsk.env[tool.upper()]
    with open(output_node.abspath(), 'w') as output_file:
        # Instead of running pyenv and rbenv to generate code and eval'ing it
        # every time, just generate it now and source it. Because we aren't
        # running it from within a shell, we need to tell rbenv and pyenv what
        # shell for which to generate the code. Otherwise, they determine it
        # through ps or $SHELL, $SHELL is just plain wrong, because that is the
        # login shell, which is not necessarily the shell that is running.
        ret = tsk.exec_command(
            [tool_path, 'init', '-', shell], stdout=output_file)

    return ret


def build(ctx):
    for shell in ctx.env.SHELLS:
        # Build files that load rbenv and pyenv
        for prefix in ['rb', 'py']:
            tool = prefix + 'env'
            path = ctx.env[tool.upper()]
            if path:
                out_node = ctx.path.find_or_declare(
                    '{0}.{1}'.format(tool, shell))
                ctx.env['{}_RC_NODES'.format(shell.upper())].append(out_node)
                ctx(rule=_make_rbenv_pyenv_file, target=out_node,
                    vars=[tool.upper()])

        if ctx.env.PYENV_VIRTUALENV:
            # If pyenv-virtualenv is installed, generate a file for it, too.
            out_node = ctx.path.find_or_declare(
                'pyenv-virtualenv.{}'.format(shell))
            ctx.env['{}_RC_NODES'.format(shell.upper())].append(out_node)

            @ctx.rule(target=out_node, vars=['PYENV', 'PYENV_VIRTUALENV'])
            def make_pyenv_virtualenv_file(tsk):
                output_node = tsk.outputs[0]
                # The shell is determined by the output file's extension.
                # suffix() returns the extension with a preceding dot, so strip
                # it off.
                _, ext = os.path.splitext(output_node.name)
                shell = ext[1:]
                with open(output_node.abspath(), 'w') as output_file:
                    ret = tsk.exec_command(
                        [ctx.env.PYENV, 'virtualenv-init', '-', shell],
                        stdout=output_file)
                return ret

    if ctx.env.PYENV_VIRTUALENV:
        # Also generate the hook that installs default packages.

        # See here for the location of hooks:
        # https://github.com/yyuu/pyenv/wiki/Authoring-plugins
        in_node = ctx.path.find_resource([
            'dotfiles', 'pyenv', 'pyenv.d',
            'virtualenv', 'install-default-packages.bash.in',
        ])
        out_node = in_node.change_ext(ext='.bash', ext_in='.bash.in')
        ctx(features='subst',
             target=out_node,
             source=in_node,
             DEFAULT_PACKAGES=' '.join(
                 shquote(package) for package
                 in ctx.env.PYENV_VIRTUALENV_DEFAULT_PACKAGES))

        # We could probably just use ctx.install_dotfile() here. But we'll
        # be careful and use the root that pyenv reports.
        ctx.install_as(
            join(ctx.env.PYENV_ROOT, out_node.path_from(
                ctx.bldnode.find_dir(['dotfiles', 'pyenv']))),
            out_node)