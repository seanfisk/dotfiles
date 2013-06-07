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
mytmux() {
	# -U: UNIX domain sockets
	lsof -u $(whoami) -a -U | \
		grep '^tmux' | \
		grep --invert-match --fixed-strings socket | \
		tr --squeeze-repeats ' ' | \
		cut --fields 9 --delimiter ' ' | \
		sort --unique
}

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

# These are somewhat legacy. In here for documentation mostly.
find-all-executables() {
	if [[ $# -gt 1 ]]; then
		echo "Usage: $0 [DIRECTORY]" 1>&2
		return 1
	fi
	find "${1:-.}" -maxdepth 1 -type f -executable
}
link-all-exectuables() {
	if [[ $# -eq 0 || $# -gt 2 ]]; then
		echo "Usage: $0 TARGET_DIR [LINK_DIR]" 1>&2
		return 1
	fi
	local target_dir=$(readlink --canonicalize-existing "$1")
	local link_dir=$(readlink --canonicalize-existing "${2:-.}")
	pushd "$link_dir"
	find "$target_dir" -maxdepth 1 -type f -executable \
		-exec ln --symbolic --verbose --target-directory . '{}' '+'
	popd
}
unlink-all-exectuables() {
	if [[ $# -eq 0 || $# -gt 2 ]]; then
		echo "Usage: $0 TARGET_DIR [LINK_DIR]" 1>&2
		return 1
	fi
	local target_dir=$(readlink --canonicalize-existing "$1")
	local link_dir=$(readlink --canonicalize-existing "${2:-.}")
	for target in $(find-all-executables "$target_dir"); do
		local link=$link_dir/$(basename "$target")
		if [[ ! -L "$link" ]]; then
			continue
		fi
		local target_path=$(readlink --canonicalize-existing "$target")
		local link_path=$(readlink --canonicalize-existing "$link")
		if [[ $target_path == $link_path ]]; then
			rm --verbose "$link"
		fi
	done
}

# Data URIs
to_data_uri() {
  echo "data:text/html;base64,$(base64 < /dev/stdin | tr -d '\r\n')"
}
# Code highlighting
alias pygmentize_to_html='pygmentize -P full=True -P nobackground=True -f html'
pygmentize_to_data_uri_html() {
	# All extra options get sent to pygmentize.
	#
	# Accepts input on stdin.
	pygmentize -P full=True -P nobackground=True -f html "$@" < /dev/stdin | to_data_uri
}

# Emacs
# Start emacsclient in the background
e() { emacsclient "$@" & }
# DON'T use alternate editor because it will start emacs in the
# terminal, which is probably not what we want. Instead, just warn us
# that the server does not exist.
## Quick Emacs
alias ecq='emacs --no-window-system --quick'
