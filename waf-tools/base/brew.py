# -*- coding: utf-8 -*-
"""Detect and configure Homebrew/Linuxbrew."""

import keyring

GITHUB_USERNAME = 'seanfisk'

def configure(ctx):
    ctx.find_program('brew', mandatory=False)
    # Set Homebrew API token; see here:
    # https://gist.github.com/christopheranderton/8644743
    token = keyring.get_password('Homebrew API Token', GITHUB_USERNAME)
    ctx.msg("Checking for Homebrew API token for '{}'".format(GITHUB_USERNAME),
            token is not None)
    if token:
        ctx.env.HOMEBREW_API_TOKEN = token

def build(ctx):
    if ctx.env.HOMEBREW_API_TOKEN:
        ctx.env.SHELL_ENV['HOMEBREW_API_TOKEN'] = ctx.env.HOMEBREW_API_TOKEN
