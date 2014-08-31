# Version check
MIN_BASH_VERSION=4
if [[ ${BASH_VERSINFO[0]} -lt $MIN_BASH_VERSION ]]; then
	echo >&2 "This configuration is compatible only with GNU Bash version $MIN_BASH_VERSION and upwards. Please update your Bash version."
	return
fi
unset MIN_BASH_VERSION

# A simple prompt, useful for recording shell sessions.
alias prompt-simple="PS1='\h:\w\$ '"

alias rl='source ~/.bashrc'
