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

# exit if non-interactive
[[ $- != *i* ]] && return

# loads rbenv into a shell session
[[ -d ~/.rbenv ]] && path_add_hierarchy ~/.rbenv
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
[[ -s ~/.autojump/etc/profile.d/autojump.sh ]] && source ~/.autojump/etc/profile.d/autojump.sh

# set the editor
export EDITOR='emacsclient --alternate-editor='

# ssh-agent handling
# See here for lots of tips:
# <http://mah.everybody.org/docs/ssh>
SSH_ENV_FILE=~/.ssh/ssh_agent_environment

# Made this a function so I can call it directly from the shell.
ssh-agent-bootstrap() {
	# Boot up ssh-agent if it's not already started.
	# if [[ -z "$SSH_AUTH_SOCK" && -z "$SSH_AGENT_PID" ]]; then
	should_start_ssh_agent=true
	if [[ -f $SSH_ENV_FILE ]]; then
		source "$SSH_ENV_FILE"
		# Check to see if ssh-agent is still running. If not, boot it up. If
		# so, we're done.
		#
		# - `-p' checks for a specific PID
		# - `-o comm=' prints the command only (not the args). This could be
		#   a full path, so check for "ssh-agent" at the end. The equals
		#   sign with nothing else disables printing of the header.
		if [[ "$(ps -p $SSH_AGENT_PID -o comm=)" == *ssh-agent ]]; then
			should_start_ssh_agent=false
			echo 'Connected to existing ssh-agent.'
		fi
	fi

	if $should_start_ssh_agent; then
		# trap doesn't work in a function since the function runs it in a
		# subshell (I think).

		# Start ssh-agent in this shell.
		# `-s' causes ssh-agent to output Bourne shell syntax
		echo "Starting ssh-agent. Run \`ssh-add' to unlock a key."
		ssh-agent -s > "$SSH_ENV_FILE"
		source "$SSH_ENV_FILE"
		# Since ssh-add requires a password, we must run that manually to
		# get access to the key.

		# Kill ssh-agent upon exit from *this* shell (the shell in which it was started).
		trap 'source <(ssh-agent -k)' EXIT
	fi
}

ssh-agent-bootstrap

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
