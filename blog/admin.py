from flask import (
    Blueprint, flash, redirect, render_template, request, session, url_for
)
from werkzeug.security import generate_password_hash
from blog.auth import login_required
from blog.db import get_db
from blog.checker import (
    check_settings_valid, check_account_username_valid, check_account_password_valid,
    check_category_valid, check_category_ids_valid
)
from blog.getter import get_blog_info, get_category_list, get_default_category, get_row_count

bp = Blueprint('admin', __name__, url_prefix='/admin')


@bp.route('/settings', methods=('GET', 'POST'))
@login_required
def settings():
    error = None

    if request.method == 'POST':
        values = {
            'blog_title': request.form['blog_title'],
            'posts_per_page': int(request.form['posts_per_page']),
            'pagination_size': int(request.form['pagination_size'])
        }
        error = check_settings_valid(values)
        if error is not None:
            flash(error)
        else:
            posts_truncate = 1 if request.form.get('posts_truncate') == 'on' else 0

            db = get_db()
            db.execute(
                'UPDATE setting'
                ' SET blog_title = ?, posts_per_page = ?, pagination_size = ?, posts_truncate = ?',
                (values['blog_title'], values['posts_per_page'], values['pagination_size'], posts_truncate)
            )
            db.commit()
            flash('Settings have successfully changed!')
            return redirect(url_for('admin.settings'))

    values = get_db().execute(
        'SELECT blog_title, posts_per_page, pagination_size, posts_truncate, search_allow FROM setting'
    ).fetchone()

    if error:
        return render_template('admin/settings.html', blog_info=get_blog_info(), categories=get_category_list(),
                               alarm_type='danger', settings=values, current='settings')

    return render_template('admin/settings.html', blog_info=get_blog_info(), categories=get_category_list(),
                           alarm_type='success', settings=values, current='settings')


@bp.route('/account', methods=('GET', 'POST'))
@login_required
def account():
    error = None
    db = get_db()
    user_id = session.get('user_id')

    if request.method == 'POST':
        if 'username' in request.form:
            username = request.form['username']
            error = check_account_username_valid(username)
            if error is not None:
                flash(error)
            else:
                db.execute('UPDATE user SET username = ? WHERE id = ?', (username, user_id))
                db.commit()
                flash('Username has successfully changed!')
                return redirect(url_for('admin.account'))

        else:
            values = {
                'pw_current': request.form['pw_current'],
                'pw_new': request.form['pw_new'],
                'pw_new_confirm': request.form['pw_new_confirm']
            }
            error = check_account_password_valid(user_id, values)
            if error is not None:
                flash(error)
            else:
                password = request.form['pw_new']
                db.execute('UPDATE user SET password = ? WHERE id = ?', (generate_password_hash(password), user_id))
                db.commit()
                flash('Your password has successfully changed!')
                return redirect(url_for('admin.account'))

    values = db.execute('SELECT userid, username FROM user WHERE id = ?', (user_id,)).fetchone()

    if error:
        return render_template('admin/account.html', blog_info=get_blog_info(), categories=get_category_list(),
                               alarm_type='danger', account=values, current='account')

    return render_template('admin/account.html', blog_info=get_blog_info(), categories=get_category_list(),
                           alarm_type='success', account=values, current='account')


@bp.route('/categories', methods=('GET', 'POST'))
@login_required
def categories():
    error = None
    db = get_db()

    if request.method == 'POST':
        if 'select_default_category' in request.form:
            category_id = int(request.form['select_default_category'])
            error = check_category_ids_valid(category_id)
            if error is not None:
                flash(error)
            else:
                db.execute('UPDATE category SET c_default = 0')
                db.commit()
                db.execute('UPDATE category SET c_default = 1 WHERE id = ?', (category_id,))
                db.commit()
                flash('Default category has successfully saved!')
                return redirect(url_for('admin.categories'))

        elif 'create_category_name' in request.form:
            name = request.form['create_category_name']
            slug = request.form['create_category_slug']
            error = check_category_valid(name, slug)
            if error is not None:
                flash(error)
            else:
                c_order = db.execute('SELECT MAX(c_order) max FROM category').fetchone()
                db.execute(
                    'INSERT INTO category (name, slug, c_order, c_default)'
                    ' VALUES (?, ?, ?, ?)',
                    (name, slug, c_order['max'] + 1, 0)
                )
                db.commit()
                flash('New category has successfully created!')
                return redirect(url_for('admin.categories'))

        elif 'edit_category_id' in request.form:
            name = request.form['edit_category_name']
            slug = request.form['edit_category_slug']
            category_id = int(request.form['edit_category_id'])
            error = check_category_valid(name, slug, category_id)
            if error is not None:
                flash(error)
            else:
                db.execute(
                    'UPDATE category SET name = ?, slug = ?'
                    ' WHERE id = ?',
                    (name, slug, category_id)
                )
                db.commit()
                flash('Category has successfully edited!')
                return redirect(url_for('admin.categories'))

        elif 'delete_category_id' in request.form:
            category_lists = db.execute('SELECT COUNT(id) count FROM category').fetchone()
            category_id = int(request.form['delete_category_id'])
            category_name = request.form['delete_category_name']

            if category_lists['count'] <= 1:
                error = "There should be at least one category in the blog."
                flash(error)
            elif category_id == get_default_category()['id']:
                error = "Deleting default category is not allowed. Try after changing default category."
                flash(error)
            else:
                category_exists = db.execute(
                    'SELECT id, name FROM category'
                    ' WHERE id = ? AND name = ?', (category_id, category_name,)
                ).fetchone()
                if category_exists is None:
                    error = "There's no matching category information. Please try again."
                    flash(error)
                else:
                    rows = get_row_count(None, None, category_id)
                    if rows > 0:
                        db.execute(
                            'UPDATE post SET category_id = ? WHERE category_id = ?',
                            (get_default_category()['id'], category_id)
                        )
                    db.execute('DELETE FROM category WHERE id = ?', (category_id,))
                    db.commit()
                    flash(f"Category '{category_name}' has successfully deleted!")
                    return redirect(url_for('admin.categories'))

        elif 'sort_category_order' in request.form:
            c_ids = list(map(int, request.form['sort_category_order'].split(',')))

            error = check_category_ids_valid(c_ids)
            if error is not None:
                flash(error)
            else:
                db.execute('UPDATE category SET c_order = 0')
                db.commit()
                c_order = 1
                for c_id in c_ids:
                    db.execute('UPDATE category SET c_order = ? WHERE id = ?', (c_order, c_id))
                    db.commit()
                    c_order += 1
                flash('Category order has successfully changed!')
                return redirect(url_for('admin.categories'))

    if error:
        return render_template('admin/categories.html', blog_info=get_blog_info(), categories=get_category_list(),
                               default_category=get_default_category(), alarm_type='danger', current='categories')

    return render_template('admin/categories.html', blog_info=get_blog_info(), categories=get_category_list(),
                           default_category=get_default_category(), alarm_type='success', current='categories')
