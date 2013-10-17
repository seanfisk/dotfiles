# Version check

MIN_BASH_VERSION=4
if [[ ${BASH_VERSION:0:1} -lt $MIN_BASH_VERSION ]]; then
	echo 2>&1 "This configuration is compatible only with GNU Bash version $MIN_BASH_VERSION and upwards. Please update your Bash version."
	return
fi

# Include common sh-like code.
source ~/.bash.d/sh_common_rc.bash

# Exit if non-interactive. Has to be here again because return only returns from one file.
[[ $- != *i* ]] && return

# Bash-specific stuff

# A simple prompt, useful for recording shell sessions.
alias prompt-simple="PS1='\h:\w\$ '"

alias rl='source ~/.bashrc'

## Key bindings for paging and lolcat-ing. See here:
## <http://serverfault.com/questions/31845/is-there-a-way-to-configure-bash-to-always-page-output/31870#31870>
## We could use `|&' to pipe stdout AND stderr. We use `2>&1 |` for Bash 3 compatibility.
bind '"\C-j": " 2>&1 | less\C-m"'
if executable_in_path lolcat; then
	bind '"\C-xl": " 2>&1 | lolcat\C-m"'
	bind '"\C-x\C-l": " 2>&1 | lolcat --force 2>&1 | less -R\C-m"'
	bind '"\C-xa": " 2>&1 | lolcat --animate\C-m"'
fi

# Key binding for executing last command.
#
# This is equivalent to pressing C-p or the up arrow, then Enter.
bind '"\C-xp": "\C-p\C-m"'
