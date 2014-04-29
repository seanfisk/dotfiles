source ~/.shell_common.d/path_utils.bash

if function_or_executable_exists copy; then
	if function_or_executable_exists paste; then
		if function_or_executable_exists aria2c; then
			# aria2c is a command-line download accelerator
			# (opens multiple connections)
			alias dl='aria2c $(paste)'
		elif function_or_executable_exists wget; then
			alias dl='wget $(paste)'
		fi
		if function_or_executable_exists wget; then
			alias webclip='wget -no-verbose -output-document=- $(paste) | copy'
		fi
		alias ssh-copy-id-clipboard='copy < ~/.ssh/id_rsa.pub'
	fi
fi

if function_or_executable_exists qpdf; then
	# For more info, see
	# <http://qpdf.sourceforge.net/files/qpdf-manual.html#ref.page-selection>.
	# The bolded command, however, is incorrect, and the `--' has to
	# come *before* the name of the output file.

	# I can never remember this...
	pdf-merge() {
		output_file=$1
		shift
		qpdf --empty --pages "$@" -- "$output_file"
	}
	# I also can never remember that qpdf calls it "merging", not "joining"
	alias pdf-join=pdf-merge
fi

# really? yes, really
alias c='cd'

alias s=ls
alias l='ls -l' # list
alias ll='ls -l' # list
alias la='ls -al' # show hidden, list

alias lg='ls | grep'
alias leg='ls | egrep'
alias lfg='ls | fgrep'

alias lag='la | grep'
alias laeg='la | egrep'
alias lafg='la | fgrep'

for program in ps pgrep pkill htop lsof pstree; do
	if executable_in_path $program; then
		# All these programs support a -u argument specifying the
		# user. For ps, pgrep, and pkill it is effective user id
		# (euid). For htop and lsof this is unspecified. In most of my
		# cases, euid and ruid will be the same anyway.
		#
		# There are two different versions of pstree:
		# - http://freecode.com/projects/pstree, used on my Mac OS X
		# - http://psmisc.sourceforge.net/, used on most GNU/Linux machines
		# But they both support the -u flag!
		#
		# `id -un' is used since `whoami' has been obsoleted and is not POSIX.
		alias "my$program=$program"' -u $(id -un)'
	fi
done

# List my tmux sockets
alias mytmux='lsof -u $(id -u) -a -U | grep "^tmux"'

# git aliases
alias gt='git status'
alias gobuddygo='git push'
alias cometome='git pull'

# handy aliases
alias u='cd ..' # thanks Karlin
alias changelog="$EDITOR ~/changelog.txt"
alias less='less -R'
alias godmode='sudo -i'
alias bash-basic='env -i bash --login --noprofile --norc'
alias mkdate='date +%Y-%m-%d'

# ack and ag aliases
if executable_in_path ack; then
	# Just 'less' is fine; we don't need to pass 'less -R' to get colors to work.
	alias ackp='ack --pager=less'
	# Note: by default `git ls-files' only shows tracked files.
	alias ackg='git ls-files | ack --files-from=-'
	alias ackpg='git ls-files | ackp --files-from=-'
fi

if executable_in_path ag; then
	# Just 'less' is fine; we don't need to pass 'less -R' to get colors to work.
	alias agp='ag --pager less'
	# ag doesn't support `--files-from'. Too bad.
fi

# count lines of code in git repository
if executable_in_path ohcount; then
	git-count-lines() {
		local filenames=()
		git ls-files -z | while read -r -d$'\0' filename; do
			filenames+=("$filename")
		done
		echo "${filenames[@]}"
		ohcount "${filenames[@]}"
	}
fi

if type num-procs &> /dev/null; then
	# Don't export this by default. Use the alias to make in parallel explicitly.
	MAKEFLAGS="--jobs=$(num-procs)"
	alias make-parallel="make $MAKEFLAGS"	 # add an alias
fi

# shortcut functions
cdl() { cd "$1" && ls; }
mk() { mkdir -p "$1" && cd "$1"; }
old() { mv "$1" "$1.old"; } # make a *.old file
unold() { mv "$1" "${1%.old}"; }

# Data URIs
to_data_uri() {
	# Filter; accepts input on stdin and echoes to stdout
  echo "data:text/html;base64,$(base64 < /dev/stdin | tr -d '\r\n')"
}
# Code highlighting
if function_or_executable_exists pygmentize; then

	alias pygmentize_to_html='pygmentize -P full=True -P nobackground=True -f html'
	pygmentize_to_data_uri_html() {
		# All extra options get sent to pygmentize.
		#
		# Accepts input on stdin or as a file name.
		pygmentize_to_html "$@" < /dev/stdin | to_data_uri
	}

	if function_or_executable_exists copy; then
		hilite() {
			# Synatx highlight code and send to the clipboard
			pygmentize_to_data_uri_html "$@" < /dev/stdin | copy
		}
	fi

	if function_or_executable_exists llc; then
		llvm_api_for_cpp() {
			if [[ $# -ne 1 ]]; then
				echo >&2 "Usage: $0 SOURCE_FILE"
				return
			fi
			# Inspired by the LLVM demo (disabled) and <http://ellcc.org/demo/index.cgi>
			# Some command-lines used from <http://ellcc.org/viewvc/svn/ellcc/trunk/www.ellcc/demo/index.cgi?view=markup>
			clang++ -S -emit-llvm -Wall -c "$1" -o - | llc -march=cpp | pygmentize -l cpp | command less -R
		}
	fi
fi

# Emacs
# Start emacsclient
e() {
	if [[ $# -ne 0 ]]; then
		# Normal usage
		emacsclient --no-wait "$@"
	else
		# Allow output to be piped to an Emacs buffer.
		# See the EmacsWiki:
		# <http://www.emacswiki.org/emacs/EmacsClient#toc44>

		# Passing a literal /tmp in here is probably not the best idea, but I've never seen /tmp not exist on a box. The reason we do it is because mktemp options drastically differ from GNU to BSD (as usual, the GNU options are better).
		local stdin_tmp_file=$(mktemp /tmp/emacs-stdin-XXXXXXXXXX)
		local stdin_tmp_file_base=$(basename "$stdin_tmp_file")
		cat > "$stdin_tmp_file"
		# create-file-buffer normally appends <1>, <2>, etc. if the buffer already exists. That would be appropriate, but when using uniquify, it appends directory names. That isn't useful, and is extremely confusing when it chooses the name of the directory that `e' was *run in*. Just name the buffer according to the temp file that has been created, since we hope that will be somewhat unique.
		emacsclient --eval "(let ((b (create-file-buffer \"*$stdin_tmp_file_base*\"))) (switch-to-buffer b) (insert-file-contents \"$stdin_tmp_file\") (delete-file \"$stdin_tmp_file\"))" &> /dev/null
	fi
}
# DON'T use alternate editor because it will start emacs in the
# terminal, which is probably not what we want. Instead, just warn us
# that the server does not exist.
## Quick Emacs
alias ecq='emacs --no-window-system --quick'

# tmux update environment
# adapted from here: <http://raim.codingfarm.de/blog/2013/01/30/tmux-update-environment/>

if [[ -n "$TMUX" ]]; then
	# The TMUX environment variable will be set if we are in tmux. Otherwise this function is useless.
	re() {
		# Refresh the local environment with values from tmux
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
tmux_attach_or_new() {
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
ssh_tmux() {
	# All args are passed to `ssh' *before* the remote command. This allows us to easily specify, e.g., `-X'.

	# Note: This function is primarily intended for the EOS labs.
	# - By using -c, we are telling bash that it should not be invoked as a non-interactive login shell. However, if it's not a login shell, it won't read our .bash_profile, which includes setting the PATH to find tmux (on EOS). And if it's not interactive, it won't get far enough to read our functions and aliases (of which tmux_attach_or_new is one). Therefore we need to add `--login -i' to the command-line.
	# - See above for what `tmux_attach_or_new' does.
	# - We use exec so that the SSH session replaces our current shell. This is done because I typically open up a new window for SSH sessions and just use that window for tmux on the remote machine. I don't typically use the terminal emulator's tab feature at all (because we have tmux).
	# - By calling `tmux_attach_or_new' on the *remote* server we are assuming that the dotfiles (and tmux) are installed on the remote server. Errors will ensue if these assumptions are not correct.
	exec ssh -t "$@" 'bash --login -i -c tmux_attach_or_new'
}

# Find size of files in a git repo
git-repo-size() {
	# See here for sources of approaches: http://serverfault.com/questions/351598/get-total-files-size-from-a-file-containing-a-file-list

	if executable_in_path gwc; then
		local WC=gwc
	else
		local WC=wc
	fi
	local num_bytes=$(git ls-files -z | $WC --bytes --files0-from=- | tail -1 | cut -d' ' -f1)

	# Another approach:
	# if executable_in_path gstat; then
	# 	local STAT=gstat
	# else
	# 	local STAT=stat
	# fi
	# local num_bytes=$(git ls-files -z | while read -d $'\0' filename;  do $STAT -c '%s' "$filename"; done | awk '{total+=$1} END {print total}')

	if executable_in_path gnumfmt; then
		local NUMFMT=gnumfmt
	else
		local NUMFMT=numfmt
	fi
	$NUMFMT --to=iec-i --suffix=B "$num_bytes"
}
