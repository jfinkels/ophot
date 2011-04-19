# imports from third-party modules
from flask import abort
from flask import g
from flask import jsonify
from flask import request
from flask import session

# imports from this application
from ophot import _get_categories
from ophot import _get_last_display_position
from ophot import app
from ophot import site_config

@app.route('/_get_photos', methods=['GET'])
def get_photos():
    """Ajax method which returns a JSON object which is a map from photoid to
    filenames of photos in the category specified in the request argument
    *categoryid*.

    """
    category = request.args.get('categoryid')
    cursor = g.db.execute('select photoid, photofilename from photo'
                          ' where photocategory == "{0}"'
                          ' order by photodisplayposition asc'
                          .format(category))
    # add the / so that the filenames are relative to the root of the app
    photos = dict([(row[0], '/' + row[1]) for row in cursor.fetchall()])
    return jsonify(photos)

@app.route('/_change_category', methods=['GET'])
def change_category():
    """Ajax method which changes the category of a photo.

    Request arguments are *photoid*, an integer which is the ID of the photo to
    change, and *categoryid*, an integer which is the ID of the category to
    which the photo will be moved. If *categoryid* is equal to -1, this method
    will check for the *categoryname* request argument, create the category
    with that name, and move the photo with the specified ID to that category.

    Returns a JSON object mapping *changed* to a boolean representing whether
    the category was successfully changed, *photoid* to the ID of the photo,
    and *categoryid* to the ID of the category.

    If the photo is being changed to the same category, this method will change
    its display order position to be last.
    """
    if not session.get('logged_in'):
        abort(401)
    categoryid = request.args.get('categoryid')
    if int(categoryid) == -1:
        categoryname = request.args.get('categoryname')
        if categoryname is None or len(categoryname) == 0:
            return jsonify(changed=False, photoid=photoid,
                           categoryid=categoryid, reason='No name received.')
        categoryid = _add_new_category(categoryname)
    photoid = request.args.get('photoid')
    position = _get_last_display_position(categoryid)
    if position is None:
        position = 1
    g.db.execute('update photo set photocategory={0},photodisplayposition={1}'
                 ' where photoid={2}'.format(categoryid, position, photoid))
    g.db.commit()
    return jsonify(changed=True, photoid=photoid, categoryid=categoryid)

@app.route('/_get_categories', methods=['GET'])
def get_categories():
    """Ajax method which returns a JSON object storing an array of categories
    in alphabetical (lexicographical) order.

    """
    return jsonify(_get_categories().iteritems())


@app.route('/_change_category_name', methods=['GET'])
def change_category_name():
    """Ajax method which updates the name of the category with the specified ID
    number to the specified new name.

    Request arguments are *categoryid*, an integer which is the ID of the
    category whose name will be changed, and *categoryname*, the new name for
    the category.

    Returns a JSON object mapping *changed* to a boolean representing whether
    the category was successfully changed, *categoryid* to the ID of the
    category, and *categoryname* to the new name of the category.
    """
    # TODO move these two lines into a function
    if not session.get('logged_in'):
        abort(401)
    categoryid = request.args.get('categoryid')
    categoryname = request.args.get('categoryname')
    g.db.execute('update category set categoryname="{0}" where categoryid={1}'
                 .format(categoryname, categoryid))

    g.db.commit()
    return jsonify(changed=True)

@app.route('/_update_personal', methods=['GET'])
def update_personal():
    """Ajax method which changes either bio information or contact information.

    The request arguments are *name*, which must be either "bio" or "contact",
    and *value* which is the new value for the personal information.

    Returns a JSON object mapping *changed* to a boolean representing whether
    the info was successfully changed.

    """
    if not session.get('logged_in'):
        abort(401)
    name = request.args.get('name').upper()
    value = request.args.get('value')
    if name == 'BIO' or name == 'CONTACT':
        site_config[name] = value
        site_config.write()
    else:
        # TODO log this as an error
        pass
    return jsonify(changed=True)

# TODO POST method doesn't seem to be working
@app.route('/_change_spacing', methods=['GET'])
def change_spacing():
    """Ajax method which changes the value of the spacing between photos on the
    photo display page.

    The only request argument is *spacing*, the number of pixels between
    photos.

    Returns a JSON object mapping *changed* to a boolean representing whether
    the spacing was successfully changed.

    """
    if not session.get('logged_in'):
        abort(401)
    # TODO use a validator for configobj
    site_config['SPACING'] = int(request.args.get('spacing'))
    site_config.write()
    return jsonify(changed=True)

@app.route('/delete/<int:photoid>', methods=['DELETE'])
def delete_photo(photoid):
    """Ajax method which deletes the photo with the specified ID number from
    the database, and returns a boolean representing whether the action was
    successful.

    """
    if not session.get('logged_in'):
        abort(401)
    g.db.execute('delete from photo where photoid == {0}'.format(photoid))
    g.db.commit()
    return jsonify(deleted=True, photoid=photoid)

@app.route('/delete_category/<int:categoryid>', methods=['DELETE'])
def delete_category(categoryid):
    """Ajax method which deletes the category with the specified ID number from
    the database, and returns a boolean representing whether the action was
    successful.

    All photos with that category will no longer be accessible.

    """
    # TODO what should we do with photos orphaned by this deletion? perhaps
    # create a page for managing photo thumbnails by dragging and dropping them
    # onto categories...
    if not session.get('logged_in'):
        abort(401)
    g.db.execute('delete from category where categoryid == {0}'
                 .format(categoryid))
    g.db.commit()
    return jsonify(deleted=True, categoryid=categoryid)
