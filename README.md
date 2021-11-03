# tiny-blogger

<div align="center"><img src="https://github.com/seongjinme/tiny-blogger/blob/master/docs/images/mockup.png" alt="tiny-blogger header img"></div>

**tiny-blogger** is a python web application for personal blogging based on the basic structure of [Flaskr](https://flask.palletsprojects.com/en/2.0.x/tutorial/index.html); an official tutorial project of [Flask](https://flask.palletsprojects.com/). As an extension of [Flaskr](https://flask.palletsprojects.com/en/2.0.x/tutorial/index.html), **tiny-blogger** provides many useful features for blogging with simple and yet convenient UI.

## Features

* Enhanced UI elements based on Bootstrap framework
* Straightforward writing experiences with WYSIWYG editor
* Fully automated URL slug generator for SEO optimization
* Supports post searching by keyword, pagination and post truncating
* One-step installation & initialization using Docker image

**tiny-blogger** is still in development. More updates will come later:
* Supporting Facebook, Disqus comments plug-in
* Managing posts in Admin section

## Installation

This description is written on the premise of Linux environment with Python 3.8.

### The Basic Way

1. Clone the repository to your directory
```shell
$ git clone https://github.com/seongjinme/tiny-blogger.git
```

2. Move to your 'tiny-blogger' directory and create virtual environment
```shell
$ cd tiny-blogger
$ apt-get install python3-venv
$ python3 -m venv venv
```

3. Initiate virtual environment
```shell
$ source venv/bin/activate
```

4. Install requisite libraries included in requirements.txt
```shell
$ pip install -r requirements.txt
```

5. Set variables to initiate the blog
```shell
# If you want a development/debug mode, set "FLASK_ENV=development" instead.
# Please notice the db will be separated following the running environment.
$ export FLASK_APP=blog
$ export FLASK_ENV=production
```
6. Run Flask
```shell
$ python -m flask run -h 0.0.0.0
```

Now you can access to your blog via `http://127.0.0.1:5000`.

### With Docker Engine

If you’re using Docker Engine, you can download and run **tiny-blogger** container with just a single line of command.

#### Background mode

```shell
$ docker run -d -p 80:5000 —name tiny-blogger seongjinme/tiny-blogger:1.0
```

#### Foreground mode with tty
```shell
$ docker run -it -p 80:5000 —name tiny-blogger seongjinme/tiny-blogger:1.0
```

That’s it! Now you can access to your blog via `http://[VM_INTERNAL_IP:5000]` or `http://[VM_EXTERNAL_IP]`.

## Dependencies

* Python 3.8
* Flask 2.0.2
* jQuery 3.6.0
* jQuery UI 1.13.0
* Bootstrap 4.6.0
* Bleach 4.1.0
* Summernote 0.8.18

## Note

This web application is made for the final project of [CS50x](https://cs50.harvard.edu/x/2021/), which is the online course of an introduction for computer science and programming provided by Harvard University and edX.
