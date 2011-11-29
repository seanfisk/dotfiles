#!/bin/bash
# set the path, remove duplicates
export PATH="$HOME/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:$PATH"
source ~/.bash.d/path_utils.bash
path_remove_duplicates

# set the editor
export EDITOR='emacsclient --alternate-editor='

# loads RVM into a shell session
[[ -s "$HOME/.rvm/scripts/rvm" ]] && source "$HOME/.rvm/scripts/rvm"

# loads PythonBrew into a shell session
[[ -s "$HOME/.pythonbrew/etc/bashrc" ]] && source "$HOME/.pythonbrew/etc/bashrc"

# working directory
export WDHOME=$HOME/.wd
source $WDHOME/wdaliases.sh

# source aliases - we want this to error if not found
source ~/.bash.d/.bash_aliases

# Set umask for more privacy
umask u=rwx,g=,o=
