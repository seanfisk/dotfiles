# -*- coding: utf-8; -*-

"""Custom Powerline segments."""

from __future__ import unicode_literals, absolute_import, division
import re
import errno
import subprocess

from powerline.lib.encoding import get_preferred_input_encoding # pylint: disable=import-error,no-name-in-module

NOT_INSTALLED_RE = re.compile(
    r".*: version `(?P<version>.*)' is not installed$")
"""Pattern to extract the missing version from the program's error message."""

def _make_tool_segment(tool):
    def tool_segment(pl): # pylint: disable=invalid-name
        """Powerline segment for {}.""".format(tool)
        # Note: pl is a PowerlineLogger, and "expects to receive message in an
        # str.format() format, not in printf-like format."

        command = [tool, 'version-name']
        # Used only for exception messages.
        command_str = ' '.join(command)

        # Run the process.
        try:
            proc = subprocess.Popen(
                command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except OSError as exc:
            if exc.errno == errno.ENOENT:
                # This error probably means that the operating system couldn't
                # find the tool's executable. In this case, don't render the
                # segment. This is an opinionated decision, but it is useful
                # for people who don't have the tool installed on all of the
                # machines on which they use their Powerline configuration.
                pl.debug('Tool executable not found: {0}', tool)
                return []
            raise
        outs = proc.communicate()

        # Try to decode the output.
        try:
            out, err = (b.decode(get_preferred_input_encoding()).rstrip()
                        for b in outs)
        except UnicodeDecodeError:
            pl.exception('Decoding output of command failed: {0}', command_str)

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

        return [{
            'contents': contents,
            'highlight_groups': [tool],
        }]

    return tool_segment

for _tool in ['rbenv', 'pyenv']:
    globals()[_tool] = _make_tool_segment(_tool)
