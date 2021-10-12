from blog.db import get_db
from flask import g
from werkzeug.exceptions import abort


def get_post(slug, check_author=True):
    post = get_db().execute(
        'SELECT p.id, slug, title, body, created, user_id, username, category_id'
        ' FROM post p JOIN user u ON p.user_id = u.id'
        ' WHERE slug = ?',
        (slug,)
    ).fetchone()

    if post is None:
        abort(404, f"Post doesn't exist.")

    if check_author and post['user_id'] != g.user['id']:
        abort(403)

    return post


def get_category_list(category_id=None):
    if category_id is None:
        c_id = 'NULL'
    else:
        c_id = int(category_id)

    category_list = get_db().execute(
        'SELECT id, name FROM category WHERE id != ?',
        (c_id,)
    )

    if category_list is None:
        abort(403, "There's no category to get.")

    return category_list


def get_category(post_id):
    category = get_db().execute(
        'SELECT c.id, name'
        ' FROM category c JOIN post p ON c.id = p.category_id'
        ' WHERE p.id = ?',
        (post_id,)
    ).fetchone()

    if category is None:
        abort(403, f"Category for this post doesn't exist.")

    return category


def get_row_count(query=None):
    if query is not None:
        query = '%' + query + '%'
        rows = get_db().execute(
            'SELECT COUNT(p.id) row_count'
            ' FROM post p'
            ' WHERE title LIKE ? OR body LIKE ?',
            (query, query,)
        ).fetchone()
    else:
        rows = get_db().execute(
            'SELECT COUNT(p.id) row_count'
            ' FROM post p',
        ).fetchone()

    return rows['row_count']


def get_pagination_ranges(page=None, query=None):
    # Set variables for pagination
    db = get_db()
    values = db.execute(
        'SELECT posts_per_page, pagination_size, posts_truncate'
        ' FROM setting'
    ).fetchone()
    posts_per_page = values['posts_per_page']  # default: 3, min: 1, max: 10
    pagination_size = values['pagination_size']  # default: 5, min: 3, max: 10
    posts_truncate = True if values['pagination_size'] == 1 else False  # default: True

    # Ensure page is higher than 0
    page = 1 if page is None or page <= 1 else page

    # Get page info and post counts to initiate pagination
    row_count = get_row_count(query)
    offset = (page - 1) * posts_per_page if (page - 1) >= 0 else 0
    pages = (row_count // posts_per_page) + 1 if row_count % posts_per_page else row_count // posts_per_page

    # Ensure page is lower than total pages
    page = 1 if page > pages else page

    # Calculate pagination ranges
    pagination_range = pagination_size // 2
    if page > (pagination_range + 1):
        if page <= pages - pagination_range:
            pagination_num_start = page - pagination_range
            pagination_num_end = page + pagination_range - 1 if pagination_size % 2 == 0 else page + pagination_range
        else:
            pagination_num_start = pages - pagination_size + 1 if pages - pagination_size + 1 > 0 else 1
            pagination_num_end = pages
    else:
        pagination_num_start = 1
        pagination_num_end = pages if pages < pagination_size else pagination_size

    return {
        'offset': offset,
        'row_count': row_count,
        'pages': pages,
        'posts_per_page': posts_per_page,
        'pagination_size': pagination_size,
        'pagination_num_start': pagination_num_start,
        'pagination_num_end': pagination_num_end,
        'posts_truncate': posts_truncate
    }


def get_posts_per_page_by_search(query_string, offset, per_page):
    db = get_db()
    return db.execute(
        'SELECT p.id, title, slug, body, created, user_id, username'
        ' FROM post p JOIN user u ON p.user_id = u.id'
        ' WHERE title LIKE ? OR body LIKE ?'
        ' ORDER BY created DESC'
        ' LIMIT ?, ?',
        (query_string, query_string, offset, per_page,)
    ).fetchall()


def get_posts_per_page(offset, per_page):
    db = get_db()
    return db.execute(
        'SELECT p.id, title, slug, body, created, user_id, username'
        ' FROM post p JOIN user u ON p.user_id = u.id'
        ' ORDER BY created DESC'
        ' LIMIT ?, ?',
        (offset, per_page,)
    ).fetchall()
