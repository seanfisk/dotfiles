Sean's Dotfiles
===============

These are my configuration files for shells and other common software on UNIX-like operating systems. Currently, this repository contains configurations for **bash**, **zsh**, **git**, **mercurial**, **tmux**, **ack**, and **X windows**.

This configuration is compatible only with **GNU Bash 4 and up** and **Zsh 5 and up**. Backwards compatibility is typically not an issue because I compile my own software when it is not available on a given machine.

I don't recommend just cloning this repository and using it. Rather, I would recommend picking out pieces that you like and inserting them into your own configurations.

Installation
------------

To install the dotfiles to your home directory:

    make install

To install the dotfiles to a different prefix:

    make prefix=/my/different/prefix install

Mac OS X Notes
--------------

Mac OS X suffers from two issues which pertain directly to the dotfiles.

First, the Mac OS X-provided global zsh startup files are organized incorrectly. Mac OS X uses a small utility called [`path_helper`][path_helper] which loads a default `PATH` for various shells. With bash, it is configured to append to the `PATH` only when bash is started as a login shell (using `/etc/profile`). However, with zsh, this code is placed in `/etc/zshenv` which is read on login and non-login shell startups. A [workaround in my Macbook configuration][macbook-chef-zsh] remedies this problem.

[path_helper]: https://developer.apple.com/library/mac/documentation/Darwin/Reference/ManPages/man8/path_helper.8.html
[macbook-chef-zsh]: https://github.com/seanfisk/macbook-chef-repo/blob/f18ba3df5439ec681dc3b59b7faedcae1fdcb9e6/cookbooks/macbook_setup/recipes/default.rb#L67

The second issue has to do with [tmux][tmux] and the Mac OS X clipboard. Please see the [tmux-MacOSX-pasteboard][tmux-macosx-pasteboard] repository for the description of the problem and the workaround. To install with the tmux pasteboard workaround run:

    make install-osx

Please see `tmux-macosx.patch` for the patch that is applied. This patch assumes that the `reattach-to-user-namespace` utility is on the `PATH` (I put it in `~/bin`).

Shell Configurations
--------------------

My bash and zsh configurations are set up in a special way. Both bash and zsh include a common set of aliases and functions usable in each shell. In this way, I can use bash and zsh comfortably while maintaining one base for my common files. My main shell is zsh.

The two most annoying things to deal with are *environment variables* and *shell startup files*. These are some links that help explain these topics:

* http://shreevatsa.wordpress.com/2008/03/30/zshbash-startup-files-loading-order-bashrc-zshrc-etc/
* https://help.ubuntu.com/community/EnvironmentVariables
* http://stackoverflow.com/questions/135688/setting-environment-variables-in-os-x/5444960
* https://github.com/sstephenson/rbenv/wiki/Unix-shell-initialization

Why generate dotfiles?
----------------------

For 90% of people who use shells, generating dotfiles would be overkill. However, for people like me who require many external tools and would like their dotfiles to work on different system, generation offers some key benefits:

+ Shell scripts have no module system that they can use to require certain features, so they typically depend on external executables. For example, if I wanted to download a file in Python, I could make my Python module depend on [Requests][requests]. However, a shell script would typically use `wget` or `curl`. Well-behaved scripts typically do checks for these executables and warn the script user that they are missing. However, these checks can be tedious and are frequently omitted, leaving the presence of these executables to pure assumption.
+ Because shell scripting languages are interpreted, they are only able to do checks like this at runtime. For blocks of code that run frequently (like the rc file or the prompt), these checks can start to take up precious time.

By treating the shell configuration files as just another piece of compiled software, we can generate optimized configuration files based on the utilities found on the system at compile-time.

[requests]: https://github.com/kennethreitz/requests

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
* [tmux-MacOSX-pasteboard][tmux-macosx-pasteboard] - workaround for `pbpaste` and `pbcopy` under Mac OS X
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
[tmux-macosx-pasteboard]: https://github.com/ChrisJohnsen/tmux-MacOSX-pasteboard
[tmux]: http://tmux.sourceforge.net/
[tmuxinator]: https://github.com/aziz/tmuxinator
[xclip]: http://sourceforge.net/projects/xclip/
