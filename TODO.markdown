TODO for Sean Fisk's Dotfiles
=============================

* Investigate other ways of install autojump.
* Remove oh-my-zsh auto-update feature.
* Figure out why MANPATH isn't getting set correctly in bash but it is in zsh.
    * Definitely has to do with `/etc/zshenv` and `/usr/libexec/path_helper`.
    * Problem mitigated by new configuration.
* Write a function for creating a new tmux tab and automatically naming it.
* Get SSH keys under control. Decide which ones need to be shared, and
  add a passphrase or something using `ssh-agent`.
