# GNU/Linux specific code
# Try to keep it generic between different distros

source ~/.shell_common.d/path_utils.bash

# colorize, human readable file sizes, classify
alias ls='ls --color=always -hF'

# use xclip if we have it
if executable_in_path xclip; then
	alias copy='xclip -sel c'
	alias paste='xclip -sel c -o'
fi

# open shortcut, ala Mac OS X
if executable_in_path gnome-open; then
	alias open='gnome-open'
fi

# really useful
alias realpath='readlink --canonicalize-missing'

# multi-processor stuff
num-procs()
{
	grep --extended-regexp 'processor[[:space:]]+: [[:digit:]]+' /proc/cpuinfo | wc --lines
}

# ssh-agent handling
# See here for lots of tips:
# <http://mah.everybody.org/docs/ssh>

# Note: this code doesn't work with Mac OS X, which doesn't actually
# start ssh-agent at startup. It uses launchd as a super-server and
# "and creates a UNIX domain socket which listens for connections,
# on behalf of ssh-agent". See this page for more information:
# <http://www.dribin.org/dave/blog/archives/2007/11/28/ssh_agent_leopard/>
#
# As such, this function is not needed on Mac OS X, since it has its
# own ssh-agent handling capabilities. It might not be needed on
# graphical GNU/Linux desktops either, but we'll wait and see.

# Boot up ssh-agent if it's not already started.
#
# Check to see if the environment variables are set. If not,
# then ssh-agent must be started.
if [[ -z "$SSH_AUTH_SOCK" || -z "$SSH_AGENT_PID" ]]; then
	# Note: trap doesn't work in a function since the function runs it
	# in a subshell (I think). So don't make this a "function to start
	# ssh-agent".

	# Start ssh-agent in this shell.
	# `-s' causes ssh-agent to output Bourne shell syntax
	echo "Starting ssh-agent. Run \`ssh-add' to unlock a key."
	source <(ssh-agent -s)
	# Since ssh-add requires a password, we must run that manually to
	# get access to the key.

	# Kill ssh-agent upon exit from *this* shell (the shell in which
	# it was started).
	trap 'source <(ssh-agent -k)' EXIT
fi
