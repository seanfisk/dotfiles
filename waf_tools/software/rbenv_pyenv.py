"""Detect and configure rbenv and pyenv."""

import os


def configure(ctx):
    ctx.find_program('pyenv', mandatory=False)
    ctx.find_program('rbenv', mandatory=False)


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


def build(ctx):
    # Build files that load rbenv and pyenv
    for shell in ctx.env.SHELLS:
        for prefix in ['rb', 'py']:
            tool = prefix + 'env'
            path = ctx.env[tool.upper()]
            if path:
                out_node = ctx.path.find_or_declare(
                    '{0}.{1}'.format(tool, shell))
                ctx.env.SHELL_RC_NODES[shell].append(out_node)
                ctx(rule=_make_rbenv_pyenv_file, target=out_node, always=True)
