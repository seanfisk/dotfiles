# Version check

MIN_ZSH_VERSION=5
if [[ $ZSH_VERSION[0,1] -lt $MIN_ZSH_VERSION ]]; then
	echo 2>&1 "This configuration is compatible only with Zsh version $MIN_ZSH_VERSION and upwards. Please update your Zsh version."
	return
fi

# Although bash does, zsh does not set the $SHELL variable when
# started. rbenv uses this variable to determine which shell
# completion to load. Set it manually for zsh.
SHELL=$(which zsh)

# Include runtime configuration.
source ~/.shell_common.d/rc.bash

# Exit if non-interactive. Has to be here again because return only returns from one file.
# [[ $- != *i* ]] && return

# Path to your oh-my-zsh configuration.
export ZSH=~/.oh-my-zsh

# Set name of the theme to load.
# Look in ~/.oh-my-zsh/themes/
# Optionally, if you set this to "random", it'll load a random theme each
# time that oh-my-zsh is loaded.
export ZSH_THEME=bira-simple

# Set to this to use case-sensitive completion
export CASE_SENSITIVE="true"

# Comment this out to disable weekly auto-update checks
export DISABLE_AUTO_UPDATE="true"

# Uncomment following line if you want to disable colors in ls
# This is covered in the bashrc
export DISABLE_LS_COLORS="true"

# Uncomment following line if you want to disable autosetting terminal title.
export DISABLE_AUTO_TITLE="true"

# Which plugins would you like to load? (plugins can be found in ~/.oh-my-zsh/plugins/*)
# Example format: plugins=(rails git textmate ruby lighthouse)

# Oh My ZSH configuration
# in general, avoid aliases and go for more completions
#
# Although I use pip a lot, the pip plugin has one annoyance: it
# prevents completion of `requirements.txt' or `requirements-dev.txt'
# when using the `-r' flag. Disable it until that is fixed.
plugins=(brew gem git-flow svn vagrant)

# source Oh My ZSH
source $ZSH/oh-my-zsh.sh

# ZSH-specific stuff

alias rl='source ~/.zshrc'

## Set ZSH options
setopt INTERACTIVE_COMMENTS

#           Fetch keys of the assoc array
#             V
for key in ${(k)keybindings}; do
	bindkey -s $key ${keybindings[$key]}
done
