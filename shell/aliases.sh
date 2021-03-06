# Basic aliases

alias c='cd'
alias u='cd ..' # thanks Karlin
alias less='less -R'
alias godmode='sudo -i'
alias mkdate='date +%Y-%m-%d'

alias py=python
alias ipy=ipython
# This overrides the w command. However, I use that so little I think it's a
# worth compromise.
alias w=./waf
alias gr=./gradlew

# Shortcut functions

cdl() { cd "$1" && ls; }
mk() { mkdir -p "$1" && cd "$1"; }
old() { mv "$1" "$1.old"; } # make a *.old file
unold() { mv "$1" "${1%.old}"; }
spwd() {
	# http://stackoverflow.com/a/10037257/879885
	if [[ "$PWD" =~ ^"$HOME"(/|$) ]]; then
		out="~${PWD#$HOME}"
	else
		out="$PWD"
	fi
	echo "$out"
}
# Capture a command and its output and send it to the clipboard
ccapture() {
	capture "$@" |& ccopy
}

# VMware
alias eu=exuno
alias vr=vrops
