# Set umask for more privacy. Child processes inherit the umask from parent processes, so it is correct to put this in the profile, not the rc.
# See http://en.wikipedia.org/wiki/Umask#Processes
umask u=rwx,g=,o=
