from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from blog.auth import login_required
from blog.db import get_db
from blog.checker import (
    check_input_valid, check_user_exists, check_category_exists, check_setting_exists, check_about_input_valid
)
from blog.getter import (
    get_blog_info, get_post, get_category_by_post_id, get_category_by_slug, get_default_category,
    get_category_list, get_pagination_ranges, get_posts_per_page, get_posts_per_page_by_search,
    get_about
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
    check_category_exists()

    # Check if there are valid setting values
    check_setting_exists()

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
            p = get_pagination_ranges(1)
            pages = p['pages']
            p_num_start = p['pagination_num_start']
            p_num_end = p['pagination_num_end']
            posts_truncate = p['posts_truncate']

            posts = get_posts_per_page(p['offset'], p['posts_per_page'])
            query_keyword = query
            query = None
            page = 1
            flash(f'Theres no search results with keyword : {query_keyword}')

    # Case 2 : If there's a 'blank' query, ignore query & page number, and render index with a message
    elif query is not None and query == '':
        posts = get_posts_per_page(p['offset'], p['posts_per_page'])
        query = None
        page = 1
        flash("Search with blank spaces and blank keyword is not allowed.")

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

        # Case 3-2 : If there's no post at all, render an message
        else:
            flash("There is no post yet. Why don't you start blogging now? :)")
            posts = None
            page = 1

    if error:
        flash(error)
        return render_template('blog/index.html', blog_info=get_blog_info(), categories=get_category_list(),
                               posts=posts, query=query, page=page, pages=pages, alarm_type='danger',
                               p_num_start=p_num_start, p_num_end=p_num_end, posts_truncate=posts_truncate)

    return render_template('blog/index.html', blog_info=get_blog_info(), categories=get_category_list(),
                           posts=posts, query=query, page=page, pages=pages,
                           p_num_start=p_num_start, p_num_end=p_num_end, posts_truncate=posts_truncate)


@bp.route('/<string:category_slug>/', methods=('GET',))
def index_category(category_slug):
    # If there's no registered user, redirect to register page
    if not check_user_exists():
        return redirect(url_for('auth.register'))

    # Check if there's at least one category
    check_category_exists()

    # Check if there are valid setting values
    check_setting_exists()

    error = None

    if get_db().execute('SELECT id FROM category WHERE slug = ?', (category_slug,)).fetchone() is None:
        error = 'URL path is invalid.'
        flash(error)
        return redirect(url_for('blog.index'))

    # Get query keywords and strip
    query = request.args.get('q')
    if query:
        query = re.sub(r'(-)\1+', '-', query)
        query = re.sub(r'(\s)\1+', ' ', query)
        query = query.strip()

    # Get page info to initiate pagination
    page = request.args.get('p', 1, type=int)
    p = get_pagination_ranges(page, None, category_slug)

    # Set the rest variables for rendering index with default values
    pages = p['pages']
    p_num_start = p['pagination_num_start']
    p_num_end = p['pagination_num_end']
    posts_truncate = p['posts_truncate']

    # If there's a query, redirect to index and run searching
    if query is not None:
        return redirect(url_for('blog.index', q=query))

    # Start rendering index_category
    # Case 1 : If there's at least 1 or more posts, start rendering index
    if p['row_count'] > 0:

        # Case 1-1 : If there's a page number and it's correct, render index as usual
        if 1 <= page <= p['pages']:
            posts = get_posts_per_page(p['offset'], p['posts_per_page'], category_slug)

        # Case 1-2 : If there's a page number but it's out of range
        else:
            posts = get_posts_per_page(0, p['posts_per_page'], category_slug)
            page = 1
            error = "Page number is out of range."

    # Case 2 : If there's no post at all, render an message
    else:
        flash("There is no post with this category yet. Why don't you start blogging now? :)")
        posts = None
        page = 1

    if error:
        flash(error)
        return render_template('blog/index.html', blog_info=get_blog_info(), categories=get_category_list(),
                               posts=posts, query=query, page=page, pages=pages, alarm_type='danger',
                               p_num_start=p_num_start, p_num_end=p_num_end, posts_truncate=posts_truncate,
                               index_category=get_category_by_slug(category_slug), index_category_slug=category_slug)

    return render_template('blog/index.html', blog_info=get_blog_info(), categories=get_category_list(),
                           posts=posts, query=query, page=page, pages=pages,
                           p_num_start=p_num_start, p_num_end=p_num_end, posts_truncate=posts_truncate,
                           index_category=get_category_by_slug(category_slug), index_category_slug=category_slug)


@bp.route('/<string:category_slug>/<string:slug>/')
def view_post(category_slug, slug):
    post = get_post(slug, False)
    return render_template('blog/post.html', blog_info=get_blog_info(), post=post,
                           categories=get_category_list())


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        slug = request.form['slug']
        category_id = request.form['category']
        body = sanitize_html(request.form['body'])

        error = check_input_valid(title, slug, body, None, category_id)

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

    return render_template('blog/create.html', blog_info=get_blog_info(), alarm_type='danger',
                           default_category=get_default_category(), categories=get_category_list())


@bp.route('/<string:category_slug>/<string:slug>/edit', methods=('GET', 'POST'))
@login_required
def edit(category_slug, slug):
    post = get_post(slug)

    if request.method == 'POST':
        slug_before = slug

        title = request.form['title']
        slug = request.form['slug']
        body = request.form['body']
        post_id = post['id']
        category_id = request.form['category']

        error = check_input_valid(title, slug, body, post_id, category_id)

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
            flash('Your post has successfully updated!')
            return redirect(url_for('blog.index'))

    return render_template('blog/edit.html', blog_info=get_blog_info(), post=post, alarm_type='danger',
                           category=get_category_by_post_id(post['id']), categories=get_category_list())


@bp.route('/<string:category_slug>/<string:slug>/delete', methods=('POST',))
@login_required
def delete(category_slug, slug):
    get_post(slug)
    db = get_db()
    db.execute('DELETE FROM post WHERE slug = ?', (slug,))
    db.commit()
    flash('Your post has successfully deleted!')
    return redirect(url_for('blog.index'))


@bp.route('/about')
def about():
    post = get_about()
    return render_template('blog/about.html', blog_info=get_blog_info(), post=post,
                           categories=get_category_list())


@bp.route('/about/edit', methods=('GET', 'POST'))
@login_required
def edit_about():
    post = get_about()

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']

        error = check_about_input_valid(title, body)
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE setting SET blog_about_title = ?, blog_about_body = ?',
                (title, body)
            )
            db.commit()
            flash("Your 'About' page has successfully updated!")
            return redirect(url_for('blog.about'))

    return render_template('blog/edit_about.html', blog_info=get_blog_info(), post=post, alarm_type='danger')
