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
"""
Provides Flask-WTF Form classes for use in creating routes which allow the user
to submit information to the application.

"""
# imports for compatibility with future python versions
from __future__ import absolute_import
from __future__ import division

# imports from third-party modules
#from flaskext.uploads import UploadSet
#from flaskext.uploads import IMAGES
from flaskext.wtf import FileField
from flaskext.wtf import Form
from flaskext.wtf import TextAreaField
from flaskext.wtf.html5 import IntegerField
#from flaskext.wtf.file import file_allowed
from flaskext.wtf.file import file_required
from wtforms.validators import NumberRange


class SettingsForm(Form):
    """Class which represents the settings form."""
    spacing = IntegerField('Space between photos (in pixels)', validators=[NumberRange(min=0, message='Must be a positive number.')])
    bio = TextAreaField('Bio')
    contact = TextAreaField('Contact info')


#splash_photos = UploadSet('images', IMAGES)
class ChangeSplashPhotoForm(Form):
    """Class which represents the form with which the user can change the
    splash photo.

    """
    # also want to add "file_allowed(splash_photos, 'Images only.')" here
    photo = FileField('Select new splash photo', validators=[file_required()])
