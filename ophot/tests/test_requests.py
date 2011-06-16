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
"""Unit tests for the requests module."""
import json
import os
import tempfile
import unittest

from flask import request

from ophot import app
from ophot import before_request
from ophot import init_db
from ophot.requests import add_category
from ophot.requests import change_category
from ophot.requests import change_category_name
from ophot.requests import change_spacing
from ophot.requests import delete_category
from ophot.requests import delete_photo
from ophot.requests import get_categories
from ophot.requests import get_photos
from ophot.requests import swap_display_positions
from ophot.requests import update_personal
from ophot.tests import TestSupport


def query_url(base, **kw):
    """Creates a URL with initial part *base* and with query strings given by
    keyword arguments.

    """
    query = '&'.join('{0[0]}={0[1]}'.format(item) for item in kw.iteritems())
    return '{0}?{1}'.format(base, query)


class RequestsTestCase(TestSupport):
    """Test class for the requests module."""

    def test_add_category(self):
        """Test for adding a category."""
        self._login()
        result = self.app.get(query_url('/_add_category', categoryname='foo'))
        result = json.loads(result.data)
        self.assertEqual(True, result['added'])
        self.assertEqual(4, result['categoryid'])
        self.assertEqual('foo', result['categoryname'])
