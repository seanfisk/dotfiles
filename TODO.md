TODO for Sean Fisk's Dotfiles
=============================

* Fix symbols thing from `powerline-lint`.
* Add linuxbrew support.
* Use Python json module for Powerline.
* Make rbenv and pyenv presence in Powerline conditional to whether we have each of them.
* Take availability of bash and zsh into account.
* Set up a tmuxinator config which opens up emacs, dotfiles, and chef (at least).
* Add fasd for Emacs.
* Make adding nodes to both shells a bit more elegant.
* Write a function for creating a new tmux tab and automatically naming it.
* Write a command for updating the dotfiles and emacs repos.
* Make (pyenv and rbenv Powerline support) an actual Python module.
* Consider substituting the path the powerline module into the IPython config file. This would allow powerline to be loaded from the same module no matter from what virtualenv IPython was running. Powerline would need to be single-source compatible with Python 2 and 3, and I'm not sure it is. I think it is though, so in theory it should work. Seems dirty though.
* Write a `find-tmux` function that will find a tmux session given a list of a number of machines. Test on Yellowstone/EOS.
* Write a function that will log in to the machine with the lightest load give a list of a number of machines. Test on Yellowstone/EOS.
* Figure out how to restart `ssh-agent` on Mac OS X when I accidentally kill it.
* Include some things from http://mths.be/dotfiles.
* Get SSH keys under control. Decide which ones need to be shared.
