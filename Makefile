INSTALL = install
INSTALL_PROGRAM = $(INSTALL)
INSTALL_DATA = $(INSTALL) -b -m 644
# INSTALL_RECURSIVE idea stolen from
# <http://lists.freebsd.org/pipermail/freebsd-ports/2007-February/038476.html>
INSTALL_RECURSIVE = $(SHELL) -c 'find "$$1" | cpio -dmpuv "$$2"' --
ALL_INSTALL_TARGETS = bash zsh ack git hg tmux x11
PYPI_ROOT = http://localhost:4040/root/pypi/+simple/

# pass prefix on the command-line to change install location
# e.g.,
# make prefix=/home/dir/with/weird/path
prefix = $(HOME)

.PHONY: first install install-osx $(ALL_INSTALL_TARGETS) tmux-patch
first :
	@echo 'Please type ...'
	@echo "  \`make install' to install to \`$(prefix)'"
	@echo "  \`make python' to install PyPi settings for devpi"
	@echo "  \`make prefix=/my/different/prefix install' to install to a different directory."

install: $(ALL_INSTALL_TARGETS)

install-osx: $(ALL_INSTALL_TARGETS) tmux-patch

bash:
	$(INSTALL_DATA) .bashrc "$(prefix)"
	$(INSTALL_DATA) .bash_profile "$(prefix)"
	$(INSTALL_RECURSIVE) .shell_common.d "$(prefix)"

zsh: bash
	$(INSTALL_DATA) .zshrc "$(prefix)"
	$(INSTALL_DATA) .zprofile "$(prefix)"
	# oh-my-zsh has an auto-update feature, symbolic link so it works
	# for linking: symbolic link, no dereference, force
	ln -snf "$(realpath .oh-my-zsh)" "$(abspath $(prefix))/.oh-my-zsh"

ack:
	$(INSTALL_DATA) .ackrc "$(prefix)"

git:
	$(INSTALL_DATA) .gitconfig "$(prefix)"
	$(INSTALL_DATA) .gitignore_global "$(prefix)"

hg:
	$(INSTALL_DATA) .hgrc "$(prefix)"

tmux:
	$(INSTALL_DATA) .tmux.conf "$(prefix)"

x11:
	$(INSTALL_DATA) .Xkbmap "$(prefix)"

tmux-patch:
	patch "$(prefix)/.tmux.conf" tmux-macosx.patch

# Not yet included in ALL_INSTALL_TARGETS because it modifies global pip settings.
python:
	$(INSTALL_RECURSIVE) .pip "$(prefix)"
	echo "$(PYPI_ROOT)" >> "$(prefix)/.pip/pip.conf"
	$(INSTALL_DATA) .pydistutils.cfg "$(prefix)"
	echo "$(PYPI_ROOT)" >> "$(prefix)/.pydistutils.cfg"
