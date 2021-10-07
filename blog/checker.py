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
            'INSERT INTO category (name, slug) VALUES (?, ?)',
            ('Uncategorized', 'uncategorized')
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
             "Thank you for using tiny-blogger! Click 'Admin' > 'New Post' to create your own posts :)")
        )
        db.commit()


def check_slug_valid(slug):
    restricted_pattern = re.compile(
        r'/\.|@|:|\/|\?|#|\[|\]|!|\$|&|\(|\)|\*|\+|,|;|=|\\|%|<|>|\||\^|~|"|\{|\}|`|–|—|(\s)|(_)|[ㄱ-ㅎㅏ-ㅣ]|(-)\1+|^[-]|[-]$|[A-Z]')
    apostrophe_pattern = re.compile(r"'")
    if restricted_pattern.search(slug) or apostrophe_pattern.search(slug) or len(slug) > 200:
        return False
    return True


def check_slug_not_duplicated(post_id, slug):
    db = get_db()
    count = db.execute(
        'SELECT id, slug FROM post WHERE slug = ?',
        (slug,)
    ).fetchone()
    if count is None or count['id'] == post_id:
        return True
    return False


def check_category_valid(category_id):
    db = get_db()
    category = db.execute(
        'SELECT id, name FROM category WHERE id = ?',
        (category_id,)
    ).fetchone()
    if category is None:
        return False
    return True


def check_input_error(title, slug, body, post_id, category_id):
    error = None
    if not title:
        error = 'Title is required. (Up to 100 characters)'
    elif not slug:
        error = 'Post URL Slug is required. (Up to 200 characters)'
    elif not check_slug_valid(slug):
        error = 'Blank spaces, special chars except hyphen(-) are not allowed for Post URL slug. (Up to 200 characters)'
    elif not check_category_valid(category_id):
        error = 'Valid category must be selected.'
    elif post_id is not None:
        if not check_slug_not_duplicated(post_id, slug):
            error = 'Post URL Slug is duplicated.'
    elif not body:
        error = 'Body is required.'
    return error
