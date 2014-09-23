# Basic aliases

alias c='cd'
alias u='cd ..' # thanks Karlin
alias less='less -R'
alias godmode='sudo -i'
alias bash-basic='env -i bash --login --noprofile --norc'
alias mkdate='date +%Y-%m-%d'

alias l='ls -l' # list
alias ll='ls -l' # list
alias la='ls -al' # show hidden, list

alias lg='ls | grep'
alias leg='ls | egrep'
alias lfg='ls | fgrep'

alias lag='la | grep'
alias laeg='la | egrep'
alias lafg='la | fgrep'

alias ipy=ipython

# Shortcut functions

cdl() { cd "$1" && ls; }
mk() { mkdir -p "$1" && cd "$1"; }
old() { mv "$1" "$1.old"; } # make a *.old file
unold() { mv "$1" "${1%.old}"; }
