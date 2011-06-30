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
"""Provides REST/JSON routes for reading and writing photos."""
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
from ophot import get_last_display_position
from ophot import require_logged_in
from ophot import select_single
from ophot._rest import to_photo_dict
from ophot.queries import Q_DELETE_PHOTO
from ophot.queries import Q_GET_PHOTO
from ophot.queries import Q_GET_PHOTO_BY_DISPLAYPOS
from ophot.queries import Q_GET_PHOTO_DISPLAYPOS
from ophot.queries import Q_GET_PHOTOS
from ophot.queries import Q_GET_PHOTOS_BY_CAT
from ophot.queries import Q_UPDATE_PHOTO_CATEGORY
from ophot.queries import Q_UPDATE_PHOTO_DISPLAYPOS


def _update_photo_category(photoid, categoryid):
    """Updates the category of the photo with the specified ID, and assigns the
    photo to the last display position.

    """
    position = (get_last_display_position(categoryid) or 0) + 1
    g.db.execute(Q_UPDATE_PHOTO_CATEGORY.format(categoryid, position, photoid))
    g.db.commit()


def _update_photo_displaypos(photoid, displayposition):
    """Updates the display position of the photo with the specified ID, or
    swaps it if the specified display position is already occupied.

    """
    # get the ID of the photo which already exists at the requested display
    # position (if there is one)
    existing = select_single(Q_GET_PHOTO_BY_DISPLAYPOS.format(displayposition))
    if existing:
        # move the photo that was already in that position to the old position
        # of the requested photo
        current_pos = select_single(Q_GET_PHOTO_DISPLAYPOS.format(photoid))
        g.db.execute(Q_UPDATE_PHOTO_DISPLAYPOS.format(current_pos, existing))
    # move the requested photo to the requested displayposition
    g.db.execute(Q_UPDATE_PHOTO_DISPLAYPOS.format(displayposition, photoid))
    g.db.commit()


@app.route('/photos/<int:photoid>', methods=['GET'])
def get_photo(photoid):
    """Returns information for the photo with the specified photoid.
    
    The JSON response will look like this::
        {
            "id": 42,
            "displayposition": 1,
            "filename": "path/to/file",
            "categoryid": 2
        }
    """
    result = g.db.execute(Q_GET_PHOTO.format(photoid)).fetchone()
    return jsonify(_to_photo_dict(('id', 'displayposition', 'filename',
                                   'categoryid'), result))
        

@app.route('/photos', methods=['GET'])
def get_photos():
    """Returns information for every photo in the database.

    The JSON response will look like this::
        [
            {
                "id": 42,
                "displayposition": 1,
                "filename": "path/to/file42",
                "categoryid": 2
            },
            {
                "id": 43,
                "displayposition": 2,
                "filename": "path/to/file43",
                "categoryid": 2
            }
        ]
    """
    result = g.db.execute(Q_GET_PHOTOS).fetchall()
    return jsonify([_to_photo_dict(('id', 'displayposition', 'filename',
                                    'categoryid'), row) for row in result])


@app.route('/photos/by-category/<int:categoryid>', methods=['GET'])
def get_photos_by_category(categoryid):
    """Returns information for every photo in the specified category, sorted by
    photo display position in ascending order.

    The JSON response will look like this::
        [
            {
                "id": 42,
                "displayposition": 1,
                "filename": "path/to/file42",
                "categoryid": 2
            },
            {
                "id": 43,
                "displayposition": 2,
                "filename": "path/to/file43",
                "categoryid": 2
            }
        ]
    """
    result = g.db.execute(Q_GET_PHOTOS_BY_CAT.format(categoryid)).fetchall()
    return jsonify([_to_photo_dict(('id', 'displayposition', 'filename',
                                    'categoryid'), row) for row in result])


#@app.route('/photos/<int:photoid>', methods=['PATCH'])
@app.route('/photos/<int:photoid>', methods=['POST'])
def update_photo(photoid):
    """Updates the properties of the photo with the specified ID.

    There are two mutually exclusive request arguments. The two possible
    arguments are *categoryid*, an integer which is the ID of the category to
    which the photo will be moved, and *displayposition*, which is the integer
    representing the display position of this photo within its category. If
    either one is specified, the other cannot be specified. Otherwise, the
    response will be HTTP Error 400 Bad Request.

    If the request would change the category of the photo, the display position
    of the photo is automatically set to one greater than the value of the
    greatest display position in the new category (or 1 if there are no other
    photos in that category).

    If the request would change the display position to a display position
    which is already claimed by some other photo, this will ''swap'' the
    display positions of the two photos.

    For example, if the input is::
        {
            "displayposition": 8
        }

    then the JSON response will look like this::
        {
            "id": 42,
            "displayposition": 8,
            "filename": "path/to/file",
            "categoryid": 2
        }
    """
    require_logged_in()
    if 'categoryid' in request.form:
        _update_photo_category(photoid, request.form.get('categoryid'))
    if 'displayposition' in request.args:
        _update_photo_displaypos(photoid, request.form.get('displayposition'))
    # TODO is it correct to make another read from the database to get the
    # updated data, or should we just assume that the updated data is there?
    return get_photo(photoid)


@app.route('/photos/<int:photoid>', methods=['DELETE'])
def delete_photo(photoid):
    """Ajax function which deletes the photo with the specified ID number from
    the database, and returns a boolean representing whether the action was
    successful.

    """
    require_logged_in()
    g.db.execute(Q_DELETE_PHOTO.format(photoid))
    g.db.commit()
    return make_response(None, 204)
