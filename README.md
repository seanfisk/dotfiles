Sean's Dotfiles
===============

These are my configuration files for shells other common software. Currently, this repository contains configurations for **bash**, **zsh**, **git**, **mercurial**, **tmux**, **ack**, and **X windows**.

This configuration is compatible only with **GNU Bash 4 and up** and **Zsh 5 and up**. Backwards compatibility is typically not an issue because I compile my own software when it is not available on a given machine.

I don't recommend just cloning this repository and using it. Rather, I would recommend picking out pieces that you like and inserting them into your own configurations.

Installation
------------

To install the dotfiles to your home directory:

    make install

To install the dotfiles to a different prefix:

    make prefix=/my/different/prefix install

To install with the tmux pasteboard workaround on Mac OS X (see `tmux-macosx.patch`):

    make install-osx

Shell Configurations
--------------------

My bash and zsh configurations are set up in a special way. Both bash and zsh include a common set of aliases and functions usable in each shell. In this way, I can use bash and zsh comfortably while maintaining one base for my common files. My main shell is zsh.

The two most annoying things to deal with are *environment variables* and *shell startup files*. These are some links that help explain these topics:

* http://shreevatsa.wordpress.com/2008/03/30/zshbash-startup-files-loading-order-bashrc-zshrc-etc/
* https://help.ubuntu.com/community/EnvironmentVariables
* http://stackoverflow.com/questions/135688/setting-environment-variables-in-os-x/5444960
* https://github.com/sstephenson/rbenv/wiki/Unix-shell-initialization

Recommended Software
--------------------

These are some command-line utilities that I use often. They are usually installed using [Homebrew][homebrew] (Mac OS X), [yum][yum] (Fedora, CentOS), or [aptitude][aptitude] (Debian, Ubuntu), or compiled from source and installed to my `~/.local` directory.

[homebrew]: https://github.com/mxcl/homebrew
[yum]: http://yum.baseurl.org/
[aptitude]: http://wiki.debian.org/Aptitude

* [ack][ack] - file tree search, grep replacement
* [aria2][aria2] - download utility and accelerator, similar to `wget`
* [autojump][autojump] - easily navigate directories
* [htop][htop], [htop-osx][htop-osx] - top replacement
* [pyenv][pyenv] - Python environment manager
* [rbenv][rbenv] - Ruby environment manager
* [tig][tig] - text-interface mode for git (git log viewer, mostly replaced by [magit](https://github.com/magit/magit))
* [tmux-MacOSX-pasteboard][tmux-osx-pasteboard] - Workaround for `pbpaste` and `pbcopy` under Mac OS X
* [tmux][tmux] - terminal multiplexer, GNU screen replacement
* [tmuxinator][tmuxinator] - manage complex tmux sessions easily
* [xclip][xclip] - command line interface to the X11 clipboard

[ack]: http://betterthangrep.com/
[aria2]: http://aria2.sourceforge.net/
[autojump]: https://github.com/joelthelion/autojump
[htop-osx]: https://github.com/cynthia/htop-osx
[htop]: http://htop.sourceforge.net/
[pyenv]: https://github.com/yyuu/pyenv
[rbenv]: https://github.com/sstephenson/rbenv
[tig]: http://jonas.nitro.dk/tig/
[tmux-osx-pasteboard]: https://github.com/ChrisJohnsen/tmux-MacOSX-pasteboard
[tmux]: http://tmux.sourceforge.net/
[tmuxinator]: https://github.com/aziz/tmuxinator
[xclip]: http://sourceforge.net/projects/xclip/
