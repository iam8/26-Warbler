# Ioana A Mititean
# Unit 26: Warbler (Twitter Clone)

# TODO: implement url_for in templates!

"""
Warbler app - Flask setup and config, routes, and views.
"""

import os

from flask import Flask, url_for, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError

from forms import UserAddForm, LoginForm, MessageForm, UserEditForm
from models import db, connect_db, User, Message


CURR_USER_KEY = "curr_user"

app = Flask(__name__)

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///warbler'))

app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
toolbar = DebugToolbarExtension(app)


###################################################################################################
# User signup/login/logout

@app.before_request
def add_user_to_g():
    """
    If we're logged in, add curr user to Flask global.
    """

    if CURR_USER_KEY in session:
        g.user = db.session.get(User, session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """
    Log in user.
    """

    session[CURR_USER_KEY] = user.id


def do_logout():
    """
    Logout user.
    """

    if CURR_USER_KEY in session:
        session.pop(CURR_USER_KEY)


@app.route('/signup', methods=["GET", "POST"])
def signup():
    """
    Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If there already is a user with that username, flash message and re-present form.
    """

    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
                location=form.location.data or User.location.server_default.arg,
                image_url=form.image_url.data or User.image_url.server_default.arg,
            )
            db.session.commit()

        except IntegrityError:
            flash("Username or email already taken", 'danger')
            return render_template('users/signup.jinja2', form=form)

        do_login(user)

        return redirect(url_for("homepage"))

    else:
        return render_template('users/signup.jinja2', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """
    Handle user login.
    """

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data, form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect(url_for("homepage"))

        flash("Invalid credentials.", 'danger')

    return render_template('users/login.jinja2', form=form)


@app.route('/logout')
def logout():
    """
    Handle logout of user.
    """

    do_logout()

    flash("Successfully logged out!", category="success")
    return redirect(url_for("login"))


###################################################################################################
# General user routes:

@app.route('/users')
def list_users():
    """
    Page with listing of users.

    Can take a 'q' param in querystring to search by that username.
    """

    search = request.args.get('q')

    if not search:
        users = User.query.all()
    else:
        users = User.query.filter(User.username.like(f"%{search}%")).all()

    return render_template('users/index.jinja2', users=users)


@app.route('/users/<int:user_id>')
def users_show(user_id):
    """
    Show user profile.
    """

    user = db.get_or_404(User, user_id)

    # Snagging messages in order from the database; user.messages won't be in order by default
    messages = (Message
                .query
                .filter(Message.user_id == user_id)
                .order_by(Message.timestamp.desc())
                .limit(100)
                .all())

    return render_template('users/show.jinja2', user=user, messages=messages)


@app.route('/users/<int:user_id>/following')
def show_following(user_id):
    """
    Show list of people this user is following.
    """

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect(url_for("homepage"))

    user = db.get_or_404(User, user_id)
    return render_template('users/following.jinja2', user=user)


@app.route('/users/<int:user_id>/followers')
def show_followers(user_id):
    """
    Show list of followers of this user.
    """

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect(url_for("homepage"))

    user = db.get_or_404(User, user_id)
    return render_template('users/followers.jinja2', user=user)


@app.route("/users/<int:user_id>/likes")
def display_likes(user_id):
    """
    Display list of warbles (messages) this user likes.
    """

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect(url_for("homepage"))

    user = db.get_or_404(User, user_id)
    likes = user.likes
    return render_template("users/likes.jinja2", user=user, likes=likes)


@app.route('/users/follow/<int:follow_id>', methods=['POST'])
def add_follow(follow_id):
    """
    Add a follow for the currently-logged-in user.

    Users cannot follow themselves.
    """

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect(url_for("homepage"))

    if follow_id == g.user.id:
        flash("You cannot follow yourself!", "warning")
        return redirect(url_for("homepage"))

    followed_user = db.get_or_404(User, follow_id)
    g.user.following.append(followed_user)
    db.session.commit()

    return redirect(url_for("show_following", user_id=g.user.id))


@app.route('/users/stop_following/<int:follow_id>', methods=['POST'])
def stop_following(follow_id):
    """
    Have currently-logged-in-user stop following this user.
    """

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect(url_for("homepage"))

    followed_user = db.get_or_404(User, follow_id)

    try:
        g.user.following.remove(followed_user)
    except ValueError:
        db.session.rollback()
        return redirect(url_for("show_following", user_id=g.user.id))

    db.session.commit()

    return redirect(url_for("show_following", user_id=g.user.id))


@app.route("/users/add_like/<int:msg_id>", methods=["POST"])
def add_like(msg_id):
    """
    Like a message for the currently-logged-in user.

    Users cannot like their own messages.
    """

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect(url_for("homepage"))

    message = db.session.get(Message, msg_id)

    if message.user_id == g.user.id:
        flash("You cannot like your own messages!")
        return redirect(url_for("homepage"))

    g.user.likes.append(message)
    db.session.commit()

    return redirect(url_for("display_likes", user_id=g.user.id))


@app.route("/users/remove_like/<int:msg_id>", methods=["POST"])
def remove_like(msg_id):
    """
    Remove the currently-logged-in user's like on a message.
    """

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect(url_for("homepage"))

    message = db.session.get(Message, msg_id)

    try:
        g.user.likes.remove(message)
    except ValueError:
        db.session.rollback()
        return redirect(url_for("display_likes", user_id=g.user.id))

    db.session.commit()

    return redirect(url_for("display_likes", user_id=g.user.id))


@app.route('/users/profile', methods=["GET", "POST"])
def profile():
    """
    Update profile for current user.
    """

    # Check if user is logged in
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect(url_for("homepage"))

    user = g.user
    form = UserEditForm(obj=user)

    if form.validate_on_submit():

        # Check if password is correct
        if not User.authenticate(user.username, form.password.data):
            flash("Password incorrect.", category="danger")
            return redirect(url_for("homepage"))

        user.username = form.username.data
        user.email = form.email.data
        user.image_url = form.image_url.data or User.image_url.server_default.arg
        user.header_image_url = (form.header_image_url.data or
                                 User.header_image_url.server_default.arg)
        user.bio = form.bio.data or None
        user.location = form.location.data or None

        # Handle case where username or email is already taken
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash("Username or email already taken", 'danger')
            return render_template("/users/edit.jinja2", form=form)

        flash("User updated!", category="success")
        return redirect(url_for("users_show", user_id=user.id))

    return render_template("/users/edit.jinja2", form=form)


@app.route('/users/delete', methods=["POST"])
def delete_user():
    """
    Delete user.
    """

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect(url_for("homepage"))

    do_logout()

    db.session.delete(g.user)
    db.session.commit()

    return redirect(url_for("signup"))


###################################################################################################
# Messages routes:

@app.route('/messages/new', methods=["GET", "POST"])
def messages_add():
    """
    Add a message:

    Show form if GET. If valid, update message and redirect to user page.
    """

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect(url_for("homepage"))

    form = MessageForm()

    if form.validate_on_submit():
        msg = Message(text=form.text.data)
        g.user.messages.append(msg)
        db.session.commit()

        return redirect(url_for("users_show", user_id=g.user.id))

    return render_template('messages/new.jinja2', form=form)


@app.route('/messages/<int:message_id>', methods=["GET"])
def messages_show(message_id):
    """
    Show a message.
    """

    msg = db.session.get(Message, message_id)
    return render_template('messages/show.jinja2', message=msg)


@app.route('/messages/<int:message_id>/delete', methods=["POST"])
def messages_destroy(message_id):
    """
    Delete a message.
    """

    msg = db.session.get(Message, message_id)

    if not g.user or g.user is not msg.user:
        flash("Access unauthorized.", "danger")
        return redirect(url_for("homepage"))

    db.session.delete(msg)
    db.session.commit()

    return redirect(url_for("users_show", user_id=g.user.id))


###################################################################################################
# Homepage and error pages

@app.route('/')
def homepage():
    """
    Show homepage:

    - anon users: no messages
    - logged in: 100 most recent messages of followed_users
    """

    if g.user:
        following = [f.id for f in g.user.following]
        messages = (Message
                    .query
                    .filter((Message.user == g.user) | (Message.user_id.in_(following)))
                    .order_by(Message.timestamp.desc())
                    .limit(100)
                    .all())
        likes = g.user.likes

        return render_template('home.jinja2', messages=messages, likes=likes)

    else:
        return render_template('home-anon.jinja2')


###################################################################################################
# Turn off all caching in Flask
#   (useful for dev; in production, this kind of stuff is typically
#   handled elsewhere)
#
# https://stackoverflow.com/questions/34066804/disabling-caching-in-flask

@app.after_request
def add_header(req):
    """
    Add non-caching headers on every request.
    """

    req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    req.headers["Pragma"] = "no-cache"
    req.headers["Expires"] = "0"
    req.headers['Cache-Control'] = 'public, max-age=0'
    return req


###################################################################################################
# MAIN

if __name__ == "__main__":

    connect_db(app)

    with app.app_context():
        db.create_all()

    app.run(host='127.0.0.1', port=5000, debug=True, threaded=False)
