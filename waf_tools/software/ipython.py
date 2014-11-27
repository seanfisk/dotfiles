# -*- coding: utf-8 -*-
"""Detect and configure IPython."""

def _concatenate(tsk):
    with open(tsk.outputs[0].abspath(), 'w') as output_file:
        # Concatenate the first input file.
        with open(tsk.inputs[0].abspath()) as input_file:
            for line in input_file:
                output_file.write(line)

        # Concatenate the other input files, adding a blank line in between
        # each.
        for input_node in tsk.inputs[1:]:
            print(file=output_file)
            with open(input_node.abspath()) as input_file:
                for line in input_file:
                    output_file.write(line)

def build(ctx):
    # IPython is usually installed to and used from Python virtual
    # environments. Because of this, it is likely IPython won't be installed to
    # a system path and won't be detected by the configuration script. But
    # installing the IPython config files on systems which don't have it really
    # doesn't hurt. We'll use this simple rule: if pyenv is installed, we'll
    # install the IPython config files.
    if not ctx.env.PYENV:
        return

    parent_path = ['dotfiles', 'ipython', 'profile_default']
    in_nodes = [
        ctx.path.find_resource(parent_path + ['ipython_config-base.py']),
    ]
    out_node = ctx.path.find_or_declare(parent_path + ['ipython_config.py'])

    if ctx.env.POWERLINE:
        in_nodes.append(ctx.path.find_resource(parent_path + ['powerline.py']))

    ctx(rule=_concatenate,
        target=out_node,
        source=in_nodes)

    ctx.install_dotfile(out_node)
