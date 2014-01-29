# Version check

MIN_BASH_VERSION=4
if [[ ${BASH_VERSION:0:1} -lt $MIN_BASH_VERSION ]]; then
	echo 2>&1 "This configuration is compatible only with GNU Bash version $MIN_BASH_VERSION and upwards. Please update your Bash version."
	return
fi

# Include common sh-like code.
source ~/.shell_common.d/rc.bash

# Exit if non-interactive. Has to be here again because return only returns from one file.
# [[ $- != *i* ]] && return

# Bash-specific stuff

# A simple prompt, useful for recording shell sessions.
alias prompt-simple="PS1='\h:\w\$ '"

alias rl='source ~/.bashrc'

#           Fetch keys of the assoc array
#             V
for key in "${!keybindings[@]}"; do
	# Yay quoting! It is supposed to turn out like this:
	# "\C-j": " 2>&1 | less\C-m"
	bind "\"$key\": \"${keybindings[$key]}\""
done
