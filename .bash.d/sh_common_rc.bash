# Path munging
source ~/.bash.d/path_utils.bash
# Start with default manpath entries and existing value of variable.
MANPATH=$MANPATH:$(man --path)
# Add extra hierarchies.
add_hierarchy_to_path /usr/local
add_hierarchy_to_path ~/.local
# Add scripts directory.
PATH=~/bin:$PATH

# Nuke the dupes.
path_remove_duplicates PATH
path_remove_duplicates MANPATH

export PATH
export MANPATH

# See this post for some more info (haha):
# <http://unix.stackexchange.com/questions/22329/gnu-texinfo-directory-search-method>
INFOPATH=/usr/local/share/info/emacs:$INFOPATH
path_remove_duplicates INFOPATH
export INFOPATH

# Set umask for more privacy
umask u=rwx,g=,o=

# exit if non-interactive
[[ $- != *i* ]] && return

# loads rbenv into a shell session
if executable_in_path rbenv; then
	eval "$(rbenv init -)"
fi

# loads pythonz into a shell session
[[ -s ~/.pythonz/etc/bashrc ]] && source ~/.pythonz/etc/bashrc
# load virtualenvwrapper (python) into a shell session
# don't use the lazy functions, otherwise we won't get completion on
# the environments initially
if executable_in_path virtualenvwrapper.sh; then
	source virtualenvwrapper.sh
fi

# loads autojump into a shell session
[[ -s ~/.autojump/etc/profile.d/autojump.zsh ]] && source ~/.autojump/etc/profile.d/autojump.sh

# set the editor
export EDITOR='emacsclient --alternate-editor='

# Boot up ssh-agent if it's not already started.
if [[ -z "$SSH_AUTH_SOCK" && -z "$SSH_AGENT_PID" ]]; then
	# `-s' causes ssh-agent to output Bourne shell syntax
	echo "Starting ssh-agent. Run \`ssh-add' to unlock a key."
	source <(ssh-agent -s)
	# Since ssh-add requires a password, we must run that manually to
	# get access to the key.
fi

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