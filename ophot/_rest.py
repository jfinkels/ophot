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
"""Provides common functionality for modules exposing REST/JSON routes."""
# imports for compatibility with future python versions
from __future__ import absolute_import
from __future__ import division

# imports from third-party modules
from flask import jsonify


def _to_document_dict(names, db_row):
    """Returns a dictionary mapping the specified *names* to each of the values
    in the *db_row* parameter.

    Both *names* and *db_row* must be iterables.
    """
    return dict(zip(names, db_row))


def jsonify_status_code(status_code, *args, **kw):
    """Returns a jsonified response with the specified HTTP status code.

    The positional and keyword arguments are passed directly to the jsonify
    function which creates the response.

    """
    response = jsonify(*args, **kw)
    response.status_code = status_code
    return response


def to_category_dict(db_row):
    """Returns a dictionary representation of a category object specified by
    the given *db_row* parameter.

    """
    return _to_document_dict(('id', 'name'), db_row)


def to_photo_dict(db_row):
    """Returns a dictionary representation of a photo object specified by
    the given *db_row* parameter.

    """
    return _to_document_dict(('id', 'displayposition', 'filename',
                              'categoryid'), db_row)
