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
"""Provides general functions needed for other modules in this package."""
# imports for compatibility with future python versions
from __future__ import absolute_import
from __future__ import division

# imports from built-in modules
from contextlib import closing
import sqlite3

# imports from third-party modules
from flask import abort
from flask import g
from flask import session

# imports from this application
from .app import app
from .queries import Q_GET_CATEGORY
from .queries import Q_GET_CATEGORIES
from .queries import Q_GET_LAST_DISP_POS


@app.after_request
def after_request(response):
    """Closes the database connection stored in the db attribute of the g
    object.

    The response to the request is returned unchanged.

    """
    g.db.close()
    return response


@app.before_request
def before_request():
    """Stores the database connection in the db attribute of the g object."""
    g.db = connect_db()


def connect_db():
    """Gets a connection to the SQLite database."""
    return sqlite3.connect(app.config['DATABASE'])


def init_db():
    """Initialize the database using the schema specified in the configuration.

    """
    with closing(connect_db()) as db:
        with app.open_resource(app.config['SCHEMA']) as f:
            db.cursor().executescript(f.read())
        db.commit()


def get_last_display_position(categoryid):
    """Helper method which returns the index in the display sequence of the
    last photo in the specified category.

    Might return None.

    """
    # sometimes returns None
    return select_single(Q_GET_LAST_DISP_POS.format(categoryid))


def require_logged_in():
    """Aborts with HTTP error 401 Unauthorized if the user is not logged in on
    this session.

    """
    if not session.get('logged_in'):
        abort(401)


def select_single_row(query):
    """Executes the given query and returns the first matching row, or None if
    the query would not return any rows.

    """
    result = g.db.execute(query).fetchone()
    return result


def select_single(query):
    """Executes the given *query* and returns the first field in the first
    matching row.

    If the specified query would return no rows, then this function returns
    None.
    """
    result = select_single_row(query)
    if result is None:
        return None
    return result[0]
