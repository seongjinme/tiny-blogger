import os
from flask import Flask


def create_app(test_config=None):
    # create app instance
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        # set SECRET_KEY='dev' for dev mode only
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'blog.sqlite')
    )

    if test_config is None:
        # read the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)

    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Initialize the database
    from . import db
    db.init_app(app)
    with app.app_context():
        db.init_db()

    # Import/register 'auth' blueprint to initialize authentication
    from . import auth
    app.register_blueprint(auth.bp)

    # Import/register 'admin' blueprint
    from . import admin
    app.register_blueprint(admin.bp)

    # Import/register 'blog' blueprint
    from . import blog
    app.register_blueprint(blog.bp)
    # Setting 'blog' as the main index
    app.add_url_rule('/', endpoint='index')

    return app
