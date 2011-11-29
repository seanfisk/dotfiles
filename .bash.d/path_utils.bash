#!/bin/bash
# Utils for manipulating the path
# Compiled by Sean Fisk

# Credit : <http://stackoverflow.com/questions/370047/what-is-the-most-elegant-way-to-remove-a-path-from-the-path-variable-in-bash/370255#370255>
path_remove() {
    IFS=:
    # convert it to an array, the echo is for Z shell compatiblity
    path_arr=($(echo "$PATH"))
    unset IFS
    # perform any array operations to remove elements from the array
    path_arr=(${path_arr[@]%%$1})
    IFS=:
    new_path="${path_arr[*]}"
    unset IFS
    # output the new array
    export "PATH=$new_path"
}

# remove duplicate path entries
path_remove_duplicates() {
    IFS=:
    # convert it to an array, the echo is for zsh compatiblity
    # there are better ways to do this with zsh,
    # but I'd like to be bash compatible as well
    path_arr=($(echo "$PATH"))
    IFS=$'\n'
    # strip out duplicates lines using awk and bring it back into an array
    path_arr=($(echo "${path_arr[*]}" | awk ' !x[$0]++'))
    IFS=:
    # put the colons back in
    new_path="${path_arr[*]}"
    unset IFS
    # output the new array
    export "PATH=$new_path"
}