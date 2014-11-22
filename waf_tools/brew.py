"""Detect and configure Homebrew/Linuxbrew."""


def configure(ctx):
    ctx.find_program('brew', mandatory=False)
