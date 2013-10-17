# Path munging
source ~/.bash.d/path_utils.bash
# Start with default manpath entries and existing value of variable.
MANPATH=$MANPATH:$(man --path)

# Add hierarchies. It is helpful to add /usr so that INFOPATH gets
# correctly populated.
path_add_hierarchy /usr
path_add_hierarchy /usr/local
path_add_hierarchy ~/.local
# pip install --user XXX installs to here on Mac OS 10.8
path_add_hierarchy ~/Library/Python/2.7

# Add scripts directory.
PATH=~/bin:$PATH

# See this post for some more info (haha):
# <http://unix.stackexchange.com/questions/22329/gnu-texinfo-directory-search-method>
INFOPATH=/usr/local/share/info/emacs:$INFOPATH

# Nuke the dupes.
path_remove_duplicates PATH
path_remove_duplicates MANPATH
path_remove_duplicates INFOPATH

export PATH
export MANPATH
export INFOPATH

# Set umask for more privacy
umask u=rwx,g=,o=

# load pyenv and rbenv into shell session
for prefix in rb py; do
	tool=${prefix}env
	[[ -d ~/.$tool ]] && path_add_hierarchy ~/.$tool
	if executable_in_path $tool; then
		eval "$($tool init -)"
	fi
done

# set the editor
export EDITOR='emacsclient --alternate-editor='

# exit if non-interactive
[[ $- != *i* ]] && return

# loads autojump into a shell session
[[ -s ~/.autojump/etc/profile.d/autojump.sh ]] && source ~/.autojump/etc/profile.d/autojump.sh

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
