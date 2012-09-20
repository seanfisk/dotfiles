#!/usr/bin/env bash

# set the path, remove duplicates

export PATH=~/bin:~/.local/bin:/usr/local/sbin:/usr/local/bin:$PATH
source ~/.bash.d/path_utils.bash
path_remove_duplicates

# manpath
export MANPATH=~/.local/man:$MANPATH
path_remove_duplicates MANPATH

# Set umask for more privacy
umask u=rwx,g=,o=

# exit if non-interactive
[[ $- != *i* ]] && return

# loads RVM into a shell session
[[ -s ~/.rvm/scripts/rvm ]] && source ~/.rvm/scripts/rvm

# loads pythonz into a shell session
[[ -s ~/.pythonz/etc/bashrc ]] && source ~/.pythonz/etc/bashrc
# load virtualenvwrapper (python) into a shell session
# don't use the lazy functions, otherwise we won't get completion on
# the environments initially
if executable_in_path virtualenvwrapper.sh; then
	source virtualenvwrapper.sh
fi

# set the editor
export EDITOR='emacsclient --alternate-editor='

# working directory
export WDHOME=~/.wd
source $WDHOME/wdaliases.sh

# platform-specific code - must come before aliases
# platform-specific
kernel_name=$(uname -s)
case $kernel_name in
	Linux)
		source ~/.bash.d/platform_specific/gnu_linux.bash
		;;
	Darwin)
		source ~/.bash.d/platform_specific/mac_os_x.bash
		;;
	*)
		echo 'Kernel not recognized. Please revise the shell configuration.' >&2
		;;
esac

# source aliases - we want this to error if not found
source ~/.bash.d/aliases.bash

# local content - useful for stuff only on one machine
[[ -s ~/.bash.d/local.bash ]] && source ~/.bash.d/local.bash
