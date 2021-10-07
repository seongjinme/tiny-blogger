from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from blog.auth import login_required
from blog.db import get_db
from blog.checker import (
    check_input_error, check_user_exists, check_category_exists
)
from blog.getter import (
    get_post, get_category, get_category_list, get_pagination_ranges, get_posts_per_page, get_posts_per_page_by_search
)
from blog.sanitize import sanitize_html
import re


bp = Blueprint('blog', __name__)


@bp.route('/', methods=('GET',))
def index():
    # If there's no registered user, redirect to register page
    if not check_user_exists():
        return redirect(url_for('auth.register'))

    # Check if there's at least one category
    # check_category_exists()

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

    # Set the rest variables for rendering index with default values
    alarm_type = 'light'
    pages = p['pages']
    p_num_start = p['pagination_num_start']
    p_num_end = p['pagination_num_end']
    posts_truncate = p['posts_truncate']
    error = None

    # Render index
    # Case 1 : If there's a query keyword, render index with a search result
    if query is not None and query != '':

        query_string = '%' + query + '%'

        # Case 1-1 : If there's a result, check current page number
        if p['row_count'] > 0:

            # Case 1-1-1 : If there's a result and current page number is correct
            if 1 <= page <= p['pages']:
                posts = get_posts_per_page_by_search(query_string, p['offset'], p['posts_per_page'])

            # Case 1-1-2 : If there's a result but current page number is out of range
            else:
                posts = get_posts_per_page_by_search(query_string, 0, p['posts_per_page'])
                page = 1
                error = f'Page number is out of range with search keyword : {query}'

        # Case 1-2 : If there's no result, ignore given page number and render index with a message
        else:
            posts = get_posts_per_page(p['offset'], p['posts_per_page'])
            query = None
            page = 1
            error = f'Theres no search results with keyword : {query}'

    # Case 2 : If there's a 'blank' query, ignore query & page number, and render index with a message
    elif query is not None and query == '':
        posts = get_posts_per_page(p['offset'], p['posts_per_page'])
        query = None
        page = 1
        error = "Search with blank spaces and blank keyword is not supported."

    # Case 3 : In case if there's no query
    else:

        # Case 3-1 : If there's at least 1 or more posts, start rendering index
        if p['row_count'] > 0:

            # Case 3-1-1 : If there's a page number and it's correct, render index as usual
            if 1 <= page <= p['pages']:
                posts = get_posts_per_page(p['offset'], p['posts_per_page'])

            # Case 3-1-2 : If there's a page number but it's out of range
            else:
                posts = get_posts_per_page(0, p['posts_per_page'])
                page = 1
                error = "Page number is out of range."

        # Case 3-2 : If there's no post at all, render an alarm message only
        else:
            error = "There is no post yet. Why don't you start blogging now? :)"
            posts = None
            page = 1

    if error:
        flash(error)
    return render_template('blog/index.html',
                           posts=posts, query=query, alarm_type=alarm_type, page=page, pages=pages,
                           p_num_start=p_num_start, p_num_end=p_num_end, posts_truncate=posts_truncate)


@bp.route('/<string:slug>/')
def view_post(slug):
    post = get_post(slug, False)
    return render_template('blog/post.html', post=post)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        slug = request.form['slug']
        category_id = request.form['category']
        body = sanitize_html(request.form['body'])

        error = check_input_error(title, slug, body, None, category_id)

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, slug, body, user_id, category_id)'
                ' VALUES (?, ?, ?, ?, ?)',
                (title, slug, body, g.user['id'], category_id)
            )
            db.commit()
            flash('Your post has successfully updated!')
            return redirect(url_for('blog.index'))

    categories = get_category_list()
    return render_template('blog/create.html', alarm_type='danger', categories=categories)


@bp.route('/<string:slug>/edit', methods=('GET', 'POST'))
@login_required
def edit(slug):
    post = get_post(slug)
    category = get_category(post['id'])
    categories = get_category_list(post['category_id'])

    if request.method == 'POST':
        slug_before = slug

        title = request.form['title']
        slug = request.form['slug']
        body = request.form['body']
        post_id = post['id']
        category_id = request.form['category']

        error = check_input_error(title, slug, body, post_id, category_id)

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, slug = ?, category_id = ?, body = ?'
                ' WHERE slug = ?',
                (title, slug, category_id, body, slug_before)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/edit.html', post=post, alarm_type='danger', category=category, categories=categories)


@bp.route('/<string:slug>/delete', methods=('POST',))
@login_required
def delete(slug):
    get_post(slug)
    db = get_db()
    db.execute('DELETE FROM post WHERE slug = ?', (slug,))
    db.commit()
    return redirect(url_for('blog.index'))
