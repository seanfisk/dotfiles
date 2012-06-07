#!/bin/bash

# set the path, remove duplicates

export PATH=~/bin:~/.local/bin:/usr/local/sbin:/usr/local/bin:$PATH
source ~/.bash.d/path_utils.bash
path_remove_duplicates

# manpath
export MANPATH=~/.local/man:$MANPATH
path_remove_duplicates MANPATH

# Set umask for more privacy
umask u=rwx,g=,o=

# exit if non-interactive
[[ $- != *i* ]] && return

# loads RVM into a shell session
[[ -s ~/.rvm/scripts/rvm ]] && source ~/.rvm/scripts/rvm

# loads PythonBrew into a shell session
[[ -s ~/.pythonbrew/etc/bashrc ]] && source ~/.pythonbrew/etc/bashrc

# set the editor
export EDITOR='emacsclient --alternate-editor='

# working directory
export WDHOME=~/.wd
source $WDHOME/wdaliases.sh

# source aliases - we want this to error if not found
source ~/.bash.d/aliases.bash