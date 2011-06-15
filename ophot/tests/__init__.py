# Copyright 2011 Jeffrey Finkelstein
#
# This file is part of Ophot.
#
# Ophot is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ophot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Ophot.  If not, see <http://www.gnu.org/licenses/>.
"""Provides a test suite for all tests for the Ophot package."""
from unittest import defaultTestLoader as loader
from unittest import TestSuite as Suite

import test_ophot
import test_requests

def tests_from_modules(*modules):
    """Returns a unittest.TestSuite containing tests loaded from all the
    modules listed in *modules*.

    """
    return Suite([loader.loadTestsFromModule(module) for module in modules])

alltests = tests_from_modules(test_ophot, test_requests)
