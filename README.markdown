Shell and other configuration files (dotfiles) for Sean Fisk
============================================================

These are my configuration files for various shells and other
things. Currently, it contains configurations for the **bash shell**,
**z shell**, **git**, **tmux**, and **ack**.

I don't recommend just cloning this repository and using it. Rather, I
would recommend picking out pieces that you like and inserting them
into your own configurations.

Installation
------------

To install the dotfiles to your home directory:

    make install

To install the dotfiles to a different prefix:

    make prefix=/my/different/prefix install

Shell Configurations
--------------------

My bash and zsh configurations are set up in a special way. I have
tried to keep my bash configurations zsh-compatible, so all zsh config
files automatically include my bash configuration files as well. In
this way, I can use bash and zsh comfortably while maintaining one
base for my common files. I mostly stick to using zsh, however.

Recommended Software
--------------------

These are some command-line utilities that I use often. They are
usually installed using [Homebrew][homebrew] (Mac OS X), [yum][yum]
(Fedora, CentOS), or [aptitude][aptitude] (Debian, Ubuntu), or
compiled from source and install to my `~/.local` directory.

* [ack][ack] - file tree search, grep replacement
* [autojump][autojump] - easily navigate directories
* [axel][axel] - download accelerator
* [htop][htop], [htop-osx][htop-osx] - top replacement
* [pythonz][pythonz] - Python version manager
* [rbenv][rbenv] - Ruby environment manager
* [tig][tig] - text-interface mode for git (git log viewer)
* [tmux-MacOSX-pasteboard][tmux-osx-pasteboard] - Workaround for
  `pbpaste` and `pbcopy` under Mac OS X
* [tmux][tmux] - terminal multiplexer, GNU screen replacement
* [tmuxinator][tmuxinator] - manage complex tmux sessions easily
* [virtualenvwrapper][virtualenvwrapper] - Python environment manager
* [xclip][xclip] - command line interface to the X11 clipboard

[ack]: http://betterthangrep.com/
[aptitude]: http://wiki.debian.org/Aptitude
[autojump]: https://github.com/joelthelion/autojump
[axel]: http://axel.alioth.debian.org/
[homebrew]: https://github.com/mxcl/homebrew
[htop-osx]: https://github.com/cynthia/htop-osx
[htop]: http://htop.sourceforge.net/
[pythonz]: https://github.com/utahta/pythonbrew
[rbenv]: https://github.com/sstephenson/rbenv
[tig]: http://jonas.nitro.dk/tig/
[tmux-osx-pasteboard]: https://github.com/ChrisJohnsen/tmux-MacOSX-pasteboard
[tmux]: http://tmux.sourceforge.net/
[tmuxinator]: https://github.com/aziz/tmuxinator
[virtualenvwrapper]: https://bitbucket.org/dhellmann/virtualenvwrapper
[xclip]: http://sourceforge.net/projects/xclip/
[yum]: http://yum.baseurl.org/
