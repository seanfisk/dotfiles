# -*- coding: utf-8 -*-
"""Install htmlink."""

def build(ctx):
    ctx.install_subst_script('htmlink', PYTHON=ctx.env.DEFAULT_PYTHON)
