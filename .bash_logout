#!/bin/bash
if [ "$SHLVL" = 1 ]; then
	[ -x /usr/bin/clear ] && /usr/bin/clear
	[ -x /usr/bin/clear_console ] && /usr/bin/clear_console -q
fi