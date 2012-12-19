# GNU/Linux specific code
# Try to keep it generic between different distros

# colorize, human readable file sizes, classify
alias ls='ls --color=always -hF'

# use xclip if we have it
if executable_in_path xclip; then
	alias copy='xclip -sel c'
	alias paste='xclip -sel c -o'
fi

# open shortcut, ala Mac OS X
if executable_in_path gnome-open; then
	alias open='gnome-open'
fi

# really useful
alias realpath='readlink --canonicalize-missing'

# multi-processor stuff
num-procs()
{
	grep --extended-regexp 'processor[[:space:]]+: [[:digit:]]+' /proc/cpuinfo | wc --lines
}
