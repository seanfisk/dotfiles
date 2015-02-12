# -*- coding: utf-8 -*-

# Uses io module API; Python 3 only

"""Pylint module boilerplate checker."""

import io

from pylint.interfaces import IRawChecker
from pylint.checkers import BaseChecker
from pylint.checkers.utils import check_messages

REQUIRED_CODING = 'coding: utf-8'
"""Required source encoding"""

class BoilerplateChecker(BaseChecker):
    """Checks for project-specific boilerplate."""
    __implements__ = IRawChecker

    name = 'boilerplate'
    msgs = {
        'C9001': (
            'Module is missing or has incorrect source code encoding',
            'source-encoding',
            'Used when source code encoding is missing or incorrect',
        ),
    }

    @check_messages('source-encoding')
    def process_module(self, module):
        """Ensure the module has the correct boilerplate."""
        add_msg = lambda l: self.add_message('source-encoding', line=l)
        # 'module.file_stream' is a 'io.BufferedReader', so any reads will be
        # in binary mode. We wrap it with 'io.TextIOWrapper' to read in text
        # mode.
        #
        # Following the lead of EncodingChecker in 'checkers/misc.py' in the
        # pylint source tree, we default to ASCII. This is also specified under
        # 'Defining the Encoding' in PEP 263. Funny enough, this is the exact
        # problem this checker is designed to solve.
        stream = io.TextIOWrapper(
            module.file_stream, encoding=(module.file_encoding or 'ascii'))
        try:
            first_line = next(stream)
        except StopIteration:
            return # Empty file, always valid
        else:
            if REQUIRED_CODING not in first_line:
                try:
                    second_line = next(stream)
                except StopIteration:
                    # One-line file; did not contain required declaration
                    add_msg(1)
                else:
                    if first_line.lstrip().startswith('#!'):
                        # Multi-line file; has hash-bang; second line did not
                        # contain required declaration
                        if REQUIRED_CODING not in second_line:
                            add_msg(2)
                    else:
                        # Multi-line file; no hash-bang; first line did not
                        # contain required declaration
                        add_msg(1)
