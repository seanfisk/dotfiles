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

# Prompt (copy of zsh prompt)

# Colors from: https://wiki.archlinux.org/index.php/Color_Bash_Prompt
RED='\e[0;31m'
GREEN='\e[0;32m'
YELLOW='\e[0;33m'
BOLD_GREEN='\e[1;32m'
BOLD_BLUE='\e[1;34m'
BOLD_WHITE='\e[1;37m'
RESET='\e[0m'
GIT_PROMPT=''
# This git prompt is based on the zsh one, but attempts to use simplified logic. It might not be semantically identical in every way.
# Branch based on: http://stackoverflow.com/a/12142066
git_prompt_info() {
	local git_prompt
	# We must declare the variable local first rather than declaring and assigning together; otherwise, the "exit code" of the local command will be put into $?, which is not what we want.
	local git_branch
	git_branch=$(command git symbolic-ref --short HEAD 2>/dev/null)
	if [[ $? -eq 0 ]]; then
		# Dirty based on: http://stackoverflow.com/a/2659808
		local git_dirty
		if ! command git diff-index --quiet HEAD; then
			git_dirty='*'
		else
			git_dirty=''
		fi
		git_prompt="‹${git_branch}${git_dirty}› "
	else
		git_prompt=''
	fi
	echo "$git_prompt"
}

# Note the quoting: we want to run the git, pyenv, and rbenv commands each time, not just once.
PS1="${BOLD_GREEN}\u@\h ${BOLD_BLUE}\w ${YELLOW}"
if executable_in_path git; then
	PS1=${PS1}'$(git_prompt_info)'
fi
if function_or_executable_exists pyenv; then
	PS1=${PS1}${GREEN}'‹$(pyenv version-name)› '
fi
if function_or_executable_exists rbenv; then
	PS1=${PS1}${RED}'‹$(rbenv version-name)›'
fi

PS1=${PS1}"
${BOLD_WHITE}\$ ${RESET}"

unset RED
unset GREEN
unset YELLOW
unset BOLD_GREEN
unset BOLD_BLUE
unset BOLD_WHITE
unset RESET
