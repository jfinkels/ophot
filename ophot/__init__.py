# imports from built-in modules
from collections import OrderedDict
from contextlib import closing
import sqlite3

# imports from third party modules
from configobj import ConfigObj
from flask import Flask
from flask import g

# create the application and get app configuration from config.py, or a file
app = Flask('ophot')
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

# add some loggers for errors and warnings
if not app.debug:
    from logging import ERROR
    from logging import WARNING
    from logging import FileHandler
    from logging import Formatter
    from logging.handlers import SMTPHandler
    mail_handler = SMTPHandler('127.0.0.1',
                               'server-error@{0}'.format(app.config['DOMAIN_NAME']),
                               app.config['ERROR_MAIL_RECIPIENTS'],
                               app.config['ERROR_MAIL_SUBJECT'])
    mail_handler.setFormatter(Formatter('''
Message type:       %(levelname)s
Location:           %(pathname)s:%(lineno)d
Module:             %(module)s
Function:           %(funcName)s
Time:               %(asctime)s

Message:

%(message)s
'''))
    # email us if something goes really wrong
    mail_handler.setLevel(ERROR)
    app.logger.addHandler(mail_handler)
    # write to a file on warnings
    file_handler = FileHandler(app.config['LOGFILE'])
    file_handler.setFormatter(Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'
            ))
    file_handler.setLevel(WARNING)
    app.logger.addHandler(file_handler)


def _add_new_category(categoryname):
    """Creates a new category in the database with the specified *categoryname*
    and returns its ID number.

    """
    g.db.execute('insert into category (categoryname) values (?)',
                 [categoryname])
    g.db.commit()
    # get the ID of the category that we just inserted
    return g.db.execute('select categoryid from category where'
                        ' categoryname == "{0}"'.format(categoryname)).fetchone()[0]

def _get_categories():
    """Helper method which returns a map from category ID to category name,
    sorted in alphabetical (lexicographical) order by category name.

    """
    cursor = g.db.execute('select categoryid, categoryname from category'
                          ' order by categoryname asc')
    return OrderedDict([(row[0], row[1]) for row in cursor.fetchall()])

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
