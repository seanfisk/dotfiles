# -*- coding: utf-8 -*-
"""Detect and configure Blue Medora-related software."""

from os.path import join
from shlex import quote as shquote

ARCHITECT_ALIASES = dict(
    eu='exuno',
    vr='vrops',
)

def configure(ctx):
    locs = ctx.osx_app_locations('SelectStarter')
    ctx.env.SELECTSTARTER = locs[0] if locs else False
    ctx.msg('Checking for SelectStarter', ctx.env.SELECTSTARTER)
    for exe in ARCHITECT_ALIASES.values():
        ctx.find_program(exe)

def build(ctx):
    if ctx.env.SELECTSTARTER:
        ctx.env.SHELL_ALIASES['ss'] = shquote(join(
            ctx.env.SELECTSTARTER, 'Contents', 'MacOS', 'SelectStarter'))
    for alias, exe in ARCHITECT_ALIASES.items():
        cmd = ctx.env[exe.upper()]
        if cmd:
            ctx.env.SHELL_ALIASES[alias] = ctx.shquote_cmd(cmd)
