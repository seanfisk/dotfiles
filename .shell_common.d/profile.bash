# Commands to be run in .bash_profile and .zprofile
#
# We would like this file to be run for all interative login shells.

# Path munging
source ~/.shell_common.d/path_utils.bash
# Start with default manpath entries and existing value of variable.
MANPATH=$MANPATH:$(man --path)

# Add hierarchies. It is helpful to add /usr so that INFOPATH gets
# correctly populated.
path_add_hierarchy /usr
path_add_hierarchy /usr/local
path_add_hierarchy ~/.local
# pip install --user XXX installs to here on Mac OS 10.8
path_add_hierarchy ~/Library/Python/2.7

# Add scripts directory.
PATH=~/bin:$PATH

# See this post for some more info (haha):
# <http://unix.stackexchange.com/questions/22329/gnu-texinfo-directory-search-method>
INFOPATH=/usr/local/share/info/emacs:$INFOPATH

# Nuke the dupes.
path_remove_duplicates PATH
path_remove_duplicates MANPATH
path_remove_duplicates INFOPATH

export PATH
export MANPATH
export INFOPATH

# Set umask for more privacy
umask u=rwx,g=,o=

# Add pyenv and rbenv paths to PATH.
for prefix in rb py; do
	tool=${prefix}env
	[[ -d ~/.$tool ]] && path_add_hierarchy ~/.$tool
done

# set the editor
export EDITOR='emacsclient --alternate-editor='
