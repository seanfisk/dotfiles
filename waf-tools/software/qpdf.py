# -*- coding: utf-8 -*-
"""Detect and configure QPDF."""

from pipes import quote as shquote

def configure(ctx):
    ctx.find_program('qpdf', mandatory=False)

def build(ctx):
    if not ctx.env.QPDF:
        return
    ctx.install_subst_script('pdf-merge', QPDF=shquote(ctx.env.QPDF[0]))
    ctx.env.SHELL_ALIASES['pdf-join'] = 'pdf-merge'
