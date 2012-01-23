#!/bin/bash
# copy / paste
# Linux xclip

# Don't use the bash or zsh built-in `which'
# Use the actual executable for shell independence
if /usr/bin/which xclip &> /dev/null; then
	alias copy='xclip -sel c'
	alias paste='xclip -sel c -o'
# Mac pbcopy/paste
elif /usr/bin/which pbcopy &> /dev/null; then
	alias copy='pbcopy'
	alias paste='pbpaste'
fi
alias dl='wget $(paste)'
alias webclip='wget -nv -O - $(paste) | copy'

# platform-specific
kernel_name=$(uname -s)
if [[ $kernel_name == Linux ]]; then
	alias ls='ls --color=always -hF' # colorize, human readable file sizes, classify
elif [[ $kernelName == Darwin ]]; then
	export CLICOLOR=1 # show ls colors
	export CLICOLOR_FORCE=1 # force show ls colors, even when not going to terminal (for example, piping to less)
	alias ls='ls -hFG' # human readable file sizes, classify, and color
	alias openx='env -i open *.xcodeproj' # open Xcode project
fi
alias l='ls -l' # list
alias ll='ls -l' # list
alias la='ls -al' # show hidden, list

alias lg='ls | grep'
alias leg='ls | egrep'
alias lfg='ls | fgrep'

alias lag='la | grep'
alias laeg='la | egrep'
alias lafg='la | fgrep'

# git aliases
alias gt='git status'
alias gobuddygo='git push'
alias cometome='git pull'

# handy aliases
alias u='cd ..'
alias changelog="$EDITOR ~/changelog.txt"
alias ssh-copy-id-clipboard='copy < ~/.ssh/id_rsa.pub'
alias realpath='readlink -f'
alias less='less -R'
if /usr/bin/which gnome-open > /dev/null; then
	alias open='gnome-open'
fi
alias godmode='sudo -i'
alias reload-shell-config='source ~/.bashrc'
alias basic-bash='env --ignore-environment bash --login --noprofile --norc'

# multi-processor stuff
num-procs()
{
	grep -E 'processor[[:space:]]+: [[:digit:]]+' /proc/cpuinfo | wc -l
}
export MAKEFLAGS="--jobs=$(num-procs)" # do this for all make's
alias parallelmake="make $MAKEFLAGS"	 # add an alias

# shortcut functions
cdl() { cd "$1" && ls; }
mk() { mkdir -p "$1" && cd "$1"; }
old() { mv "$1" "$1.old"; } # make a *.old file	
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
	find "$target_dir" -maxdepth 1 -type f -executable -exec ln --symbolic --verbose --target-directory . '{}' '+'
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
# emacs
if /usr/bin/which aquamacs &> /dev/null; then
	alias ec=aquamacs # prefer aquamacs script over emacsclient
else
	ec() { emacsclient "$@" & } # start emacsclient in the background
	 # DON'T use alternate editor because it will start emacs in the terminal,
	 # which is probably not what we want. Instead, just warn us that the server
	 # does not exist.
fi
## quick emacs
alias ecq='emacs --no-window-system --quick'
