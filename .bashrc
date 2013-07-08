# Include common sh-like code.
source ~/.bash.d/sh_common_rc.bash

# Bash-specific stuff

# A simple prompt, useful for recording shell sessions.
alias prompt-simple="PS1='\h:\w\$ '"

alias reload-shell-config='source ~/.bashrc'

## Key bindings for paging and lolcat-ing. See here:
## <http://serverfault.com/questions/31845/is-there-a-way-to-configure-bash-to-always-page-output/31870#31870>
## We could use `|&' to pipe stdout AND stderr. We use `2>&1 |` for Bash 3 compatibility.
bind '"\C-j": " 2>&1 | less\C-m"'
if executable_in_path lolcat; then
	bind '"\C-xl": " 2>&1 | lolcat\C-m"'
	bind '"\C-x\C-l": " 2>&1 | lolcat --force 2>&1 | less -R\C-m"'
	bind '"\C-xa": " 2>&1 | lolcat --animate\C-m"'
fi
