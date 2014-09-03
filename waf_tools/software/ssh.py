"""Detect and configure SSH."""


def configure(ctx):
    ctx.find_program('ssh', mandatory=False)


def build(ctx):
    if not ctx.env.SSH:
        return
    ctx.env.DOTFILE_NODES.append(ctx.path.find_resource(
        ['dotfiles', 'ssh', 'config']))
