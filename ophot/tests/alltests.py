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
"""Provides all the tests as a suite.

This test suite can be specified in the setup.py script as the test suite for
the "python setup.py test" command.

"""
# imports for compatibility with future python versions
from __future__ import absolute_import
from __future__ import division

# imports from built-in modules
from unittest import defaultTestLoader as loader
from unittest import TestSuite as Suite


def tests_from_modules(*modules):
    """Returns a unittest.TestSuite containing tests loaded from all the
    modules listed in *modules*.

    """
    return Suite([loader.loadTestsFromModule(module) for module in modules])


from . import test_categories
from . import test_ophot
from . import test_photos
from . import test_rest
from . import test_user
from . import test_views

alltests = tests_from_modules(
    test_categories,
    test_ophot,
    test_photos,
    test_rest,
    test_user,
    test_views
    )
