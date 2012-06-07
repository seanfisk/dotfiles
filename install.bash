#!/usr/bin/env bash

# Dotfiles installation / removal script
# by Sean Fisk

set -o nounset
set -o errexit

# Mac OS X users:
# Set LN_EXECUTABLE to the path or name to your GNU coreutils `ln' exectuable and invoke like this
# $ LN_EXECUTABLE=gln ./install.bash install
LN_EXECUTABLE=${LN_EXECUTABLE:-ln}

usage()
{
	echo "Usage: $0 [install | remove]" 1>&2
	exit 1
}

if [[ $# -ne 1 ]]; then
	usage
fi

readonly SCRIPT_NAME=$(basename "$0")
readonly INSTALL_DIR=~
readonly IGNORE_REGEX="((^\.git(ignore|modules)?|$SCRIPT_NAME)|\.markdown)$"

for FILE in $(ls -A | grep -iEv "$IGNORE_REGEX"); do
	DEST=$INSTALL_DIR/$FILE
	SOURCE=$(pwd -P)/$FILE
	case $1 in
		install)
			set -o xtrace
			"$LN_EXECUTABLE" \
				--backup=existing \
				--interactive \
				--symbolic \
				--no-target-directory \
				"$SOURCE" "$DEST"
			set +o xtrace
			;;
		remove)
			if [[ -L "$DEST" && $(readlink "$DEST") == "$SOURCE" ]]; then
				set -o xtrace
				rm "$DEST"
				set +o xtrace
			fi
			;;
		*)
			usage
			;;
	esac
done
