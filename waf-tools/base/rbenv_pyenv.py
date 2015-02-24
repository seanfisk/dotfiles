# -*- coding: utf-8 -*-
"""Detect and configure rbenv and pyenv."""

import os
from os.path import join
from shlex import quote as shquote
import subprocess

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
        ret = ctx.exec_command(
            ctx.env.PYENV + ['virtualenv-init', '-'],
            # We don't need the output, so just throw it away.
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        ctx.env.PYENV_VIRTUALENV = ret == 0

        ctx.env.PYENV_ROOT = ctx.cmd_and_log(ctx.env.PYENV + ['root']).rstrip()

    ctx.msg('Checking for pyenv-virtualenv', ctx.env.PYENV_VIRTUALENV)

    # Set up a list of Python packages to install into a default pyenv
    # virtualenv using pyenv hooks. Create the list regardless of the
    # availability of pyenv so that other files don't get errors.
    ctx.env.PYENV_VIRTUALENV_DEFAULT_PACKAGES = ['ipython==2.4.0']

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
    tool_cmd = tsk.env[tool.upper()]
    with open(output_node.abspath(), 'w') as output_file:
        # Instead of running pyenv and rbenv to generate code and eval'ing it
        # every time, just generate it now and source it. Because we aren't
        # running it from within a shell, we need to tell rbenv and pyenv what
        # shell for which to generate the code. Otherwise, they determine it
        # through ps or $SHELL, $SHELL is just plain wrong, because that is the
        # login shell, which is not necessarily the shell that is running.
        ret = tsk.exec_command(
            tool_cmd + ['init', '-', shell], stdout=output_file)

    return ret

def build(ctx):
    for shell in ctx.env.AVAILABLE_SHELLS:
        # Build files that load rbenv and pyenv
        for prefix in ['rb', 'py']:
            tool = prefix + 'env'
            path = ctx.env[tool.upper()]
            if path:
                out_node = ctx.path.find_or_declare(
                    '{}.{}'.format(tool, shell))
                ctx.add_shell_rc_node(out_node, shell)
                ctx(rule=_make_rbenv_pyenv_file, target=out_node,
                    vars=[tool.upper()])

        if ctx.env.PYENV_VIRTUALENV:
            # If pyenv-virtualenv is installed, generate a file for it, too.
            out_node = ctx.path.find_or_declare('pyenv-virtualenv.' + shell)
            ctx.add_shell_rc_node(out_node, shell)

            @ctx.rule(target=out_node, vars=['PYENV', 'PYENV_VIRTUALENV'])
            def _make_pyenv_virtualenv_file(tsk):
                output_node = tsk.outputs[0]
                # The shell is determined by the output file's extension.
                # suffix() returns the extension with a preceding dot, so strip
                # it off.
                _, ext = os.path.splitext(output_node.name)
                shell = ext[1:]
                with open(output_node.abspath(), 'w') as output_file:
                    ret = tsk.exec_command(
                        ctx.env.PYENV + ['virtualenv-init', '-', shell],
                        stdout=output_file)
                return ret

    if ctx.env.PYENV_VIRTUALENV:
        # Generate a default virtualenv requirements file.
        requirements_base = 'default-virtualenv-requirements.txt'
        requirements_node = ctx.path.find_or_declare([
            'dotfiles', 'pyenv', 'pyenv.d', requirements_base])
        @ctx.rule(target=requirements_node,
                  vars=['PYENV_VIRTUALENV_DEFAULT_PACKAGES'])
        def _make_default_venv_reqs_file(tsk):
            with open(tsk.outputs[0].abspath(), 'w') as out_file:
                for requirement in ctx.env.PYENV_VIRTUALENV_DEFAULT_PACKAGES:
                    print(requirement, file=out_file)

        pyenv_build_node = ctx.bldnode.find_dir(['dotfiles', 'pyenv'])
        requirements_install_path = join(
            ctx.env.PYENV_ROOT,
            requirements_node.path_from(pyenv_build_node))
        # Also generate the hook that installs default packages.
        # See here for the location of hooks:
        # https://github.com/yyuu/pyenv/wiki/Authoring-plugins
        hook_in_node = ctx.path.find_resource([
            'dotfiles', 'pyenv', 'pyenv.d',
            'virtualenv', 'install-default-packages.bash.in',
        ])
        hook_out_node = hook_in_node.change_ext(ext='.bash', ext_in='.bash.in')
        ctx(features='subst',
            target=hook_out_node,
            source=hook_in_node,
            REQUIREMENTS_PATH=shquote(requirements_install_path))

        # We could probably just use ctx.install_dotfile() here. But we'll
        # be careful and use the root that pyenv reports.
        ctx.install_as(
            join(ctx.env.PYENV_ROOT,
                 hook_out_node.path_from(pyenv_build_node)),
            hook_out_node)
        ctx.install_as(
            join(ctx.env.PYENV_ROOT,
                 requirements_node.path_from(pyenv_build_node)),
            requirements_node)

        # Install shortcut scripts.
        ctx.install_subst_script('venv', PYENV=shquote(ctx.env.PYENV[0]))
        ctx.install_subst_script(
            'pyup',
            PYENV=repr(ctx.env.PYENV[0]),
            DEFAULT_PYTHON_REQUIREMENTS_PATH=repr(ctx.path.find_resource(
                'requirements-default.txt').abspath()),
            DEFAULT_VENV_REQUIREMENTS_PATH=repr(requirements_install_path))
