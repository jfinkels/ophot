"""Provides routes for ajax requests to the server."""
# imports from third-party modules
from flask import g
from flask import jsonify
from flask import request

# imports from this application
from ophot import add_new_category
from ophot import get_categories
from ophot import get_last_display_position
from ophot import select_single
from ophot import app
from ophot import require_logged_in
from ophot import site_config
from ophot.queries import Q_CHANGE_CATEGORY
from ophot.queries import Q_CHANGE_CATEGORY_NAME
from ophot.queries import Q_CHANGE_DISPLAY_POS
from ophot.queries import Q_DELETE_CATEGORY
from ophot.queries import Q_DELETE_PHOTO
from ophot.queries import Q_GET_PHOTO_POS
from ophot.queries import Q_GET_PHOTOS


@app.route('/_add_category', methods=['GET'])
def add_category():
    """Ajax function which adds a new category to the database.

    Request argument is *categoryname*, a string which is the name of the
    category to add.

    """
    require_logged_in()
    categoryname = request.args.get('categoryname')
    categoryid = add_new_category(categoryname)
    return jsonify(added=True, categoryid=categoryid,
                   categoryname=categoryname)


@app.route('/_change_category', methods=['GET'])
def change_category():
    """Ajax function which changes the category of a photo.

    Request arguments are *photoid*, an integer which is the ID of the photo to
    change, and *categoryid*, an integer which is the ID of the category to
    which the photo will be moved. If *categoryid* is equal to -1, this
    function will check for the *categoryname* request argument, create the
    category with that name, and move the photo with the specified ID to that
    category.

    Returns a JSON object mapping *changed* to a boolean representing whether
    the category was successfully changed, *photoid* to the ID of the photo,
    and *categoryid* to the ID of the category.

    If the photo is being changed to the same category, this function will
    change its display order position to be last.
    """
    require_logged_in()
    categoryid = request.args.get('categoryid')
    if int(categoryid) == -1:
        categoryname = request.args.get('categoryname')
        if categoryname is None or len(categoryname) == 0:
            return jsonify(changed=False, photoid=photoid,
                           categoryid=categoryid, reason='No name received.')
        categoryid = add_new_category(categoryname)
    photoid = request.args.get('photoid')
    position = get_last_display_position(categoryid)
    if position is None:
        position = 1
    g.db.execute(Q_CHANGE_CATEGORY.format(categoryid, position, photoid))
    g.db.commit()
    return jsonify(changed=True, photoid=photoid, categoryid=categoryid)


@app.route('/_change_category_name', methods=['GET'])
def change_category_name():
    """Ajax function which updates the name of the category with the specified
    ID number to the specified new name.

    Request arguments are *categoryid*, an integer which is the ID of the
    category whose name will be changed, and *categoryname*, the new name for
    the category.

    Returns a JSON object mapping *changed* to a boolean representing whether
    the category was successfully changed, *categoryid* to the ID of the
    category, and *categoryname* to the new name of the category.
    """
    require_logged_in()
    categoryid = request.args.get('categoryid')
    categoryname = request.args.get('categoryname')
    g.db.execute(Q_CHANGE_CATEGORY_NAME.format(categoryname, categoryid))

    g.db.commit()
    return jsonify(changed=True)


# TODO POST method doesn't seem to be working
@app.route('/_change_spacing', methods=['GET'])
def change_spacing():
    """Ajax function which changes the value of the spacing between photos on
    the photo display page.

    The only request argument is *spacing*, the number of pixels between
    photos.

    Returns a JSON object mapping *changed* to a boolean representing whether
    the spacing was successfully changed.

    """
    require_logged_in()
    # TODO use a validator for configobj
    site_config['SPACING'] = int(request.args.get('spacing'))
    site_config.write()
    return jsonify(changed=True)


@app.route('/delete_category/<int:categoryid>', methods=['DELETE'])
def delete_category(categoryid):
    """Ajax function which deletes the category with the specified ID number
    from the database, and returns a boolean representing whether the action
    was successful.

    All photos with that category will no longer be accessible.

    """
    # TODO what should we do with photos orphaned by this deletion? perhaps
    # create a page for managing photo thumbnails by dragging and dropping them
    # onto categories...
    require_logged_in()
    g.db.execute(Q_DELETE_CATEGORY.format(categoryid))
    g.db.commit()
    return jsonify(deleted=True, categoryid=categoryid)


@app.route('/delete/<int:photoid>', methods=['DELETE'])
def delete_photo(photoid):
    """Ajax function which deletes the photo with the specified ID number from
    the database, and returns a boolean representing whether the action was
    successful.

    """
    require_logged_in()
    g.db.execute(Q_DELETE_PHOTO.format(photoid))
    g.db.commit()
    return jsonify(deleted=True, photoid=photoid)


@app.route('/_get_categories', methods=['GET'])
def get_categories():
    """Ajax function which returns a JSON object storing an array of categories
    in alphabetical (lexicographical) order.

    """
    return jsonify(get_categories().iteritems())


@app.route('/_get_photos', methods=['GET'])
def get_photos():
    """Ajax function which returns a JSON object which is a map from photoid to
    filenames of photos in the category specified in the request argument
    *categoryid*.

    Returns a JSON object which is a mapping from the string "values" to an
    array in which each element is a mapping containing the keys "photoid" and
    "filename". For example:

    { "values":
      [
        { "photoid": 5, "filename": /path/to/photo5 },
        { "photoid": 2, "filename": /path/to/photo2 },
        ...
      ]
    }

    The elements of the array are in ascending order according to photo display
    position.
    """
    category = request.args.get('categoryid')
    cursor = g.db.execute(Q_GET_PHOTOS.format(category))
    # Add the / so that the filenames are relative to the root of the app.
    photos = [dict(photoid=row[0], filename='/' + row[1]) for row in
              cursor.fetchall()]
    # NOTE: we have to do this funny business of creating an array of mappings
    # because JSON does not guarantee ordered mappings. The workaround is to
    # provide this array in order, sorted by photo display position, which is
    # what's happening in the lines above.
    return jsonify(values=photos)


@app.route('/_swap_display_positions', methods=['GET'])
def swap_display_positions():
    """Ajax function which swaps the display positions of two photos.

    The request arguments are *photoid1* and *photoid2*, the ID numbers of the
    photos whose display positions will be swapped.

    Returns a JSON object mapping *moved* to a boolean representing whether the
    swap was successful, *photoid1* to the ID number of the first photo
    swapped, *photoid2* to the ID number of the second photo swapped,
    *displayposition1* to the NEW display position of photo 1, and
    *displayposition2* to the NEW displayposition of photo 2.
    """
    photoid1 = request.args.get('photoid1')
    photoid2 = request.args.get('photoid2')
    pos1 = select_single(Q_GET_PHOTO_POS.format(photoid1))
    pos2 = select_single(Q_GET_PHOTO_POS.format(photoid2))
    g.db.execute(Q_CHANGE_DISPLAY_POS.format(pos2, photoid1))
    g.db.execute(Q_CHANGE_DISPLAY_POS.format(pos1, photoid2))
    g.db.commit()
    return jsonify(moved=True, photoid1=photoid1, displayposition1=pos2,
                   photoid2=photoid2, displayposition2=pos1)


@app.route('/_update_personal', methods=['GET'])
def update_personal():
    """Ajax function which changes either bio information or contact
    information.

    The request arguments are *name*, which must be either "bio" or "contact",
    and *value* which is the new value for the personal information.

    Returns a JSON object mapping *changed* to a boolean representing whether
    the info was successfully changed.

    """
    require_logged_in()
    name = request.args.get('name').upper()
    value = request.args.get('value')
    if name == 'BIO' or name == 'CONTACT':
        site_config[name] = value
        site_config.write()
    else:
        # TODO log this as an error
        pass
    return jsonify(changed=True)
