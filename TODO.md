TODO for Sean Fisk's Dotfiles
=============================

* Use [tmux update-environment](http://raim.codingfarm.de/blog/2013/01/30/tmux-update-environment/) for updating (maybe instead of the ssh-agent hack).
* Check out bind (bash) and bindkey (zsh).
    * Use a shared data structure to maintain these keybindings and not just literal values.
* Remove redundancy in the version check.
* Decide standard of hyphens (probably) or underscores (probably not) and stick to them for functions, aliases, commands, and file names.
* Set up a tmuxinator config which opens up emacs config and dotfiles repos.
* Try to get rid of eval hackery in path utils.
* Write a zsh-specific version of path_utils, since it could be a lot more efficient.
* Write a command for updating the dotfiles and emacs repos.
* Investigate other ways of install autojump.
* Figure out why MANPATH isn't getting set correctly in bash but it is in zsh.
    * Definitely has to do with `/etc/zshenv` and `/usr/libexec/path_helper`.
    * Problem mitigated by new configuration.
* Write a function for creating a new tmux tab and automatically naming it.
* Get SSH keys under control. Decide which ones need to be shared.
