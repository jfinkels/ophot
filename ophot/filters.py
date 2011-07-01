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
"""Provides custom filters for Jinja templates."""
# imports for compatibility with future python versions
from __future__ import absolute_import
from __future__ import division

# imports from built-in modules
import re

# imports from third-party modules
from jinja2 import evalcontextfilter
from jinja2 import Markup

# imports from this application
from .app import app

# a regular expression which matches email addresses, from
# http://www.regular-expressions.info/email.html
EMAILS = re.compile(r'\b([A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4})\b', re.I)

@app.template_filter()
@evalcontextfilter
def link_emails(eval_context, data):
    """Replaces email addresses in the specified *data* string with HTML mailto
    links.

    """
    result = EMAILS.sub(r'<a href="mailto:\1">\1</a>', data)
    if eval_context.autoescape:
        result = Markup(result)
    return result
