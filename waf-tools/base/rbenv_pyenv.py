# -*- coding: utf-8 -*-
"""Detect and configure rbenv and pyenv."""

import os
from os.path import join
from shlex import quote as shquote
import re
import subprocess

import waflib

TOOL_FILENAME_RE = re.compile(r'(?P<tool>.*)-.*\.(?P<shell>.*)')

def _split_exports(lines):
    profile_lines = []
    rc_lines = []
    for line in lines:
        if line.startswith('export '):
            profile_lines.append(line)
        else:
            rc_lines.append(line)
    return (profile_lines, rc_lines)

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

        ctx.env.PYENV_ROOT = ctx.cmd_and_log(
            ctx.env.PYENV + ['root'], quiet=waflib.Context.BOTH).rstrip()

    ctx.msg('Checking for pyenv-virtualenv', ctx.env.PYENV_VIRTUALENV)

    # Set up a list of Python packages to install into a default pyenv
    # virtualenv using pyenv hooks. Create the list regardless of the
    # availability of pyenv so that other files don't get errors.
    ctx.env.PYENV_VIRTUALENV_DEFAULT_PACKAGES = ['ipython==4.1.1']

def _make_rbenv_pyenv_files(tsk):
    # The generated code loads pyenv and rbenv into the shell session. We need
    # to load this in the rc file because it loads up shell functions. For
    # example, `pyenv shell' is only available when this `eval' command is run
    # *within the shell*.
    profile_node, rc_node = tsk.outputs
    # XXX Parsing stuff we've generated is kind of ugly, but there aren't a lot
    # of better options AFAIK.
    match = TOOL_FILENAME_RE.fullmatch(rc_node.name)
    if match is None:
        raise ValueError('Unparseable tool filename: {}'.format(rc_node.name))
    tool = match.group('tool')
    shell = match.group('shell')
    tool_cmd = tsk.env[tool.upper()]
    # Instead of running pyenv and rbenv to generate code and eval'ing it every
    # time, just generate it now and source it. Because we aren't running it
    # from within a shell, we need to tell rbenv and pyenv what shell for which
    # to generate the code. Otherwise, they determine it through ps or $SHELL,
    # $SHELL is just plain wrong, because that is the login shell, which is not
    # necessarily the shell that is running.
    profile_lines, rc_lines = _split_exports(tsk.generator.bld.cmd_and_log(
        tool_cmd + ['init', '-', shell],
        quiet=waflib.Context.BOTH).splitlines())

    # If we installed the tool using Homebrew, rewrite the path to the opt/
    # directory instead of using a specific version. This allows our file
    # to survive upgrades of the tool.
    try:
        brew_opt_path = tsk.generator.bld.cmd_and_log(
            tsk.env.BREW + ['--prefix', tool],
            quiet=waflib.Context.BOTH).rstrip()
    except waflib.Errors.WafError:
        pass
    else:
        brew_cellar_path = os.path.realpath(brew_opt_path)
        rc_lines[0] = rc_lines[0].replace(
            brew_cellar_path, brew_opt_path)
        rc_lines.insert(
            0,
            "# Use of Homebrew's opt/ directory was hacked in here; "
            'this is not stock')

    profile_node.write('\n'.join(profile_lines))
    rc_node.write('\n'.join(rc_lines))

def _make_pyenv_virtualenv_files(tsk):
    profile_node, rc_node = tsk.outputs
    # The shell is determined by the output file's extension.
    # suffix() returns the extension with a preceding dot, so strip
    # it off.
    ext = os.path.splitext(rc_node.name)[1]
    shell = ext[1:]
    profile_lines, rc_lines = _split_exports(
        tsk.generator.bld.cmd_and_log(
            tsk.env.PYENV + ['virtualenv-init', '-', shell],
            quiet=waflib.Context.BOTH).splitlines())

    # XXX: The code introduced in this commit causes ${PATH} to be
    # resolved when this code is output, not when it is run.
    #
    # https://github.com/yyuu/pyenv-virtualenv/commit/
    # dfd165506933d2f81e3b5a0eb6528f06ce653d01
    # #diff-0df4de328d02bb89f5b3ef3838d1ab1bL68
    # Also see my PR: https://github.com/yyuu/pyenv-virtualenv/pull/154
    #
    # For now, we have a hacky fix.
    shims_path = join(tsk.generator.bld.cmd_and_log(
        tsk.env.BREW + ['--prefix', 'pyenv-virtualenv'],
        quiet=waflib.Context.BOTH).rstrip(), 'shims')
    profile_lines[0] = 'export PATH="{}:$PATH"'.format(shims_path)

    profile_node.write('\n'.join(profile_lines))
    rc_node.write('\n'.join(rc_lines))

def build(ctx):
    for shell in ctx.env.AVAILABLE_SHELLS:
        # Build files that load rbenv and pyenv
        for prefix in ['rb', 'py']:
            tool = prefix + 'env'
            tool_up = tool.upper()
            path = ctx.env[tool_up]
            if path:
                out_nodes = []
                for filetype in ['profile', 'rc']:
                    out_node = ctx.path.find_or_declare(
                        '{}-{}.{}'.format(tool, filetype, shell))
                    out_nodes.append(out_node)
                    ctx.add_shell_node(out_node, filetype, shell)
                ctx(rule=_make_rbenv_pyenv_files, target=out_nodes,
                    vars=[tool_up])

        if ctx.env.PYENV_VIRTUALENV:
            # If pyenv-virtualenv is installed, generate a file for it, too.
            out_nodes = []
            for filetype in ['profile', 'rc']:
                out_node = ctx.path.find_or_declare(
                    'pyenv-virtualenv-{}.{}'.format(filetype, shell))
                out_nodes.append(out_node)
                ctx.add_shell_node(out_node, filetype, shell)

            ctx(rule=_make_pyenv_virtualenv_files, target=out_nodes,
                vars=['PYENV', 'PYENV_VIRTUALENV'])

    # Install requirements file for the default Python.
    requirements_default_py_node = ctx.path.find_resource([
        'dotfiles', 'pyenv', 'pyenv.d', 'requirements-default-python.txt'])
    ctx.install_dotfile(requirements_default_py_node)

    if ctx.env.PYENV_VIRTUALENV:
        # Disable prompt changing
        # See here: https://github.com/yyuu/pyenv-virtualenv/issues/135
        ctx.env.SHELL_ENV['PYENV_VIRTUALENV_DISABLE_PROMPT'] = '1'

        # Generate a default virtualenv requirements file.
        requirements_base = 'requirements-default-virtualenv.txt'
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
            PYTHON=ctx.env.DEFAULT_PYTHON,
            PYENV=repr(ctx.env.PYENV[0]),
            REQUIREMENTS_DEFAULT_PYTHON_PATH=repr(ctx.dotfile_install_path(
                requirements_default_py_node)),
            REQUIREMENTS_DEFAULT_VENV_PATH=repr(requirements_install_path))
