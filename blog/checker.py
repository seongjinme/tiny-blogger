from db import get_db
import re


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
