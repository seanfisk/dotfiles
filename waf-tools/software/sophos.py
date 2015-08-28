# -*- coding: utf-8 -*-
"""Detect and configure Sophos Anti-Virus."""

from pathlib import Path

def configure(ctx):
    if ctx.env.MACOSX:
        path = Path('/Applications/Sophos Anti-Virus.app')
        # XXX: Hard-coded path. Use application ID used by 'open' instead.
        ctx.env.SOPHOS = str(path) if path.is_dir() else False
        ctx.msg('Checking for Sophos Anti-Virus', ctx.env.SOPHOS)
    else:
        ctx.env.SOPHOS = False

def build(ctx):
    if not ctx.env.SOPHOS:
        return
    ctx.install_script(ctx.path.find_resource(['scripts', 'sophos-reboot']))
    ctx.env.SHELL_ALIASES['sr'] = 'sophos-reboot'
