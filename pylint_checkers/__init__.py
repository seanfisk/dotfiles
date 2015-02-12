# -*- coding: utf-8 -*-

"""Local pylint checkers."""

from pylint_checkers.boilerplate import BoilerplateChecker
from pylint_checkers.waf import WafChecker

def register(linter):
    """Register our checkers."""
    for cls in [BoilerplateChecker, WafChecker]:
        linter.register_checker(cls(linter))
