# Include common sh-like code.
source ~/.bash.d/sh_common_rc.bash

# Bash-specific stuff

alias reload-shell-config='source ~/.bashrc'

## Key bindings for paging and lolcat-ing. See here:
## <http://serverfault.com/questions/31845/is-there-a-way-to-configure-bash-to-always-page-output/31870#31870>
## We use `|&' to pipe stdout AND stderr.
bind '"\C-j": " |& less\C-m"'
if executable_in_path lolcat; then
	bind '"\C-i": " |& lolcat\C-m"'
	# C-o doesn't seem to work in bash, so no animation for now.
	#bind '"\C-o": " | lolcat --animate\C-m"'
	bind '"\C-v": " |& lolcat --force | less -R\C-m"'
fi
