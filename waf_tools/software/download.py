"""Detect and configure Wget and Aria2."""


def configure(ctx):
    ctx.find_program('aria2c', mandatory=False)
    ctx.find_program('wget')  # Wget is mandatory!!!
