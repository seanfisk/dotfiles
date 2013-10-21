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

for program in ps pgrep pkill htop lsof; do
	if executable_in_path $program; then
		# All these programs support a -u argument specifying the
		# user. For ps, pgrep, and pkill it is effective user id
		# (euid). For htop and lsof this is unspecified. In most of my
		# cases, euid and ruid will be the same anyway.
		alias "my$program=$program -u $(whoami)"
	fi
done

# List my tmux sockets
alias mytmux="lsof -u $(whoami) -a -U | grep '^tmux'"

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

# ack alias (with pager)
if executable_in_path ack; then
	alias ackp="ack --pager='less -R'"
fi

if executable_in_path ag; then
	# ag with pager
	# Without `--color', ag will omit colors when being piped to less.
	agp() {
		ag --color "$@" | less
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
		local stdin_tmp_file=$(mktemp emacs-stdin-XXXXXXXXXX)
		local stdin_tmp_file_base=$(basename "$stdin_tmp_file")
		cat > "$stdin_tmp_file"
		# create-file-buffer normally appends <1>, <2>, etc. if the buffer already exists. That would be appropriate, but when using uniquify, it appends directory names. That isn't useful, and is extremely confusing when it chooses the name of the directory that `e' was *run in*. Just name the buffer according to the temp file that has been created, since we know that will be unique.
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
