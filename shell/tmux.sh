# tmux update environment
# adapted from here: <http://raim.codingfarm.de/blog/2013/01/30/tmux-update-environment/>

if [[ -n "$TMUX" ]]; then
	# The TMUX environment variable will be set if we are in tmux. Otherwise this function is useless.
	re() {
		# Refresh the local environment with values from tmux.
		local line
		while read line; do
			if [[ $line == -* ]]; then
				# Remove the `-'.
				unset ${line/#-/}
			else
				# Add quotes around the argument.
				# Quoting differs from the original for zsh compatibility.
				line=${line/=/'="'}
				line=${line/%/\"}
				eval export $line
			fi
		done < <(tmux show-environment)
	}
fi

# Attach to an existing tmux session, or create one if it doesn't exist
tmux-attach-or-new() {
	# This is idempotent: if a server already exists, this does nothing.
	tmux start-server
	local tmux_subcommand
	if tmux has-session 2>/dev/null; then
		tmux_subcommand=attach
	else
		tmux_subcommand=new-session
	fi
	# When we exec, the tmux process replaces the currently running shell. Since the only purpose the "currently running shell" serves is to start tmux, we don't really need it anymore.
	# While it's not absolutely necessary to exec, if we do, then when
	# the process terminates, the terminal window/tab or SSH session
	# will exit, which is kind of cool.
	exec tmux "$tmux_subcommand"
}

# Start an SSH connection by running the shell function `tmux_attach_or_new' within bash.
ssh-tmux() {
	# All args are passed to `ssh' *before* the remote command. This allows us to easily specify, e.g., `-X'.

	# Note: This function is primarily intended for the EOS labs.
	# - By using -c, we are telling bash that it should not be invoked as a non-interactive login shell. However, if it's not a login shell, it won't read our .bash_profile, which includes setting the PATH to find tmux (on EOS). And if it's not interactive, it won't get far enough to read our functions and aliases (of which tmux_attach_or_new is one). Therefore we need to add `--login -i' to the command-line.
	# - See above for what `tmux_attach_or_new' does.
	# - We use exec so that the SSH session replaces our current shell. This is done because I typically open up a new window for SSH sessions and just use that window for tmux on the remote machine. I don't typically use the terminal emulator's tab feature at all (because we have tmux).
	# - By calling `tmux_attach_or_new' on the *remote* server we are assuming that the dotfiles (and tmux) are installed on the remote server. Errors will ensue if these assumptions are not correct.
	exec ssh -t "$@" 'bash --login -i -c tmux-attach-or-new'
}
