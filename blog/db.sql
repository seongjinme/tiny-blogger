CREATE TABLE IF NOT EXISTS user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    userid TEXT UNIQUE NOT NULL,
    username TEXT NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS post (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    body TEXT NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user (id),
    FOREIGN KEY (category_id) REFERENCES category (id)
);

CREATE TABLE IF NOT EXISTS category (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    c_order INTEGER NOT NULL,
    c_default INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS setting (
    blog_title TEXT DEFAULT 'tiny-blogger',
    blog_about_title TEXT,
    blog_about_body TEXT,
    search_allow INTEGER NOT NULL DEFAULT 1,
    posts_per_page INTEGER NOT NULL DEFAULT 3,
    posts_truncate INTEGER NOT NULL DEFAULT 1,
    pagination_size INTEGER NOT NULL DEFAULT 5,
    cmt_allow TEXT NOT NULL DEFAULT 'Off',
    cmt_facebook_appid TEXT,
    cmt_facebook_count INTEGER,
    cmt_facebook_color TEXT,
    cmt_disqus_shortname TEXT
)