# -*- coding: utf-8 -*-
"""Detect and configure plain Python-specific tools.

This file is intended to contain tools that are useful with a plain Python, and
not specific to a Python-related tool.
"""

def build(ctx):
    if not ctx.env.DEFAULT_PYTHON:
        return

    ctx.install_script(ctx.path.find_resource(['scripts', 'pyver']))
