"""Detect and configure Homebrew."""


def configure(ctx):
    ctx.find_program('brew', mandatory=False)
