# Version check

MIN_ZSH_VERSION=5
if [[ $ZSH_VERSION[0,1] -lt $MIN_ZSH_VERSION ]]; then
	echo 2>&1 "This configuration is compatible only with Zsh version $MIN_ZSH_VERSION and upwards. Please update your Zsh version."
	return
fi

# For whatever reason, zsh does not set the $SHELL variable. rbenv
# uses this variable to determine which shell completion to load. Set
# it manually for zsh.
SHELL=$(which zsh)

# Include common sh-like code.
source ~/.bash.d/sh_common_rc.bash

# Path to your oh-my-zsh configuration.
export ZSH=~/.oh-my-zsh

# Set name of the theme to load.
# Look in ~/.oh-my-zsh/themes/
# Optionally, if you set this to "random", it'll load a random theme each
# time that oh-my-zsh is loaded.
#export ZSH_THEME=robbyrussell
export ZSH_THEME=bira-simple
#export ZSH_THEME=fletcherm
#export ZSH_THEME=kphoen

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
plugins=(brew gem git-flow pip svn vagrant)

# source Oh My ZSH
source $ZSH/oh-my-zsh.sh

# ZSH-specific stuff

alias reload-shell-config='source ~/.zshrc'

## Key bindings for paging and lolcat-ing. See here:
## <http://serverfault.com/questions/31845/is-there-a-way-to-configure-bash-to-always-page-output/31870#31870>
## We use `|&' to pipe stdout AND stderr.
bindkey -s '\C-j' ' |& less\C-m'
if executable_in_path lolcat; then
	bindkey -s '\C-xl' ' |& lolcat\C-m'
	bindkey -s '\C-x\C-l' ' |& lolcat --force |& less -R\C-m'
	bindkey -s '\C-xa' ' |& lolcat --animate\C-m'
fi
