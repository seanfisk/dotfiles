non-native-dns() {
	echo "The \`$1' command does not use native macOS DNS resolution facilities. Using the \`dns' or \`rdns' alias is recommended." >&2
	$@
}
