# -*- coding: utf-8 -*-
"""Install htmlink."""

def build(ctx):
    ctx.install_script(ctx.path.find_resource(['scripts', 'htmlink']))
