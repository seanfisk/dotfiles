# -*- coding: utf-8 -*-
"""Detect and configure Git."""

from pipes import quote as shquote

def configure(ctx):
    ctx.find_program('git', mandatory=False)
    ctx.find_program('hub', mandatory=False)
    # These tools are needed for Git aliases.
    ctx.find_gnu_util('wc', mandatory=False)
    ctx.find_gnu_util('numfmt', mandatory=False)
    ctx.find_program('ohcount', mandatory=False)

def build(ctx):
    if not ctx.env.GIT:
        return

    # Hub's alias command `hub alias -s' produces really simple output:
    #
    #     alias git=hub
    #
    # Just use hub's path instead of git if we have it.
    if ctx.env.HUB:
        git = ctx.env.HUB
        ctx.env.SHELL_ALIASES['git'] = ctx.shquote_cmd(git)
    else:
        git = ctx.env.GIT

    ctx.env.SHELL_ALIASES['g'] = ctx.shquote_cmd(git)
    ctx.env.SHELL_ALIASES['gt'] = ctx.shquote_cmd(git + ['status'])
    ctx.env.SHELL_ALIASES['gobuddygo'] = ctx.shquote_cmd(git + ['push'])
    ctx.env.SHELL_ALIASES['cometome'] = ctx.shquote_cmd(git + ['pull'])
    # Update dotfiles alias
    ctx.env.SHELL_ALIASES['ud'] = ' && '.join([
        ctx.shquote_cmd(['cd', ctx.srcnode.abspath()]),
        ctx.shquote_cmd(git + ['pull']),
        # Distclean to avoid possible errors. A full rebuild does not take
        # long.
        ctx.shquote_cmd([
            './waf', 'distclean', 'configure', 'build', 'install']),
    ])

    for name in ['gitconfig', 'gitignore-global']:
        ctx.install_dotfile(ctx.path.find_resource(['dotfiles', name]))

    ctx.install_subst_script('find-file-exts', PYTHON=ctx.env.DEFAULT_PYTHON)

    if ctx.env.WC and ctx.env.NUMFMT:
        # Find size of the working tree in a git repo.
        # See here for sources of approaches:
        # http://serverfault.com/questions/351598/get-total-files-size-from-a-file-containing-a-file-list
        ctx.env.SHELL_ALIASES['git-working-tree-size'] = (
            '{git} ls-files -z | {wc} --bytes --files0-from=- | '
            '{numfmt} --to=iec-i --suffix=B').format(
                git=ctx.shquote_cmd(git),
                wc=ctx.shquote_cmd(ctx.env.WC),
                numfmt=ctx.shquote_cmd(ctx.env.NUMFMT))
        # Another approach, using GNU stat and awk:
        #
        # git ls-files -z | while read -d $'\0' filename;
        # do $STAT -c '%s' "$filename"; done |
        # awk '{total+=$1} END {print total}

    if ctx.env.OHCOUNT:
        ctx.install_subst_script(
            'git-count-lines', GIT=shquote(ctx.env.GIT[0]))
