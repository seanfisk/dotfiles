# Commands to be run in .bashrc and .zshrc
#
# We would like this file to be run for all interactive shells, both login and non-login.

# exit if non-interactive
# [[ $- != *i* ]] && return

# loads autojump into a shell session
[[ -s ~/.autojump/etc/profile.d/autojump.sh ]] && source ~/.autojump/etc/profile.d/autojump.sh

# platform-specific aliases and functions - must come before aliases.bash
kernel_name=$(uname -s)
case $kernel_name in
	Linux)
		source ~/.shell_common.d/platform_specific/gnu_linux.bash
		;;
	Darwin)
		source ~/.shell_common.d/platform_specific/mac_os_x.bash
		;;
	*)
		echo 'Kernel not recognized. Please revise the shell configuration.' >&2
		;;
esac

# source aliases - we want this to error if not found
source ~/.shell_common.d/aliases.bash

# local runtime configuration - useful for stuff only on one machine
[[ -s ~/.shell_common.d/localrc.bash ]] && source ~/.shell_common.d/localrc.bash
