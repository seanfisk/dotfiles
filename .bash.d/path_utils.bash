#!/bin/bash
# Utils for manipulating the path
# Compiled by Sean Fisk

# Credit : <http://stackoverflow.com/questions/370047/what-is-the-most-elegant-way-to-remove-a-path-from-the-path-variable-in-bash/370255#370255>
# $1: element to remove from the path
# $2: optional: name of variable to parse instead of PATH
path_remove() {
	local var_name=${2:-PATH}
	# get the value of the variable in var_name
  local var=$(eval echo \$$var_name)
	IFS=:
	# convert it to an array, the echo is for zsh compatiblity
	path_arr=($(echo "$var"))
	unset IFS
	# perform any array operations to remove elements from the array
  # path_arr cannot be local, as I think it's being used in a subshell
	path_arr=(${path_arr[@]%%$1})
	IFS=:
	local new_path="${path_arr[*]}"
	unset IFS
	# output the new array
	export "$var_name=$new_path"
}

# remove duplicate path entries
# $1: optional: name of variable to parse instead of PATH
path_remove_duplicates() {
  local var_name=${1:-PATH}
  # get the value of the variable in var_name
  local var=$(eval echo \$$var_name)
  IFS=:
	# convert it to an array, the echo is for zsh compatiblity
	# there are better ways to do this with zsh,
	# but I'd like to be bash compatible as well
  # path_arr cannot be local, as I think it's being used in a subshell
	path_arr=($(echo "$PATH"))
	IFS=$'\n'
	# strip out duplicates lines using awk and bring it back into an array
	path_arr=($(echo "${path_arr[*]}" | awk ' !x[$0]++'))
	IFS=:
	# put the colons back in
	local new_path="${path_arr[*]}"
	unset IFS
	# output the new array
	export "$var_name=$new_path"
}