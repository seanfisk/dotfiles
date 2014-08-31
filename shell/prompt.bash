# -*- coding: utf-8; -*-
# Prompt (copy of bira-simple Oh My Zsh prompt)

# Colors from: https://wiki.archlinux.org/index.php/Color_Bash_Prompt
RED='\e[0;31m'
GREEN='\e[0;32m'
YELLOW='\e[0;33m'
BOLD_GREEN='\e[1;32m'
BOLD_BLUE='\e[1;34m'
BOLD_WHITE='\e[1;37m'
RESET='\e[0m'
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
if hash git &>/dev/null; then
	PS1=${PS1}'$(git_prompt_info)'
fi
if hash pyenv &>/dev/null; then
	PS1=${PS1}${GREEN}'‹$(pyenv version-name)› '
fi
if hash rbenv &>/dev/null; then
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
