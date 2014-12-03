# -*- coding: utf-8 -*-
"""Detect and configure Mercurial (hg)."""

def configure(ctx):
    ctx.find_program('hg', mandatory=False)

def build(ctx):
    if not ctx.env.HG:
        return
    ctx.install_dotfile(ctx.path.find_resource(['dotfiles', 'hgrc']))
