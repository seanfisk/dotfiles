"""Detect and configure Emacs and other editors."""

from pipes import quote as shquote


def configure(ctx):
    ctx.find_program('emacsclient', mandatory=False)
    ctx.find_program('e-sink', var='E_SINK', mandatory=False)


def build(ctx):
    if ctx.env.EMACSCLIENT:
        editor = 'emacsclient --alternate-editor='
        if ctx.env.E_SINK:
            ctx.install_script('e')
        else:
            ctx.env.SHELL_ALIASES['e'] = 'emacsclient --no-wait'

        # Add Python packages.
        ctx.env.PYENV_VIRTUALENV_DEFAULT_PACKAGES += [
            'elpy',
            # Rope is not Python 3-compatible yet.
            # 'rope',
            'jedi',
        ]
    else:
        editor = 'nano'
    ctx.env.SHELL_ENV['EDITOR'] = shquote(editor)
