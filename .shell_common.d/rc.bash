# Commands to be run in .bashrc and .zshrc
#
# We would like this file to be run for all interactive shells, both login and non-login.

source ~/.shell_common.d/path_utils.bash

# exit if non-interactive
# [[ $- != *i* ]] && return

# Load pyenv and rbenv into the shell session. We need to load this here, in the rc file, because it loads up shell functions. For example, `pyenv shell' is only available when this `eval' command is run *within the shell*.
for prefix in rb py; do
	tool=${prefix}env
	if executable_in_path $tool; then
		eval "$($tool init -)"
	fi
done

# Load autojump into a shell session. This needs to be loaded in each interactive shell session because it loads functions, aliases, etc. Unfortunately, it also amends the PATH, so successive inner shells that get started will have multiple paths to autojump's bin directory in the PATH. We could call path_remove_duplicates, but we'd rather not do this in here. It's not a huge deal and it doesn't break anything, so we'll deal with it for now.
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
