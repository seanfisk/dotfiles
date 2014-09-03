"""Detect and configure Mercurial (hg)."""


def configure(ctx):
    ctx.find_program('hg', mandatory=False)


def build(ctx):
    if not ctx.env.HG:
        return
    ctx.env.DOTFILE_NODES.append(ctx.path.find_resource(['dotfiles', 'hgrc']))
