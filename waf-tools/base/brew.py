# -*- coding: utf-8 -*-
"""Detect and configure Homebrew/Linuxbrew."""

GITHUB_USERNAME = 'seanfisk'

def configure(ctx):
    ctx.find_program('brew', mandatory=False)
    # Set Homebrew API token; see here:
    # https://gist.github.com/christopheranderton/8644743
    token = ctx.safe_get_password('Homebrew API Token', GITHUB_USERNAME)
    ctx.msg("Checking for Homebrew API token for '{}'".format(GITHUB_USERNAME),
            token is not None)
    if token:
        ctx.env.HOMEBREW_API_TOKEN = token
    if ctx.env.BREW:
        for cmd in ['command-not-found-init', 'cask']:
            has_cmd = ctx.exec_command(ctx.env.BREW + ['command', cmd]) == 0
            var_name = 'BREW_' + cmd.replace('-', '_').upper()
            ctx.env[var_name] = (
                ctx.env.BREW + [cmd] if has_cmd else False)
            ctx.msg("Checking for brew-{}".format(cmd), has_cmd)

def _make_cmd_not_found(tsk):
    out_node = tsk.outputs[0]
    shell = out_node.suffix()[1:]
    return tsk.generator.bld.feed_to_shell(
        shell, tsk.env.BREW_COMMAND_NOT_FOUND_INIT, out_node)

def build(ctx):
    if ctx.env.HOMEBREW_API_TOKEN:
        ctx.env.SHELL_ENV['HOMEBREW_API_TOKEN'] = ctx.env.HOMEBREW_API_TOKEN
    if ctx.env.BREW_COMMAND_NOT_FOUND_INIT:
        for shell in ctx.env.AVAILABLE_SHELLS:
            out_node = ctx.path.find_or_declare(
                'brew-command-not-found.' + shell)
            ctx.add_shell_rc_node(out_node, shell)
            ctx(rule=_make_cmd_not_found, target=out_node,
                vars=[shell.upper(), 'BREW_COMMAND_NOT_FOUND_INIT'])
    if ctx.env.BREW_CASK:
        ctx.install_script(ctx.path.find_resource([
            'scripts', 'brew-cask-migrate']))
