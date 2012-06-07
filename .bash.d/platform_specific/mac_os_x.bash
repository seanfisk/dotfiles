#!/usr/bin/env bash

# Mac OS X specific code

# show ls colors
export CLICOLOR=1
# force show ls colors, even when not going to terminal (for example, piping to less)
export CLICOLOR_FORCE=1
# human readable file sizes, classify, and color
alias ls='ls -hFG'

# open Xcode project
alias openx='env -i open *.xcodeproj'

# pbcopy/paste
alias copy='pbcopy'
alias paste='pbpaste'

# multi-processor stuff
num-procs()
{
	system_profiler SPHardwareDataType | grep --extended-regexp 'Total Number Of Cores: [[:digit:]]+' | awk '/Total Number Of Cores/ {print $5};'
}