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
"""Provides REST/JSON routes for reading and writing categories."""
# imports for compatibility with future python versions
from __future__ import absolute_import
from __future__ import division

# imports from third-party modules
from flask import g
from flask import jsonify
from flask import request
from flask import make_response

# imports from this application
from ophot import app
from ophot import require_logged_in
from ophot._rest import to_category_dict
from ophot.queries import Q_GET_CATEGORIES
from ophot.queries import Q_GET_CATEGORY_BY_ID
from ophot.queries import Q_GET_CATEGORY_BY_NAME
from ophot.queries import Q_UPDATE_CATEGORY_NAME


def _update_category_name(categoryid, name):
    """Updates the name of the category with the specified ID.

    """
    g.db.execute(Q_UPDATE_CATEGORY_NAME.format(categoryid, name))
    g.db.commit()


@app.route('/categories', methods=['GET'])
def get_categories():
    """Returns information for every category in the database, returned as an
    array sorted by name in ascending order.

    The JSON response will look like this::
        {
            "items":
              [
                  {
                      "id": 1,
                      "name": "landscape"
                  },
                  {
                      "id": 3,
                      "name": "personal"
                  },
                  {
                      "id": 2,
                      "name": "portrait"
                  }
              ]
        }
    """
    result = g.db.execute(Q_GET_CATEGORIES).fetchall()
    return jsonify(items=[to_category_dict(row) for row in result])


@app.route('/categories', methods=['POST'])
def create_category():
    """Adds a category to the database.

    Request argument is *name*, a string which is the name of the category to
    add.

    For example, if the input is::
        {
            "name": "foo"
        }

    then the JSON response will look like this::
        {
            "id": 4,
            "name": "foo"
        }

    """
    require_logged_in()
    categoryname = request.form.get('name')
    g.db.execute(Q_ADD_CATEGORY, [categoryname])
    g.db.commit()
    result = g.db.execute(Q_GET_CATEGORY_BY_NAME.format(categoryname))
    # TODO subclass response to create JsonifyResponse which allows status code
    # to be set in the constructor
    response = jsonify(to_category_dict(result.fetchone()))
    response.status_code = 201
    return response


@app.route('/categories/<int:categoryid>', methods=['GET'])
def get_category(categoryid):
    """Returns information for the category with the specified ID.
    
    For example, if the input is::
        {
            "id": 1
        }

    The JSON response will look like this::
        {
            "id": 1,
            "name": "personal"
        }
    """
    result = g.db.execute(Q_GET_CATEGORY_BY_ID.format(categoryname))
    return jsonify(to_category_dict(result.fetchone()))


#@app.route('/categories/<int:categoryid>', methods=['PATCH'])
@app.route('/categories/<int:categoryid>', methods=['POST'])
def update_category(categoryid):
    """Updates the properties of the category with the specified ID.

    The request argument is *name*, which is the name to apply to the category.

    For example, if the input is::
        {
            "name": "foo"
        }

    then the JSON response will look like this::
        {
            "id": 2,
            "name": "foo"
        }
    """
    if 'name' in request.form:
        _update_category_name(categoryid, request.form.get('name'))
    # TODO is it correct to make another read from the database to get the
    # updated data, or should we just assume that the updated data is there?
    return get_category(categoryid)


@app.route('/categories/<int:categoryid>', methods=['DELETE'])
def delete_category(categoryid):
    """Deletes the category with the specified ID.

    If the category is deleted, the response will be HTTP Status 204 No
    Content.

    """
    require_logged_in()
    g.db.execute(Q_DELETE_CATEGORY.format(categoryid))
    g.db.commit()
    return make_response(None, 204)
