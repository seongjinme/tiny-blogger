from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from blog.auth import login_required
from blog.db import get_db
from blog.sanitize import sanitize_html
import re
# import bleach


bp = Blueprint('blog', __name__)


def get_post(slug, check_author=True):
    post = get_db().execute(
        'SELECT p.id, slug, title, body, created, user_id, username'
        ' FROM post p JOIN user u ON p.user_id = u.id'
        ' WHERE slug = ?',
        (slug,)
    ).fetchone()

    if post is None:
        abort(404, f"Post doesn't exist.")

    if check_author and post['user_id'] != g.user['id']:
        abort(403)

    return post


def get_category(post_id):
    category = get_db().execute(
        'SELECT c.id, name'
        ' FROM category c JOIN post p ON c.post_id = p.id'
        ' WHERE p.id = ?',
        (post_id,)
    ).fetchone()

    if category is None:
        abort(403, f"Category id for post id {post_id} doesn't exist.")

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
        print(rows)
    else:
        rows = get_db().execute(
            'SELECT COUNT(p.id) row_count'
            ' FROM post p',
        ).fetchone()

    return rows['row_count']


def get_pagination_ranges(page=None, query=None):
    # Set variables for pagination
    posts_per_page = 3  # default: 3, min: 1, max: 10
    pagination_size = 5  # default: 5, min: 3, max: 10
    posts_truncate = True  # default: True

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


@bp.route('/', methods=('GET',))
def index():
    # Get query keywords and strip
    query = request.args.get('q')
    if query:
        query = re.sub(r'(-)\1+', '-', query)
        query = re.sub(r'(\s)\1+', ' ', query)
        query = query.strip()

    # Get page info to initiate pagination
    page = request.args.get('p', 1, type=int)
    if query is not None or query != '':
        p = get_pagination_ranges(page, query)
    else:
        p = get_pagination_ranges(page)

    # Case 1 : If there's a query keyword, render index with a search result
    if query is not None and query != '':

        query_string = '%' + query + '%'

        # Case 1-1 : If there's a result, check current page number
        if p['row_count'] > 0:

            # Case 1-1-1 : If there's a result and current page number is correct
            if 1 <= page <= p['pages']:
                posts = get_posts_per_page_by_search(query_string, p['offset'], p['posts_per_page'])
                return render_template('blog/index.html',
                                       posts=posts, query=query, page=page, pages=p['pages'],
                                       p_num_start=p['pagination_num_start'], p_num_end=p['pagination_num_end'],
                                       posts_truncate=p['posts_truncate'])

            # Case 1-1-2 : If there's a result but current page number is out of range
            else:
                posts = get_posts_per_page_by_search(query_string, 0, p['posts_per_page'])
                error = f'Page number is out of range with search keyword : {query}'
                flash(error)
                return render_template('blog/index.html',
                                       posts=posts, query=query, alarm_type='light', page=1, pages=p['pages'],
                                       p_num_start=p['pagination_num_start'], p_num_end=p['pagination_num_end'],
                                       posts_truncate=p['posts_truncate'])

        # Case 1-2 : If there's no result, ignore given page number and render index with a message
        else:
            posts = get_posts_per_page(p['offset'], p['posts_per_page'])
            error = f'Theres no search results with keyword : {query}'
            flash(error)
            return render_template('blog/index.html',
                                   posts=posts, alarm_type='light', page=1, pages=p['pages'],
                                   p_num_start=p['pagination_num_start'], p_num_end=p['pagination_num_end'],
                                   posts_truncate=p['posts_truncate'])

    # Case 2 : If there's a 'blank' query, ignore query & page number, and render index with a message
    elif query is not None and query == '':
        posts = get_posts_per_page(p['offset'], p['posts_per_page'])
        error = f'Search with blank spaces and blank keyword is not supported.'
        flash(error)
        return render_template('blog/index.html',
                               posts=posts, alarm_type='light', page=1, pages=p['pages'],
                               p_num_start=p['pagination_num_start'], p_num_end=p['pagination_num_end'],
                               posts_truncate=p['posts_truncate'])

    # Case 3 : In case if there's no query
    else:

        # Case 3-1 : If there's at least 1 or more posts, start rendering index
        if p['row_count'] > 0:

            # Case 3-1-1 : If there's a page number and it's correct, render index as usual
            if 1 <= page <= p['pages']:
                posts = get_posts_per_page(p['offset'], p['posts_per_page'])
                return render_template('blog/index.html',
                                       posts=posts, page=page, pages=p['pages'],
                                       p_num_start=p['pagination_num_start'], p_num_end=p['pagination_num_end'],
                                       posts_truncate=p['posts_truncate'])

            # Case 3-1-2 : If there's a page number but it's out of range
            else:
                posts = get_posts_per_page(0, p['posts_per_page'])
                error = f'Page number is out of range.'
                flash(error)
                return render_template('blog/index.html',
                                       posts=posts, alarm_type='light', page=1, pages=p['pages'],
                                       p_num_start=p['pagination_num_start'], p_num_end=p['pagination_num_end'],
                                       posts_truncate=p['posts_truncate'])

        # Case 3-2 : If there's no post at all, render an alarm message only
        else:
            error = f'There is no post yet. Why don\'t you start blogging now? :)'
            flash(error)
            return render_template('blog/index.html',
                                   alarm_type='light', page=1, pages=p['pages'],
                                   p_num_start=p['pagination_num_start'], p_num_end=p['pagination_num_end'],
                                   posts_truncate=p['posts_truncate'])


@bp.route('/<string:slug>/')
def view_post(slug):
    post = get_post(slug, False)
    return render_template('blog/post.html', post=post)


def check_slug_valid(slug):
    restricted_pattern = re.compile(
        r'/\.|@|:|\/|\?|#|\[|\]|!|\$|&|\(|\)|\*|\+|,|;|=|\\|%|<|>|\||\^|~|"|\{|\}|`|–|—|(\s)|(_)|[ㄱ-ㅎㅏ-ㅣ]|(-)\1+|^[-]|[-]$|[A-Z]')
    apostrophe_pattern = re.compile(r"'")
    if restricted_pattern.search(slug) or apostrophe_pattern.search(slug) or len(slug) > 200:
        return False
    return True


def check_slug_duplicated(post_id, slug):
    db = get_db()
    count = db.execute(
        'SELECT id, slug FROM post WHERE slug = ?',
        (slug,)
    ).fetchone()
    if count is None or count['id'] == post_id:
        return True
    return False


def check_input_error(title, slug, body, post_id):
    error = None
    if not title:
        error = 'Title is required. (Up to 100 characters)'
    elif not slug:
        error = 'Post URL Slug is required. (Up to 200 characters)'
    elif not check_slug_valid(slug):
        error = 'Blank spaces, special chars except hyphen(-) are not allowed for Post URL slug. (Up to 200 characters)'
    elif post_id is not None:
        if not check_slug_duplicated(post_id, slug):
            error = 'Post URL Slug is duplicated.'
    elif not body:
        error = 'Body is required.'
    return error


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        slug = request.form['slug']
        body = sanitize_html(request.form['body'])

        error = check_input_error(title, slug, body, None)

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, slug, body, user_id)'
                ' VALUES (?, ?, ?, ?)',
                (title, slug, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')


@bp.route('/<string:slug>/edit', methods=('GET', 'POST'))
@login_required
def edit(slug):
    post = get_post(slug)

    if request.method == 'POST':
        slug_before = slug

        title = request.form['title']
        slug = request.form['slug']
        body = request.form['body']
        post_id = post['id']

        error = check_input_error(title, slug, body, post_id)

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, slug = ?, body = ?'
                ' WHERE slug = ?',
                (title, slug, body, slug_before)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/edit.html', post=post)


@bp.route('/<string:slug>/delete', methods=('POST',))
@login_required
def delete(slug):
    get_post(slug)
    db = get_db()
    db.execute('DELETE FROM post WHERE slug = ?', (slug,))
    db.commit()
    return redirect(url_for('blog.index'))
