# Utils for manipulating the path
# Compiled by Sean Fisk

# Inspired by <http://technotales.wordpress.com/2010/09/19/managing-path-and-manpath/>
# $1: Hiearchy to add (e.g., `/usr/local')
add_hierarchy_to_path() {
	local hierarchy=$1
	if [[ -d $hierarchy/bin ]]; then
		PATH=$hierarchy/bin:$PATH
	fi
	if [[ -d $hierarchy/sbin ]]; then
		PATH=$hierarchy/sbin:$PATH
	fi
	if [[ -d $hierarchy/man ]]; then
		MANPATH=$hierarchy/man:$MANPATH
	fi
	if [[ -d $hierarchy/share/man ]]; then
		MANPATH=$hierarchy/share/man:$MANPATH
	fi
}

# Credit : <http://stackoverflow.com/questions/370047/what-is-the-most-elegant-way-to-remove-a-path-from-the-path-variable-in-bash/370255#370255>
# $1: element to remove from the path
# $2: name of variable to parse
path_remove() {
	local var_name=$2
	# get the value of the variable in var_name
	local var=$(eval echo \$$var_name)
	IFS=:
	# convert it to an array, the echo is for zsh compatiblity
	path_arr=($(echo "$var"))
	unset IFS
	# perform any array operations to remove elements from the array
	path_arr=(${path_arr[@]%%$1})
	IFS=:
	local new_path="${path_arr[*]}"
	unset IFS
	# output the new array
	eval "$var_name=$new_path"
}

# remove duplicate path entries
# $1: name of variable to parse
path_remove_duplicates() {
	local var_name=$1
	# get the value of the variable in var_name
	local var=$(eval echo \$$var_name)
	IFS=:
	# convert it to an array, the echo is for zsh compatiblity
	# there are better ways to do this with zsh,
	# but I'd like to be bash compatible as well
	# path_arr cannot be local, as I think it's being used in a subshell
	path_arr=($(echo "$var"))
	IFS=$'\n'
	# strip out duplicates lines using awk and bring it back into an array
	path_arr=($(echo "${path_arr[*]}" | awk ' !x[$0]++'))
	IFS=:
	# put the colons back in
	local new_path="${path_arr[*]}"
	unset IFS
	# output the new array
	eval "$var_name=$new_path"
}

# check to see if an executable is in the path
# bash and zsh compatible
#
executable_in_path() {
	builtin hash $1 2>/dev/null
}

# check to see if a function or executable exists
# this is meant for my use only, so it is not extremely robust
function_or_executable_exists() {
	builtin type $1 &> /dev/null
}
