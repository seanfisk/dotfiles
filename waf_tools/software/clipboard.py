"""Detect and configure clipboard programs."""

from pipes import quote as shquote


def configure(ctx):
    if ctx.env.MACOSX:
        for action in ['copy', 'paste']:
            path = ctx.find_program('pb' + action)
            ctx.env[action.upper() + '_COMMAND'] = path
    elif ctx.env.LINUX:
        xclip_path = ctx.find_program('xclip', mandatory=False)
        if xclip_path:
            base_cmd_list = [xclip_path, '-sel', 'c']
            ctx.env.COPY_COMMAND = ' '.join(base_cmd_list + ['-in'])
            ctx.env.PASTE_COMMAND = ' '.join(base_cmd_list + ['-out'])


def build(ctx):
    if not (ctx.env.COPY_COMMAND and ctx.env.PASTE_COMMAND):
        return

    ctx.env.SHELL_ALIASES['copy'] = shquote(ctx.env.COPY_COMMAND)
    ctx.env.SHELL_ALIASES['paste'] = shquote(ctx.env.PASTE_COMMAND)

    # aria2 might be available, wget is always available
    downloader = shquote(ctx.env.ARIA2C or ctx.env.WGET)
    # Download from clipboard
    ctx.env.SHELL_ALIASES['dl'] = downloader + ' "$(paste)"'
    # Download to clipboard
    ctx.env.SHELL_ALIASES['dltc'] = (
        shquote(ctx.env.WGET) + ' --no-verbose --output-document=- "$(paste)" '
        '| copy')
