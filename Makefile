INSTALL = install
INSTALL_PROGRAM = $(INSTALL)
INSTALL_DATA = $(INSTALL) -b -m 644
# INSTALL_RECURSIVE idea stolen from
# <http://lists.freebsd.org/pipermail/freebsd-ports/2007-February/038476.html>
INSTALL_RECURSIVE = $(SHELL) -c 'find "$$1" | cpio -dmpuv "$$2"' --

# pass prefix on the command-line to change install location
# e.g.,
# make prefix=/home/dir/with/weird/path
prefix = $(HOME)

.PHONY: first install bash zsh ack git tmux
first :
@echo 'Please type ...'
@echo "  \`make install' to install to \`$(prefix)'"
@echo "  \`make prefix=/my/different/prefix install' to install to a different directory."

install: bash zsh ack git tmux

bash:
	$(INSTALL_DATA) .bashrc "$(prefix)"
	$(INSTALL_DATA) .bash_profile "$(prefix)"
	$(INSTALL_DATA) .bash_logout "$(prefix)"
	$(INSTALL_RECURSIVE) .bash.d "$(prefix)"

zsh: bash
	$(INSTALL_DATA) .zshrc "$(prefix)"
	$(INSTALL_DATA) .zprofile "$(prefix)"
	$(INSTALL_DATA) .zlogout "$(prefix)"
	# oh-my-zsh has an auto-update feature, symbolic link so it works
	# for linking: symbolic link, no dereference, interactive
	ln -sni "$(realpath .oh-my-zsh)" "$(abspath $(prefix))/.oh-my-zsh"

ack:
	$(INSTALL_DATA) .ackrc "$(prefix)"

git:
	$(INSTALL_DATA) .gitconfig "$(prefix)"
	$(INSTALL_DATA) .gitignore_global "$(prefix)"

tmux:
	$(INSTALL_DATA) .tmux.conf "$(prefix)"
