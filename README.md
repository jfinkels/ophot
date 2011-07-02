Ophot - a photography portfolio web application
===============================================

Introduction
------------

This is ophot, a small web application which provides a simple photography
portfolio website. It allows a manager to log in in order to add, edit or
remove photos.

This README was last updated on 1 July 2011.

Copyright license
-----------------

The code comprising this web application is copyright 2011 Jeffrey Finkelstein,
and is published under the GNU Affero General Public License, either version 3
or (at your option) any later version. For more information see the LICENSE
file.

Contents
--------

This package contains:

* LICENSE - the copyright license under which this program is distributed to
    you (the GNU Affero General Public License version 3 or later)
* ophot/ - the Python package containing the application itself
* ophot.wsgi - the WSGI specification file which runs the application when
    deployed to a server as a WSGI application
* README - this file
* reset-db.sh - script which resets the database to an initial empty state
    (warning: this will remove any photos which have been uploaded to the
    application)
* runserver.py - Python script which runs the Ophot Flask application in the
    current directory
* setup.py - Python setuptools configuration file for packaging this
    application
* TODO - tasks to be done for developers of this application

The ophot/ directory is a Python package and contains the following files:

* __init__.py - the file which makes this directory a Python package
* _rest.py - common functionality for the photos, categories, and user REST
    modules
* app.py - module containing the Flask application object
* categories.py - provides RESTful routes for accessing categories
* config.py - configuration for the application and some settings for
    user-visible parts of the site
* filters.py - filters for use with the Jinja2 templates in the templates/
    directory
* helpers.py - utility functions for use throught this package
* photos.py - provides RESTful routes for accessing photos
* queries.py - string constants which are used in queries to the database
* schema.sql - the schema for the photo database
* views.py - functions which process routes which are the views for users of
    the site

and the following subdirectories:

* static/ - the static content for the site, including scripts and styles
* templates/ - the Jinja2 templates defining the dynamically generated HTML
    pages for the site
* tests/ - the unit tests for the Python code in this package


Installing
----------

This application requires Python 2.7 (http://www.python.org/).

This application requires the following libraries to be installed:

* [ConfigObj](http://www.voidspace.org.uk/python/configobj.html)
* [Flask](http://flask.pocoo.org)
* [Flask-Uploads](http://packages.python.org/Flask-Uploads)
* [Flask-WTF](http://packages.python.org/Flask-WTF)
* [Python Imaging Library (PIL)](http://www.pythonware.com/products/pil)

Using "pip" or "easy_install" is probably the easiest way to install these:

    pip install Flask Flask-Uploads Flask-WTF PIL configobj

Building as a Python egg
------------------------

This package can be built, installed, etc. as a Python egg using the provided
setup.py script. For more information, run

    python setup.py --help

Configuring
-----------

To configure this application, edit the configuration file "config.py". You
must add at least USERNAME, PASSWORD, and SECRET_KEY for allowing the
administrator to log in. You probably want to change the value of NAME, plus
some others as well.

Instead of editing the configuration file directly, you can set the
OPHOT_SETTINGS environment variable to be the path to a file containing the
configuration settings which you wish to override. For example, create a text
file called "myconfig" and add the following:

    USERNAME = 'myusername'
    PASSWORD = 'mypassword'
    SECRET_KEY = '123456789012345678901234'

(See the config.py file for more information on how to generate a secret key.)
Next change the OPHOT_SETTINGS environment variable to point to that file:

    export OPHOT_SETTINGS=/path/to/myconfig

Place the above command at the bottom of the file $HOME/.bash_profile in order
to set that environment variable on every login:

    echo OPHOT_SETTINGS=/path/to/myconfig >> $HOME/.bash_profile

Running
-------

Before running the application we also need to initialize the database. The
reset-db.sh script will create the database for you based on the schema in the
schema.sql file:

    ./reset-db.sh

To run the web server and start serving, run:

    python runserver.py

Remember to disable debug mode when running on a production server.

One can also deploy this application as a WSGI application, using, for example,
mod_wsgi for Apache. To deploy this application as a WSGI application, edit the
first two lines in the ophot.wsgi file from

    PATH_TO_APP = '/var/www/ophot'
    PATH_TO_VIRTUALENV = PATH_TO_APP + '/env/bin/activate_this.py'

to be the correct paths to the top level directory of the application and the
virtualenv environment in which the application should run, respectively.

Testing
-------

The Python unit tests are contained in the ophot/tests/ directory (which is a
Python package). To run the test suite, run the command

    python setup.py test

Contact
-------

Jeffrey Finkelstein <jeffrey.finkelstein@gmail.com>
