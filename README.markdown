Shell and other configuration files (dotfiles) for Sean Fisk
============================================================

These are my configuration files for various shells and other things. Currently, it contains configurations for the **bash shell**, **z shell**, **git**, and my friend Karlin's **[working directory script](https://github.com/karlin/working-directory)**.

I don't recommend just cloning this repository and using it. Rather, I would recommend picking out pieces that you like and inserting them into your own configurations.

Installation
------------

Simply run `./install.bash install` from the repository to symbolic link all relevant dotfiles into your home directory. The script will offer you to backup each file if it already exists. It will not just clobber it.

To remove the configuration and unlink all files, run `./install.bash remove` from the repository.

**Mac OS X users!** - this install script uses features specific to the GNU version of the `ln` executable which are not present in Mac OS X's BSD version (I feel the BSD version is severely crippled). To install correctly, either manually link the files, or use [Homebrew](https://github.com/mxcl/homebrew) to install the `coreutils` formula. This installs all the GNU coreutils with a prefix of `g`. Invoke the install script like this:

	brew install coreutils
	LN_EXECUTABLE=gln ./install.bash install
	
The removal of the files does not use `ln` and therefore does not matter for removal.

Shell Configurations
--------------------

My bash and zsh configurations are set up in a special way. I have tried to keep my bash configurations zsh-compatible, so all zsh config files automatically include my bash configuration files as well. In this way, I can use bash and zsh comfortably while maintaining one base for my common files. I mostly stick to using zsh, however.

Recommended Software
--------------------

These are some command-line utilities that I use often:

* [tig][tig] - text-interface mode for git (git log viewer)
* [tmux][tmux] - terminal multiplexer, GNU screen replacement
* [tmux-MacOSX-pasteboard][tmux-osx-pasteboard] - Workaround for `pbpaste` and
  `pbcopy` under Mac OS X
* [rvm][rvm] - Ruby Version Manager
* [pythonbrew][pythonbrew] - Python version manager
* [xclip][xclip] - command line interface to the X11 clipboard
* [ack][ack] - file tree search, grep replacement
* [htop][htop], [htop-osx][htop-osx] - top replacement

[tig]: http://jonas.nitro.dk/tig/
[tmux]: http://tmux.sourceforge.net/
[tmux-osx-pasteboard]: https://github.com/ChrisJohnsen/tmux-MacOSX-pasteboard
[rvm]: http://beginrescueend.com/
[pythonbrew]: https://github.com/utahta/pythonbrew
[xclip]: http://sourceforge.net/projects/xclip/
[ack]: http://betterthangrep.com/
[htop]: http://htop.sourceforge.net/
[htop-osx]: https://github.com/cynthia/htop-osx
