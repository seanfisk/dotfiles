# -*- coding: utf-8 -*-
"""Detect and configure clipboard programs."""

def configure(ctx):
    if ctx.env.MACOSX:
        for action in ['copy', 'paste']:
            path = ctx.find_program('pb' + action)
            ctx.env[action.upper() + '_COMMAND'] = path
    elif ctx.env.LINUX:
        path = ctx.find_program('xclip', mandatory=False)
        if path:
            base_cmd_list = path + ['-sel', 'c']
            ctx.env.COPY_COMMAND = base_cmd_list + ['-in']
            ctx.env.PASTE_COMMAND = base_cmd_list + ['-out']

    # For the sha sum alias
    ctx.find_gnu_util('sha256sum', mandatory=False)
    ctx.find_program('cut', mandatory=False)

def build(ctx):
    if not (ctx.env.COPY_COMMAND and ctx.env.PASTE_COMMAND):
        return

    for alias in ['copy', 'paste']:
        ctx.env.SHELL_ALIASES[alias] = ctx.shquote_cmd(
            ctx.env[alias.upper() + '_COMMAND'])

    # aria2 might be available, wget is always available
    downloader = ctx.shquote_cmd(ctx.env.ARIA2C or ctx.env.WGET)
    # Download URL in clipboard
    ctx.env.SHELL_ALIASES['dlc'] = downloader + ' "$(paste)"'
    # Download contents to stdout
    ctx.env.SHELL_ALIASES['dlo'] = (ctx.shquote_cmd(
        ctx.env.WGET + ['--no-verbose', '--output-document=-']))
    # Download URL in clipboard and send contents to stdout
    ctx.env.SHELL_ALIASES['dlco'] = 'dlo "$(paste)"'
    # Download URL in clipboard and put contents in clipboard
    ctx.env.SHELL_ALIASES['dlcc'] = 'dlo "$(paste)" | copy'
    # Download URL in clipboard and do a SHA-256 sum on it (useful for Chef).
    if ctx.env.SHA256SUM and ctx.env.CUT:
        ctx.env.SHELL_ALIASES['dlsha'] = (
            'dlo "$(paste)" | ' + ctx.shquote_cmd(ctx.env.SHA256SUM) +
            ' - | ' + ctx.shquote_cmd(ctx.env.CUT) + " -d' ' -f1 | copy")
