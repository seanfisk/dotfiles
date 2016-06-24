# -*- coding: utf-8 -*-
"""Handle stored passwords via keyring."""

import keyring
from waflib.Configure import conf

@conf
def safe_get_password(self, system, username): # pylint: disable=unused-argument
    """Get a password from keyring, ignoring errors when a backend is
    unavailable."""
    try:
        # This will return None if not found
        return keyring.get_password(system, username)
    except RuntimeError:
        # Raised when no suitable backends are found
        return None
