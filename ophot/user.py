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
"""Provides REST/JSON routes for editing user settings."""
# imports for compatibility with future python versions
from __future__ import absolute_import
from __future__ import division

# imports from third-party modules
from flask import jsonify
from flask import request

# imports from this application
from ophot import app
from ophot import require_logged_in
from ophot import site_config


@app.route('/user', methods=['GET'])
def get_user_settings():
    """Returns the user settings (bio, contact, and spacing between photos).

    The JSON response is::
        {
            "bio": "All about me...",
            "contact": "123 Example St.,\nExample City, EX 99999",
            "spacing": 10
        }
    """
    return jsonify(bio=site_config['BIO'], contact=site_config['CONTACT'],
                   spacing=site_config['SPACING'])


#@app.route('/user', methods=['PATCH'])
@app.route('/user', methods=['POST'])
def update_user_settings():
    """Updates the user settings.

    The request arguments are all optional. The arguments are *bio*, a string
    containing the bio information of the user, *contact*, a string containing
    the contact information of the user, and *spacing*, an integer which is the
    spacing in pixels between photos displayed on the splash page.

    For example, if the request is::
        {
            "bio": "Foo bar",
            "spacing": 20
        }

    then the JSON response will be::
        {
            "bio": "Foo bar",
            "contact": "123 Example St.,\nExample City, EX 99999",
            "spacing": 20
        }
    """
    require_logged_in()
    if 'bio' in request.args:
        site_config['BIO'] = request.args.get('bio')
    if 'contact' in request.args:
        site_config['CONTACT'] = request.args.get('contact')
    if 'spacing' in request.args:
        # TODO use a validator for configobj
        site_config['SPACING'] = int(request.args.get('spacing'))
    site_config.write()
    return get_user_settings()
