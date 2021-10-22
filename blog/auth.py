import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from blog.db import get_db
from blog.checker import (
    check_category_exists, check_post_exists, check_setting_exists, check_account_registration_valid, check_user_exists
)
from blog.getter import get_blog_info

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        values = {
            'blog_title': request.form['blog_title'],
            'userid': request.form['userid'],
            'username': request.form['username'],
            'password': request.form['password'],
            'password_confirm': request.form['password_confirm']
        }
        db = get_db()

        # Validate input data
        error = check_account_registration_valid(values)

        # Insert input data to DB
        if error is not None:
            flash(error)

        else:
            try:
                db.execute(
                    'INSERT INTO user (userid, username, password) VALUES (?, ?, ?)',
                    (values['userid'], values['username'], generate_password_hash(values['password'])),
                )
                db.commit()

            # Check if userid is duplicated
            except db.IntegrityError:
                error = f"User ID {values['userid']} is already registered."

            # If registration is completed, redirect to login page
            else:

                # Check if there's any setting values, and insert default values
                check_setting_exists()

                # Check if there's any category exists, and create one if there isn't
                check_category_exists()

                # Check and create the first post
                check_post_exists(values['userid'])

                # Update blog title into db
                db.execute('UPDATE setting SET blog_title = ?', (values['blog_title'],))
                db.commit()

                flash('Your registration has successfully completed!')

                return redirect(url_for('auth.login'))

    # If registered user exists when someone accesses register page with 'GET' method, redirect to index
    if get_db().execute('SELECT userid FROM user').fetchone() is not None:
        error = 'Registered user account already exists.'
        flash(error)
        return redirect(url_for('blog.index'))

    return render_template('auth/register.html', alarm_type='danger')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    error = None
    # If there's no registered user, redirect to register page
    if not check_user_exists():
        return redirect(url_for('auth.register'))

    if session.get('user_id'):
        flash("You're already logged in!")
        return redirect(url_for('blog.index'))

    if request.method == 'POST':
        userid = request.form['userid']
        password = request.form['password']

        # Ensure userid and password is submitted
        if not userid:
            error = 'User ID is required.'
        elif not password:
            error = 'Password is required.'
        else:
            db = get_db()
            user = db.execute(
                'SELECT * FROM user WHERE userid = ?', (userid,)
            ).fetchone()

            # Validate userid and password
            if user is None or not check_password_hash(user['password'], password):
                error = 'User id or password is incorrect.'

            # If validation is completed, clear current session and start new session
            if error is None:
                session.clear()
                session['user_id'] = user['id']
                return redirect(url_for('index'))

        # Store error message
        flash(error)

    if error:
        return render_template('auth/login.html', blog_info=get_blog_info(), alarm_type='danger')

    return render_template('auth/login.html', blog_info=get_blog_info(), alarm_type='success')


# Check user info of current session before view function in blog
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
