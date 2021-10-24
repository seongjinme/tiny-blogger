import os
from flask import Flask
from instance.config import *


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        if os.environ.get('FLASK_ENV') == 'production':
            app.config.from_object(ProductionConfig)
        elif os.environ.get('FLASK_ENV') == 'development':
            app.config.from_object(DevelopmentConfig)

    else:
        app.config.from_object(TestingConfig)

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
