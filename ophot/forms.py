"""
Provides Flask-WTF Form classes for use in creating routes which allow the user
to submit information to the application.

"""
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
