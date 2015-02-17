# -*- coding: utf-8; -*-

"""Custom Powerline segments."""

from __future__ import unicode_literals, absolute_import, division
import re
import sys

# subprocess32 is a backport of Python 3.2's subprocess module to Python 2.
# When using Python 2, it is required for using these segments. The reason we
# require it is that Python 2's subprocess module attempts to encode its
# environment dictionary using the ascii codec, while Powerline decodes it
# using the system's preferred encoding. This causes frequent errors when there
# are non-ASCII characters in the environment. While we could hack around this
# for Python 2, subprocess32 includes other important bug fixes so we thought
# it prudent to use it.
if sys.version_info < (3,):
    try:
        import subprocess32 as subprocess
    except ImportError:
        raise NotImplementedError(
            'rbenv/pyenv segments under Python 2 require installation of the '
            'subprocess32 package. Please install it to use these segments.')
else:
    import subprocess

from powerline.lib.encoding import get_preferred_input_encoding # pylint: disable=import-error,no-name-in-module
from powerline.theme import requires_segment_info # pylint: disable=import-error,no-name-in-module

# rbenv/pyenv segments
# TODO: Make into installable Powerline segments.

NOT_INSTALLED_RE = re.compile(
    r".*: version `(?P<version>.*)' is not installed$")
"""Pattern to extract the missing version from the program's error message."""

def _make_tool_segment(tool):
    @requires_segment_info
    def tool_segment(pl, segment_info): # pylint: disable=invalid-name
        """Return the current {0} version name.""".format(tool)
        # Note: pl is a PowerlineLogger, and "expects to receive message in an
        # str.format() format, not in printf-like format."

        command = [tool, 'version-name']
        # Used only for exception messages.
        command_str = ' '.join(command)

        # Run the process.
        try:
            proc = subprocess.Popen(
                command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                # Have to specify these so that the extension works correctly
                # with the daemon.
                cwd=segment_info['getcwd'](), env=segment_info['environ'])
        except OSError:
            pl.exception('Could not execute command: {0}', command_str)
            return []

        outs = proc.communicate()

        # Try to decode the output.
        try:
            out, err = (b.decode(get_preferred_input_encoding()).rstrip()
                        for b in outs)
        except UnicodeDecodeError:
            pl.exception('Decoding output of command failed: {0}', command_str)
            return []

        # Check for success.
        if proc.returncode == 0:
            contents = out
        else:
            # If the call failed because the version does not exist, try to
            # output something helpful: the version name with a warning sign.
            match = NOT_INSTALLED_RE.match(err)

            # If the call failed for some other reason, log an error and don't
            # render the segment.
            if not match:
                pl.error(
                    'Comand exited with non-zero status: {0}', command_str)
                return []

            contents = match.group('version') + u' ⚠'

        return contents

    return tool_segment

for _tool in ['rbenv', 'pyenv']:
    globals()[_tool] = _make_tool_segment(_tool)

# Shell segments
# TODO: Make Powerline PR.
@requires_segment_info
def shell_version(pl, segment_info): # pylint: disable=invalid-name,unused-argument
    """Display the name and version of the currently-running shell."""
    return segment_info.get('shell_version', None)
