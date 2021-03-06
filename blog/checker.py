from werkzeug.security import check_password_hash
from blog.db import get_db
import re


def check_user_exists():
    if get_db().execute('SELECT userid FROM user').fetchone() is None:
        return False
    return True


def check_category_exists():
    db = get_db()

    # If there's no category, create default category named "Uncategorized"
    if db.execute('SELECT id FROM category').fetchone() is None:
        db.execute(
            'INSERT INTO category (name, slug, c_order, c_default) VALUES (?, ?, ?, ?)',
            ('Uncategorized', 'uncategorized', 1, 1)
        )
        db.commit()


def check_setting_exists():
    db = get_db()

    # If there's no setting values, create and insert default values
    if db.execute('SELECT * FROM setting').fetchone() is None:
        db.execute(
            'INSERT INTO setting DEFAULT VALUES;'
        )
        db.execute(
            'UPDATE setting SET blog_about_title = ?, blog_about_body = ?', (
                "About this blog",
                "This is the page where you can post and open your own profile! "
                "If you're logged in, click 'edit' button to create your own profile :)"
            )
        )
        db.commit()


def check_post_exists(userid):
    db = get_db()

    # If there's no post after new userid and category have created, create default one
    if db.execute('SELECT id FROM post').fetchone() is None:
        user = db.execute('SELECT id FROM user WHERE userid = ?', (userid,)).fetchone()
        category = db.execute('SELECT id FROM category WHERE name = ?', ('Uncategorized',)).fetchone()

        # If the default category ('Uncategorized') doesn't exists, choose the oldest category
        if category is None:
            category = db.execute('SELECT id FROM category ORDER BY id').fetchone()
        db.execute(
            'INSERT INTO post (user_id, category_id, title, slug, body) VALUES (?, ?, ?, ?, ?)',
            (user['id'], category['id'], 'Hello, world!', 'hello-world',
             "Thank you for using tiny-blogger! "
             "If you're logged in, click 'Admin' > 'New Post' to create your own posts :)")
        )
        db.commit()


def check_slug_valid(slug):
    restricted_pattern = re.compile(
        r'/\.|@|:|\/|\?|#|\[|\]|!|\$|&|\(|\)|\*|\+|,|;|=|\\|%|<|>|\||\^|~|"|\{|\}|`|???|???|(\s)|(_)|[???-??????-???]|(-)\1+|^[-]|[-]$|[A-Z]')
    apostrophe_pattern = re.compile(r"'")
    if restricted_pattern.search(slug) or apostrophe_pattern.search(slug) or len(slug) > 200:
        return False
    return True


def check_post_slug_not_duplicated(post_id, slug):
    db = get_db()
    count = db.execute(
        'SELECT id, slug FROM post WHERE slug = ?',
        (slug,)
    ).fetchone()
    if count is None or count['id'] == post_id:
        return True
    return False


def check_category_slug_not_duplicated(slug, category_id=None):
    db = get_db()
    count = db.execute(
        'SELECT id, slug FROM category WHERE slug = ?',
        (slug,)
    ).fetchone()
    if count is None or count['id'] == category_id:
        return True
    return False


def check_category_name_not_duplicated(name, category_id=None):
    db = get_db()
    count = db.execute(
        'SELECT id, name FROM category WHERE name = ?',
        (name,)
    ).fetchone()
    if count is None or count['id'] == category_id:
        return True
    return False


def check_category_id_exists(category_id):
    db = get_db()
    category = db.execute(
        'SELECT id, name FROM category WHERE id = ?',
        (category_id,)
    ).fetchone()
    if category is None:
        return False
    return True


def check_input_valid(title, slug, body, post_id, category_id):
    error = None
    if not title:
        error = 'Title is required. (Up to 100 characters)'
    elif not slug:
        error = 'Post URL Slug is required. (Up to 200 characters)'
    elif not check_slug_valid(slug):
        error = 'Blank spaces, special chars except hyphen(-) are not allowed for Post URL slug. (Up to 200 characters)'
    elif not check_category_id_exists(category_id):
        error = 'Valid category must be selected.'
    elif not check_post_slug_not_duplicated(post_id, slug):
        error = 'Post URL Slug is duplicated.'
    elif not body:
        error = 'Body is required.'
    return error


def check_about_input_valid(title, body):
    error = None
    if not title:
        error = 'Title is required. (Up to 100 characters)'
    elif not body:
        error = 'Body is required.'
    return error


def check_settings_valid(values):
    error = None
    if not values['blog_title'] or len(values['blog_title']) < 1 or len(values['blog_title']) > 50:
        error = 'Title is required. (Up to 50 characters)'
    elif not values['posts_per_page'] or values['posts_per_page'] < 1 or values['posts_per_page'] > 20:
        error = 'Correct number of \'Posts per page\' is required. (Between 1 to 20)'
    elif not values['pagination_size'] or values['pagination_size'] < 3 or values['pagination_size'] > 10:
        error = 'Correct number of \'Pagination size\' is required. (Between 3 to 10)'
    return error


def check_account_username_valid(username):
    error = None
    if not username or len(username) < 1 or len(username) > 32:
        error = 'Correct number of characters of Username is required. (Up to 32 characters)'
    return error


def check_account_password_valid(user_id, values):
    error = None
    db = get_db()
    user = db.execute(
        'SELECT * FROM user WHERE id = ?', (user_id,)
    ).fetchone()

    if not values['pw_current'] or not check_password_hash(user['password'], values['pw_current']):
        error = 'Current password is incorrect.'
    elif not values['pw_new'] or len(values['pw_new']) < 8 or len(values['pw_new']) > 128:
        error = 'Password must have between 8 to 128 characters.'
    elif not values['pw_new_confirm'] or len(values['pw_new_confirm']) < 8 or len(values['pw_new_confirm']) > 128 \
            or values['pw_new'] != values['pw_new_confirm']:
        error = 'Both passwords (New, Confirm) must be matched.'
    return error


def check_account_registration_valid(values):
    error = None

    if not values['blog_title'] or len(values['blog_title']) < 1 or len(values['blog_title']) > 50:
        error = 'Your blog title is required. (Up to 50 characters)'
    elif not values['userid'] or len(values['userid']) < 4 or len(values['userid']) > 32:
        error = 'User ID must have between 4 to 32 characters.'
    elif not (values['userid'].isalnum() and values['userid'].islower()):
        error = 'Only lowercase alphanumeric characters are allowed for User ID.'
    elif not values['username']:
        error = 'Username is required.'
    elif not values['password'] or len(values['password']) < 8 or len(values['password']) > 128:
        error = 'Password must have between 8 to 128 characters.'
    elif not values['password_confirm'] or len(values['password_confirm']) < 8 or \
            len(values['password_confirm']) > 128 or values['password'] != values['password_confirm']:
        error = 'Both passwords (New, Confirm) must be matched.'
    return error


def check_category_valid(name, slug, category_id=None):
    error = None

    if not name or len(name) < 1 or len(name) > 32:
        error = 'Category name is required. (Up to 32 characters)'
    elif not slug or len(slug) < 1 or len(name) > 32:
        error = 'Category slug is required. (Up to 32 characters)'
    elif not check_category_name_not_duplicated(name, category_id):
        error = 'Category name must not be duplicated.'
    elif not check_category_slug_not_duplicated(slug, category_id):
        error = 'Category slug must not be duplicated.'
    elif slug == 'admin' or slug == 'auth' or slug == 'about' or slug == 'create':
        error = 'Using preserved slug is not allowed. (admin, auth, about, create)'
    elif not check_slug_valid(slug):
        error = 'Blank spaces, special chars except hyphen(-) are not allowed for category slug.'
    return error


def check_category_ids_valid(category_ids):
    error = None
    db = get_db()

    if hasattr(category_ids, '__iter__'):
        for category_id in category_ids:
            if db.execute('SELECT id FROM category WHERE id = ?', (category_id,)).fetchone() is None:
                error = 'Some information of category is not valid. Please try again.'
                break

    else:
        if db.execute('SELECT id FROM category WHERE id = ?', (category_ids,)).fetchone() is None:
            error = 'Some information of category is not valid. Please try again.'

    return error
