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
    quoted_git = shquote(ctx.env.GIT)
    ctx.env.SHELL_ALIASES['gt'] = quoted_git + ' status'
    ctx.env.SHELL_ALIASES['gobuddygo'] = quoted_git + ' push'
    ctx.env.SHELL_ALIASES['cometome'] = quoted_git + ' pull'

    ctx.env.DOTFILE_NODES += [
        ctx.path.find_resource(['dotfiles', name])
        for name in ['gitconfig', 'gitignore_global']]

    if ctx.env.WC and ctx.env.NUMFMT:
        # Find size of the working tree in a git repo.
        # See here for sources of approaches:
        # http://serverfault.com/questions/351598/get-total-files-size-from-a-file-containing-a-file-list
        ctx.env.SHELL_ALIASES['git-working-tree-size'] = (
            'git ls-files -z | {wc} --bytes --files0-from=- | '
            '{numfmt} --to=iec-i --suffix=B').format(
                wc=shquote(ctx.env.WC),
                numfmt=shquote(ctx.env.NUMFMT))
        # Another approach, using GNU stat and awk:
        #
        # git ls-files -z | while read -d $'\0' filename;
        # do $STAT -c '%s' "$filename"; done |
        # awk '{total+=$1} END {print total}

    if ctx.env.HUB:
        # Hub's alias command `hub alias -s' produces really simple output,
        # which is basically this.
        ctx.env.SHELL_ALIASES['git'] = 'hub'

    if ctx.env.OHCOUNT:
        ctx.install_script('git-count-lines')
