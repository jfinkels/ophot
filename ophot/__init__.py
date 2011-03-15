# imports from built-in modules
from contextlib import closing
import sqlite3

# imports from third party modules
from configobj import ConfigObj
from flask import Flask
from flask import g

# create the application and get app configuration from config.py, or a file
app = Flask(__name__)
app.config.from_object('ophot.config')
app.config.from_envvar('OPHOT_SETTINGS', silent=True)

# site-wide configuration which is not necessary for running the app
site_config = ConfigObj(app.config['SETTINGS_FILE'])
if 'BIO' not in site_config:
    site_config['BIO'] = ''
if 'CONTACT' not in site_config:
    site_config['CONTACT'] = ''
if 'SPACING' not in site_config:
    site_config['SPACING'] = app.config['DEFAULT_PHOTO_SPACING']

def _get_categories():
    """Helper method which returns a map from category ID to category name,
    sorted in alphabetical (lexicographical) order by category name.

    """
    cursor = g.db.execute('select categoryid, categoryname from category'
                          ' order by categoryname asc')
    return dict([(row[0], row[1]) for row in cursor.fetchall()])

def _get_last_display_position(categoryid):
    """Helper method which returns the index in the display sequence of the
    last photo in the specified category.

    Might return None.

    """
    # sometimes returns None
    return g.db.execute('select max(photodisplayposition) from photo where'
                        ' photocategory == "{0}"'
                        .format(categoryid)).fetchone()[0]

def init_db():
    """Initialize the database using the schema specified in the configuration.

    """
    with closing(connect_db()) as db:
        with app.open_resource(app.config['SCHEMA']) as f:
            db.cursor().executescript(f.read())
        db.commit()

def connect_db():
    """Gets a connection to the SQLite database."""
    return sqlite3.connect(app.config['DATABASE'])

@app.before_request
def before_request():
    """Stores the database connection in the db attribute of the g object."""
    g.db = connect_db()

@app.after_request
def after_request(response):
    """Closes the database connection stored in the db attribute of the g
    object.

    The response to the request is returned unchanged.

    """
    g.db.close()
    return response

import ophot.requests
import ophot.views

if __name__ == '__main__':
    app.run()
