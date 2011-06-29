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
"""Provides query strings for queries to the database."""
Q_ADD_CATEGORY = 'insert into category (categoryname) values (?)'
Q_ADD_PHOTO = ('insert into photo (photofilename, photocategory,'
               ' photodisplayposition) values (?, ?, ?)')
Q_DELETE_CATEGORY = 'delete from category where categoryid == {0}'
Q_DELETE_PHOTO = 'delete from photo where photoid == {0}'
Q_GET_CATEGORY = 'select categoryid from category where categoryname == "{0}"'
Q_GET_CATEGORY_BY_ID = 'select * from category where categoryid == {0}'
Q_GET_CATEGORY_BY_NAME = 'select * from category where categoryname == "{0}"'
Q_GET_CATEGORIES = ('select categoryid, categoryname from category order by'
                    ' categoryname asc')
Q_GET_LAST_DISP_POS = ('select max(photodisplayposition) from photo'
                       ' where photocategory == "{0}"')
Q_GET_PHOTO = 'select * from photo where photoid == {0}'
Q_GET_PHOTO_BY_DISPLAYPOS = ('select photoid from photo'
                             ' where photodisplayposition={0}')
Q_GET_PHOTO_DISPLAYPOS = ('select photodisplayposition from photo'
                          ' where photoid == {0}')
Q_GET_PHOTOS = 'select * from photo'
Q_GET_PHOTOS_BY_CAT = ('select photoid, photofilename from photo'
                       ' where photocategory == "{0}"'
                       ' order by photodisplayposition asc')
Q_UPDATE_CATEGORY_NAME = ('update category set categoryname="{0}"'
                          ' where categoryid={1}')
Q_UPDATE_PHOTO_CATEGORY = ('update photo'
                           ' set photocategory={0},photodisplayposition={1}'
                           ' where photoid={2}')
Q_UPDATE_PHOTO_DISPLAYPOS = ('update photo set photodisplayposition={0}'
                             ' where photoid == {1}')
