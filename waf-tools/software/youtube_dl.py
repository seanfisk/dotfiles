# -*- coding: utf-8 -*-
"""Detect and configure youtube-dl."""

def configure(ctx):
    ctx.find_program('youtube-dl', var='YOUTUBE_DL', mandatory=False)
