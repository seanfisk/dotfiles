# Exit if non-interactive. There are many reasons to do this:
# - Aliases, etc. are not typically necessary for non-interactive scripts
# - Speeds up execution time for non-interactive subshells
# - We need to "keep the shell clean." See `man rsync` for more info on that.
[[ $- != *i* ]] && return
