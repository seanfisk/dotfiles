TODO for Sean Fisk's Dotfiles
=============================

* Fix up `executable_in_path` and `function_or_executable_exists`. They basically do the same thing, and it's not clear which is preferred.
* Fix scp (for EOS).
* Persistent SSH connections don't work on EOS.
* Put bash function "docstrings" within the function, because they can be seen when using `type -f`.
* Write a `find-tmux` function that will find a tmux session given a list of a number of machines. Test on Yellowstone/EOS.
* Write a function that will log in to the machine with the lightest load give a list of a number of machines. Test on Yellowstone/EOS.
* Remove redundancy in the version check.
* Figure out how to restart `ssh-agent` on Mac OS X when I accidentally kill it.
* Decide standard of hyphens (probably) or underscores (probably not) and stick to them for functions, aliases, commands, and file names.
* Set up a tmuxinator config which opens up emacs config and dotfiles repos.
* Try to get rid of eval hackery in path utils.
* Write a zsh-specific version of path_utils, since it could be a lot more efficient.
* Write a command for updating the dotfiles and emacs repos.
* Write a function for creating a new tmux tab and automatically naming it.

* SSH
    * Get SSH keys under control. Decide which ones need to be shared.
