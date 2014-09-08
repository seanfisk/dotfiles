"""Detect and configure Homebrew."""


def configure(ctx):
    ctx.find_program('brew', mandatory=False)


def build(ctx):
    if not ctx.env.BREW:
        return
    # Homebrew deletes (Tex)Info manuals unless you bar it from doing so. Heck
    # yes I want these, I use Emacs!
    ctx.env.SHELL_ENV['HOMEBREW_KEEP_INFO'] = 'true'
