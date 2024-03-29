# Ioana A Mititean
# Unit 26: Warbler (Twitter Clone)

"""
SQLAlchemy models for Warbler.
"""

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()


class Follow(db.Model):
    """
    Connection of a follower <-> followed_user.

    One user can follow multiple users, and one user can be followed by multiple others.
    """

    __tablename__ = 'follows'

    user_being_followed_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade"),
        primary_key=True,
    )

    user_following_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade"),
        primary_key=True,
    )


class Like(db.Model):
    """
    Mapping user likes to warbles (messages).

    One user can have many liked messages, and one message can be liked by many users.
    """

    __tablename__ = 'likes'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='cascade')
    )

    message_id = db.Column(
        db.Integer,
        db.ForeignKey('messages.id', ondelete='cascade'),
        unique=True
    )


class User(db.Model):
    """
    User in the system.
    """

    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    email = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    username = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    image_url = db.Column(
        db.Text,
        server_default="/static/images/default-pic.png",
    )

    header_image_url = db.Column(
        db.Text,
        server_default="/static/images/warbler-hero.jpg"
    )

    bio = db.Column(
        db.Text,
    )

    location = db.Column(
        db.Text,
        server_default="Planet Earth"
    )

    password = db.Column(
        db.Text,
        nullable=False,
    )

    messages = db.relationship('Message', back_populates="user")

    followers = db.relationship(
        "User",
        secondary="follows",
        back_populates="following",
        primaryjoin=(Follow.user_being_followed_id == id),
        secondaryjoin=(Follow.user_following_id == id)
    )

    following = db.relationship(
        "User",
        secondary="follows",
        back_populates="followers",
        primaryjoin=(Follow.user_following_id == id),
        secondaryjoin=(Follow.user_being_followed_id == id)
    )

    likes = db.relationship(
        'Message',
        secondary="likes"
    )

    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.email}>"

    def is_followed_by(self, other_user):
        """
        Is this user followed by `other_user`?
        """

        found_user_list = [user for user in self.followers if user == other_user]
        return len(found_user_list) == 1

    def is_following(self, other_user):
        """
        Is this user following `other_user`?
        """

        found_user_list = [user for user in self.following if user == other_user]
        return len(found_user_list) == 1

    @classmethod
    def signup(cls, username, email, password, image_url, location):
        """
        Sign up user.

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_pwd,
            image_url=image_url,
            location=location
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """
        Find user with `username` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False


class Message(db.Model):
    """
    An individual message ("warble").

    Each message can have only one user, and each user can have many messages.
    """

    __tablename__ = 'messages'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    text = db.Column(
        db.String(140),
        nullable=False,
    )

    timestamp = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.now(),
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
    )

    user = db.relationship('User', back_populates="messages")

    def __repr__(self):
        """
        Return a string representation of a Message, which includes Message ID and the ID of the
        user associated with that message,
        """

        return f"<Message #{self.id}: User #{self.user_id}>"


def connect_db(app):
    """
    Connect this database to provided Flask app.
    """

    db.app = app
    db.init_app(app)
