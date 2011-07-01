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
"""Creates the Flask application object which represents the Ophot application
and provides the user settings.

"""
# imports for compatibility with future python versions
from __future__ import absolute_import
from __future__ import division

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
if 'PURCHASE' not in site_config:
    site_config['PURCHASE'] = ''

# add some loggers for errors and warnings
if not app.debug:
    from logging import ERROR
    from logging import WARNING
    from logging import FileHandler
    from logging import Formatter
    from logging.handlers import SMTPHandler
    sender_address = 'server-error@{0}'.format(app.config['DOMAIN_NAME'])
    mail_handler = SMTPHandler('127.0.0.1', sender_address,
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
            '%(asctime)s %(levelname)s: %(message)s'
            ' [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(WARNING)
    app.logger.addHandler(file_handler)

