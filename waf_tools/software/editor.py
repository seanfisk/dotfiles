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
        # Rope is not Python 3-compatible yet.
        ctx.env.PYENV_VIRTUALENV_DEFAULT_PACKAGES += [
            'elpy==1.5.1',
            'jedi==0.8.1-final0',
            'flake8==2.2.3',
            'mccabe==0.2.1',
            'pep8==1.5.7',
            'pyflakes==0.8.1',
        ]
    else:
        editor = 'nano'
    ctx.env.SHELL_ENV['EDITOR'] = shquote(editor)
