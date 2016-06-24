# -*- coding: utf-8 -*-
"""Detect and configure process managment programs."""

from shlex import quote as shquote

def configure(ctx):
    ctx.env.PROCESS_PROGRAMS = []
    for prog in ['ps', 'pgrep', 'pkill', 'htop', 'lsof', 'pstree']:
        if ctx.find_program(prog, mandatory=False):
            ctx.env.PROCESS_PROGRAMS.append(prog)

def build(ctx):
    # Process programs
    #
    # All these programs support a -u argument specifying the user. For ps,
    # pgrep, and pkill it is effective user id (euid). For htop and lsof this
    # is unspecified. In most of my cases, euid and ruid will be the same
    # anyway.
    #
    # There are two different versions of pstree:
    # - http://freecode.com/projects/pstree, used on my Mac OS X
    # - http://psmisc.sourceforge.net/, used on most GNU/Linux machines
    # But they both support the -u flag!
    #
    # Note: `id -un' was used since `whoami' has been obsoleted and is not
    # POSIX.
    for prog in ctx.env.PROCESS_PROGRAMS:
        prog_path = ctx.env[prog.upper()]
        ctx.env.SHELL_ALIASES['my' + prog] = (
            shquote(prog_path[0]) + ' -u "$(id -un)"')
