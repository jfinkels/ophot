"""Provides query strings for queries to the database."""

Q_ADD_CATEGORY = 'insert into category (categoryname) values (?)'
Q_CHANGE_CATEGORY = ('update photo'
                     ' set photocategory={0},photodisplayposition={1}'
                     ' where photoid={2}')
Q_CHANGE_CATEGORY_NAME = ('update category set categoryname="{0}"',
                          ' where categoryid={1}')
Q_CHANGE_DISPLAY_POS = ('update photo set photodisplayposition={0}'
                        ' where photoid == {1}')
Q_DELETE_CATEGORY = 'delete from category where categoryid == {0}'
Q_DELETE_PHOTO = 'delete from photo where photoid == {0}'
Q_GET_CATEGORY = 'select categoryid from category where categoryname == "{0}"'
Q_GET_CATEGORIES = ('select categoryid, categoryname from category order by'
                    ' categoryname asc')
Q_GET_LAST_DISP_POS = ('select max(photodisplayposition) from photo'
                       ' where photocategory == "{0}"')
Q_GET_PHOTO_POS = ('select photodisplayposition from photo'
                   ' where photoid == {0}')
Q_GET_PHOTOS = ('select photoid, photofilename from photo'
                ' where photocategory == "{0}"'
                ' order by photodisplayposition asc')
