# -*- coding: utf-8 -*-
"""Detect and configure logrotate."""

# We added logrotate due to Powerline's growing log. Another choice was
# newsyslogd, which is built into OS X (see http://serverfault.com/a/644768).
# However, this requires modifying a config file owned by root, and
# [presumably] operates as root. logrotate can be run as a user-level daemon
# through launchd, which is preferable.

from os.path import join
from collections import OrderedDict

import appdirs

def configure(ctx):
    # logrotate configuration is only supported with launchd on OS X
    if not ctx.env.MACOSX:
        return

    # All nodes to concatenate and add to the config.
    ctx.env.LOGROTATE_NODES = []

    ctx.env.LOGROTATE_CONF_PATH = join(
        appdirs.user_config_dir('logrotate'), 'config')

    ctx.find_program('logrotate', mandatory=False)

def build(ctx):
    if not (ctx.env.LOGROTATE and ctx.env.LOGROTATE_NODES):
        return

    conf_node = ctx.path.find_or_declare('logrotate.conf')
    @ctx.rule(target=conf_node, source=ctx.env.LOGROTATE_NODES)
    def _concat(tsk):
        with open(tsk.outputs[0].abspath(), 'w') as output_file:
            for input_node in tsk.inputs:
                print(file=output_file)
                with open(input_node.abspath()) as input_file:
                    for line in input_file:
                        output_file.write(line)

    ctx.install_as(ctx.env.LOGROTATE_CONF_PATH, conf_node)

    # I made up this domain; that's not a real domain.
    label = 'net.logrotate'
    plist_node = ctx.path.find_or_declare(label + '.plist')
    @ctx.rule(target=plist_node, vars=['LOGROTATE', 'LOGROTATE_CONF_PATH'])
    def _make_launch_agent(tsk):
        # Based on the plist provided with Homebrew's logrotate; see
        # 'brew info logrotate'.
        ctx.plist_dump_node(
            OrderedDict([
                ('Label', label),
                ('ProgramArguments',
                 ctx.env.LOGROTATE + [ctx.env.LOGROTATE_CONF_PATH]),
                # Run daily at midnight (or whenver the comp comes online;
                # launchd will account for this).
                ('StartCalendarInterval', {'Hour': 0}),
            ]),
            tsk.outputs[0],
        )

    ctx.install_launch_agent(plist_node)
