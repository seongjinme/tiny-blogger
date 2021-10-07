import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from blog.db import get_db
from blog.checker import check_category_exists, check_post_exists

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        userid = request.form['userid']
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        # Validate input data
        if not userid:
            error = 'User ID is required.'
        elif not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        # Insert input data to DB
        if error is None:
            try:
                db.execute(
                    'INSERT INTO user (userid, username, password) VALUES (?, ?, ?)',
                    (userid, username, generate_password_hash(password)),
                )
                db.commit()

            # Check if userid is duplicated
            except db.IntegrityError:
                error = f'User ID {userid} is already registered.'

            # If registration is completed, redirect to login page
            else:

                # Check if there's any category exists, and create one if there isn't
                check_category_exists()

                # Check and create the first post
                check_post_exists(userid)

                return redirect(url_for('auth.login'))

        # Store error message
        flash(error)

    # If registered user exists when someone accesses register page with 'GET' method, redirect to index
    if get_db().execute('SELECT userid FROM user').fetchone() is not None:
        error = 'Registered user account already exists.'
        flash(error)
        return redirect(url_for("blog.index"))

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if session.get('user_id'):
        flash("You're already logged in!")
        return redirect(url_for('blog.index'))

    if request.method == 'POST':
        userid = request.form['userid']
        password = request.form['password']
        error = None

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
        return render_template('auth/login.html', alarm_type='light')

    return render_template('auth/login.html')


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
