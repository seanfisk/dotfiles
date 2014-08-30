TODO for Sean Fisk's Dotfiles
=============================

* Take out hash commands from prompts for Bash/Zsh.
* Rethink organization of modules/rc/profile files and directories.
* Set up a tmuxinator config which opens up emacs, dotfiles, and chef (at least).
* Consider moving pyenv/rbenv to .zshenv/.bash_profile. Add pyenv virtualenv init as well.
* Use Waf for installation of dotfiles. I have checked out some other dotfiles managers, but they don't offer the level of customization I desire. Most of them also do not support Windows. Using Waf gives us Windows support, and furthermore, allows us to build dotfiles as if they were any other piece of software. We can use templating, detect configurations at compile time, etc. It will be awesome.
* Check out [Powerline](https://github.com/Lokaltog/powerline) and [zpython](https://bitbucket.org/ZyX_I/zsh/src).
* Write a function for creating a new tmux tab and automatically naming it.
* Consider [e-sink](https://github.com/lewang/e-sink) for `e` alias.
* Fix up `executable_in_path` and `function_or_executable_exists`. They basically do the same thing, and it's not clear which is preferred.
* Put bash function "docstrings" within the function, because they can be seen when using `type -f`.
* Write a `find-tmux` function that will find a tmux session given a list of a number of machines. Test on Yellowstone/EOS.
* Write a function that will log in to the machine with the lightest load give a list of a number of machines. Test on Yellowstone/EOS.
* Remove redundancy in the version check.
* Figure out how to restart `ssh-agent` on Mac OS X when I accidentally kill it.
* Decide standard of hyphens (probably) or underscores (probably not) and stick to them for functions, aliases, commands, and file names.
* Try to get rid of eval hackery in path utils.
* Write a zsh-specific version of path_utils, since it could be a lot more efficient.
* Write a command for updating the dotfiles and emacs repos.
* Include some things from http://mths.be/dotfiles.
* Get SSH keys under control. Decide which ones need to be shared.
* Consider [fasd](https://github.com/clvv/fasd) over autojump.
