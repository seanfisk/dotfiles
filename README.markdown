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

My bash and zsh configurations are set up in a special way. Both bash
and zsh include a common set of aliases and functions usable in each
shell. In this way, I can use bash and zsh comfortably while
maintaining one base for my common files. I mostly stick to using zsh,
however.

Recommended Software
--------------------

These are some command-line utilities that I use often. They are
usually installed using [Homebrew][homebrew] (Mac OS X), [yum][yum]
(Fedora, CentOS), or [aptitude][aptitude] (Debian, Ubuntu), or
compiled from source and install to my `~/.local` directory.

Since I use it frequently, [autojump][autojump] is vendorized in this
repository and is automatically installed.

[pythonz][pythonz] and [rbenv][rbenv] could possibly be
vendorized. However, I've decided not to do that at this time because
I don't use Python and Ruby on every single machine on which I work.

* [ack][ack] - file tree search, grep replacement
* [aria2][aria2] - download utility and accelerator, similar to `wget`
* [autojump][autojump] - easily navigate directories
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
[aria2]: http://aria2.sourceforge.net/
[autojump]: https://github.com/joelthelion/autojump
[homebrew]: https://github.com/mxcl/homebrew
[htop-osx]: https://github.com/cynthia/htop-osx
[htop]: http://htop.sourceforge.net/
[pythonz]: https://github.com/saghul/pythonz
[rbenv]: https://github.com/sstephenson/rbenv
[tig]: http://jonas.nitro.dk/tig/
[tmux-osx-pasteboard]: https://github.com/ChrisJohnsen/tmux-MacOSX-pasteboard
[tmux]: http://tmux.sourceforge.net/
[tmuxinator]: https://github.com/aziz/tmuxinator
[virtualenvwrapper]: https://bitbucket.org/dhellmann/virtualenvwrapper
[xclip]: http://sourceforge.net/projects/xclip/
[yum]: http://yum.baseurl.org/
