# -*- coding: utf-8 -*-
"""Detect and configure QPDF."""

def configure(ctx):
    ctx.find_program('qpdf', mandatory=False)

def build(ctx):
    if not ctx.env.QPDF:
        return
    ctx.install_script('pdf-merge')
    ctx.env.SHELL_ALIASES['pdf-join'] = 'pdf-merge'
