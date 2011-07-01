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
"""Unit tests for the filters module."""
# imports for compatibility with future python versions
from __future__ import absolute_import
from __future__ import division

# imports from third-party application
from jinja2 import Environment
from jinja2.nodes import EvalContext

# imports from this application
from .helpers import TestSupport
from ..filters import link_emails

class FiltersTestCase(TestSupport):
    """Test class for the filters module."""

    def test_link_emails(self):
        """Test for replacing email addresses in a string with mailto links."""
        email = 'example@example.com'
        teststring = 'Hello, world {0}, foo'.format(email)
        result = link_emails(EvalContext(Environment()), teststring)
        self.assertIn('<a href="mailto:{0}">{0}</a>'.format(email), result)
