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
#
# For Homebrew installs
if executable_in_path brew; then
	AUTOJUMP_BREW_PATH="$(brew --prefix)/etc/autojump.sh"
	if [[ -s $AUTOJUMP_BREW_PATH ]]; then
		source "$AUTOJUMP_BREW_PATH"
	fi
	unset AUTOJUMP_BREW_PATH
fi
# Normal installs
if ! function_or_executable_exists j; then
	[[ -s ~/.autojump/etc/profile.d/autojump.sh ]] && source ~/.autojump/etc/profile.d/autojump.sh
fi

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

# Common bash/zsh keybindings data structure.
# See here: <http://serverfault.com/questions/31845/is-there-a-way-to-configure-bash-to-always-page-output/31870#31870>

# There is apparently no way portable between Bash and Zsh to declare subscripts to an associative array which have backslashes. Zsh interprets the subscript as if it was between double quotes (with some other funky rules), and Bash follows regular quoting rules (I think). The workaround is to use the intermediate `key' variable to get consistent quoting.

declare -A keybindings # delcare as associative array

# Paging
# Note: `|&' is Bash 4 and Zsh only.
key='\C-j'; keybindings[$key]=' |& less\C-m'

# Executing last command.
# This is equivalent to pressing C-p or the up arrow, then Enter.
key='\C-xp'; keybindings[$key]='\C-p\C-m'

# Lolcat-ing.
if executable_in_path lolcat; then
	key='\C-xl'; keybindings[$key]=' |& lolcat\C-m'
	key='\C-x\C-l'; keybindings[$key]=' |& lolcat --force |& less -R\C-m'
	key='\C-xa'; keybindings[$key]=' |& lolcat --animate\C-m'
fi

# local runtime configuration - useful for stuff only on one machine
[[ -s ~/.shell_common.d/localrc.bash ]] && source ~/.shell_common.d/localrc.bash
