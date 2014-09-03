from __future__ import unicode_literals, absolute_import, division
import subprocess

COMMAND = 'version-name'


def make_tool_segment(tool):
    def tool_segment(pl):
        command = [tool, COMMAND]
        # Used only for exception messages.
        command_str = ' '.join(command)
        try:
            version_name_bytes = subprocess.check_output(command)
        except subprocess.CalledProcessError:
            pl.exception('Calling {0} failed.', repr(command_str))
        try:
            version_name_unicode = version_name_bytes.decode('utf-8')
        except:
            pl.exception('Error decoding output of {0}.', repr(command_str))
        version_name = version_name_unicode.rstrip()
        return [{
            'contents': version_name,
            'highlight_group': [tool],
        }]

    return tool_segment

pyenv = make_tool_segment('pyenv')
rbenv = make_tool_segment('rbenv')
