# -*- coding: utf-8 -*-
"""Detect and configure SSH."""

def configure(ctx):
    ctx.find_program('ssh', mandatory=False)

def build(ctx):
    if not ctx.env.SSH:
        return

    in_node = ctx.path.find_resource(['dotfiles', 'ssh', 'config.in'])
    out_node = in_node.change_ext(ext='', ext_in='.in')
    ctx(features='subst',
        source=in_node,
        target=out_node,
        TEMP_DIR=ctx.env.TEMP_DIR,
        TEMP_DIR_LEN=(
            ' ' *
            (len('@TEMP_DIR_LEN@') - len('@TEMP_DIR@') + len(ctx.env.TEMP_DIR))
        ))

    ctx.install_dotfile(out_node)
