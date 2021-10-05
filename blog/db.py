import sqlite3
import click
from flask import current_app, g
from flask.cli import with_appcontext


def get_db():
    # establishes a connection to the file pointed at by 'DATABASE'
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()

    with current_app.open_resource('db.sql') as db_schema:
        db.executescript(db_schema.read().decode('utf8'))


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Database has initialized!')


def init_app(app):
    # Run close_db() after returning response from app
    app.teardown_appcontext(close_db)

    # add init_db_command to as a new flask command that can be called
    app.cli.add_command(init_db_command)
