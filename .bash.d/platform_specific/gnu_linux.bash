# GNU/Linux specific code
# Try to keep it generic between different distros

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
SSH_ENV_FILE=~/.ssh/ssh_agent_environment

# Made this a function so I can call it directly from the shell.
ssh-agent-bootstrap() {
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
	local should_start_ssh_agent=true
	if [[ -f $SSH_ENV_FILE ]]; then
		# Don't allow the agent PID to be printed here because it might be
		# invalid. We won't find that out until the if statement below.
		source "$SSH_ENV_FILE" > /dev/null

		# Check to see if the ssh-agent UNIX domain socket still
		# exists. Keep in mind: if ssh-agent receives SIGINT, it will
		# delete the socket. Just try not to SIGKILL it because it will
		# then not be able to cleanup the socket.
		#
		# Also check to see if ssh-agent is still running.
		#
		# - `-p' checks for a specific PID
		# - `-o comm=' prints the command only (not the args). This could be
		#   a full path, so check for "ssh-agent" at the end. The equals
		#   sign with nothing else disables printing of the header.
		#
		# If both these conditions succeed, ssh-agent is up and running
		# and we should connect to it. Otherwise, boot it up.
		if [[ -S "$SSH_AUTH_SOCK" && "$(ps -p $SSH_AGENT_PID -o comm=)" == *ssh-agent ]]; then
			should_start_ssh_agent=false
			echo 'Connected to existing ssh-agent.'
			# Now that we know the agent PID is valid, echo it.
			source <(tail -n 1 "$SSH_ENV_FILE")
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
