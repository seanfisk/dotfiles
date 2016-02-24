# -*- coding: utf-8 -*-
"""Detect and configure Ghostscript."""

from pipes import quote as shquote

def configure(ctx):
    ctx.find_program('gs', mandatory=False)

def build(ctx):
    if not ctx.env.GS:
        return
    ctx.install_subst_script('pdf-compress', GS=shquote(ctx.env.GS[0]))
