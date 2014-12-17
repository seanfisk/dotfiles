# -*- coding: utf-8 -*-
"""Detect and configure password creation aliases."""

DEFAULT_PASSWORD_LENGTH = 15

def configure(ctx):
    if ctx.env.MACOSX:
        ctx.find_program('sf-pwgen', var='SF_PWGEN', mandatory=False)
    ctx.find_program('pwgen', mandatory=False)

def build(ctx):
    if ctx.env.SF_PWGEN:
        base_cmd = ctx.env.SF_PWGEN + [
            '--length', str(DEFAULT_PASSWORD_LENGTH)]
        for kind in ['random', 'memorable']:
            ctx.env.SHELL_ALIASES['sfpw' + kind[0]] = ctx.shquote_cmd(
                # Using the long option --algorithm causes a segfault :o
                base_cmd + ['-a', kind])

    if ctx.env.PWGEN:
        suffix = [
            str(DEFAULT_PASSWORD_LENGTH),
            '1', # only generate one password
        ]
        ctx.env.SHELL_ALIASES['pwr'] = ctx.shquote_cmd(
            ctx.env.PWGEN + ['--secure'] + suffix)
        ctx.env.SHELL_ALIASES['pwm'] = ctx.shquote_cmd(ctx.env.PWGEN + suffix)
