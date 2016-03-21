# -*- coding: utf-8 -*-
"""Detect and configure iTerm2 shell integration."""

def configure(ctx):
    locs = ctx.osx_app_locations('iTerm')
    ctx.msg('Checking for iTerm2', locs[0] if locs else False)
    ctx.env.ITERM2 = bool(locs)

def build(ctx):
    if not ctx.env.ITERM2:
        return

    # The instructions for shell integration [1] instruct to put this in
    # .bash_profile and .zshrc. But all the code in zsh_startup.in is wrapped
    # in a login shell conditional statement, so there's really no reason not
    # to put it in .zprofile.
    #
    # [1]: https://iterm2.com/shell_integration.html
    for shell in ctx.env.AVAILABLE_SHELLS:
        ctx.add_shell_profile_node(ctx.path.find_resource([
            'shell', 'iterm2', shell + '_startup.in']), shell)
