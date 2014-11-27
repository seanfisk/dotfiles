# -*- coding: utf-8 -*- pylint: disable=invalid-name,undefined-variable
"""IPython configuration for Powerline"""

#------------------------------------------------------------------------------
# Powerline configuration
#------------------------------------------------------------------------------

# https://powerline.readthedocs.org/en/latest/usage/other.html#ipython-prompt
# Only activate Powerline if it's available. If it's not, print a warning.
import imp
try:
    imp.find_module('powerline')
    c.InteractiveShellApp.extensions.append(
        'powerline.bindings.ipython.post_0_11')
except ImportError:
    import IPython
    # Pylint can't find this function for some reason...
    IPython.utils.warn.warn( # pylint: disable=no-member
        'Could not find powerline module; Powerline not loaded.')
