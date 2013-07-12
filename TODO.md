TODO for Sean Fisk's Dotfiles
=============================

* Check out bind (bash) and bindkey (zsh).
    * Specifically, add bindings for normal paging, lolcat, and lolcat paging. See [this SO answer](http://serverfault.com/questions/31845/is-there-a-way-to-configure-bash-to-always-page-output/31870#31870) for advice.
    * Use a shared data structure to maintain these keybindings and not just literal values.
    * Find more keys that could be bound.
* Remove redundancy in the version check.
* Decide standard of hyphens (probably) or underscores (probably not) and stick to them for functions, aliases, commands, and file names.
* Set up a tmuxinator config which opens up emacs config and dotfiles repos.
* Make `ssh-agent` connect to any previously started `ssh-agent` process.
* Try to get rid of eval hackery in path utils.
* Write a zsh-specific version of path_utils, since it could be a lot more efficient.
* Write a command for updating the dotfiles and emacs repos.
* Investigate other ways of install autojump.
* Figure out why MANPATH isn't getting set correctly in bash but it is in zsh.
    * Definitely has to do with `/etc/zshenv` and `/usr/libexec/path_helper`.
    * Problem mitigated by new configuration.
* Write a function for creating a new tmux tab and automatically naming it.
* Get SSH keys under control. Decide which ones need to be shared, and
  add a passphrase or something using `ssh-agent`.
