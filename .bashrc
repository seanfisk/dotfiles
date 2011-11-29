#!/bin/bash
# set the path, remove duplicates
export PATH="~/bin:~/.local/bin:/usr/local/sbin:/usr/local/bin:$PATH"
source ~/.bash.d/path_utils.bash
path_remove_duplicates

# set the editor
export EDITOR='emacsclient --alternate-editor='

# loads RVM into a shell session
[[ -s ~/.rvm/scripts/rvm ]] && source ~/.rvm/scripts/rvm

# loads PythonBrew into a shell session
[[ -s ~/.pythonbrew/etc/bashrc ]] && source ~/.pythonbrew/etc/bashrc

# working directory
export WDHOME=~/.wd
source $WDHOME/wdaliases.sh

# source aliases - we want this to error if not found
source ~/.bash.d/.bash_aliases

# Set umask for more privacy
umask u=rwx,g=,o=
