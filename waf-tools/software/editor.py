# -*- coding: utf-8 -*-
"""Detect and configure Emacs and other editors."""

from shlex import quote as shquote

def configure(ctx):
    ctx.find_program('emacsclient', mandatory=False)
    ctx.find_program('nano') # nano is a mandatory fallback
    ctx.find_program('e-sink', var='E_SINK', mandatory=False)

def build(ctx):
    if ctx.env.EMACSCLIENT:
        # This variable should be a one-element list, see below for how it's
        # used.
        editor = ctx.env.EMACSCLIENT
        # This variable can have multiple arguments, also see below for how
        # it's used.
        editor_maybe_nonblock = ctx.env.EMACSCLIENT + ['--no-wait']

        if ctx.env.E_SINK:
            ctx.install_script('e')
        else:
            ctx.env.SHELL_ALIASES['e'] = ctx.shquote_cmd(editor_maybe_nonblock)

        # Add Python packages for Emacs.
        # Rope is not Python 3-compatible yet.
        ctx.env.PYENV_VIRTUALENV_DEFAULT_PACKAGES += [
            'elpy==1.6.0',
            'jedi==0.8.1-final0',
            'flake8==2.3.0',
            'mccabe==0.3',
            'pep8==1.5.7',
            'pyflakes==0.8.1',
        ]
    else:
        # Nano doesn't have a non-blocking mode.
        editor = editor_maybe_nonblock = ctx.env.NANO

    # Most programs that use EDITOR expect it to block. Here are the programs
    # that I use that I expect to use the EDITOR variable:
    #
    # git config -e; git commit
    # hg commit
    # crontab -e
    #
    # Different programs handle the value differently. For example, git
    # evaluates the value using shell rules, while crontab can only take a
    # single argument. For this reason, it's best to stick to a single
    # argument. If multiple are needed in the future, create a wrapper script.
    ctx.env.SHELL_ENV['EDITOR'] = shquote(editor[0])

    # Some programs also use VISUAL, but I haven't found a reason to set that
    # yet. Most programs use that before checking EDITOR, adding yet another
    # layer of complexity that's currently not needed.

    # Homebrew also recognizes VISUAL and EDITOR, but does not need its editor
    # to block. We therefore manually override the editor. Homebrew evaluates
    # the value using shell rules, and does therefore not need a script.
    if ctx.env.BREW:
        ctx.env.SHELL_ENV['HOMEBREW_EDITOR'] = shquote(ctx.shquote_cmd(
            editor_maybe_nonblock))
