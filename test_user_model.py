# Ioana A Mititean
# Unit 26: Warbler (Twitter Clone)

"""
User model tests for Warbler.
"""

from unittest import TestCase
from sqlalchemy.exc import IntegrityError
from flask_bcrypt import Bcrypt

from app import app
from models import db, connect_db, User, Message, Follow

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///warbler_test"
app.config['SQLALCHEMY_ECHO'] = False

app.config['TESTING'] = True
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

bcrypt = Bcrypt()

connect_db(app)

with app.app_context():
    db.drop_all()
    db.create_all()


class UserModelTestCase(TestCase):
    """
    Test User model.
    """

    def setUp(self):
        """
        Create test client; empty tables of data.
        """

        with app.app_context():
            User.query.delete()
            Message.query.delete()
            Follow.query.delete()

            user0 = User(
                email="test@test.com",
                username="testuser",
                password="HASHED_PASSWORD"
            )

            db.session.add(user0)
            db.session.commit()

            self.user0_id = user0.id

        self.client = app.test_client()
        return super().setUp()

    def tearDown(self) -> None:
        """
        Clean up any fouled transaction.
        """

        with app.app_context():
            db.session.rollback()

        return super().tearDown()

    def test_user_model(self):
        """
        Does basic model work?
        """

        user1 = User(
            email="test1@test.com",
            username="testuser1",
            password="HASHED_PASSWORD"
        )

        with app.app_context():
            db.session.add(user1)
            db.session.commit()

            # User should have no messages, likes, followers, and following
            self.assertEqual(len(user1.messages), 0)
            self.assertEqual(len(user1.likes), 0)
            self.assertEqual(len(user1.followers), 0)
            self.assertEqual(len(user1.following), 0)

        # User should have the correct attributes
        self.assertEqual(user1.email, "test1@test.com")
        self.assertEqual(user1.username, "testuser1")
        self.assertEqual(user1.image_url, "/static/images/default-pic.png")
        self.assertEqual(user1.header_image_url, "/static/images/warbler-hero.jpg")
        self.assertIsNone(user1.bio)
        self.assertEqual(user1.location, "Planet Earth")
        self.assertEqual(user1.password, "HASHED_PASSWORD")

    def test_repr(self):
        """
        Test user __repr__ method output.
        """

        with app.app_context():
            user0 = db.session.get(User, self.user0_id)

        self.assertEqual(repr(user0), f"<User #{self.user0_id}: testuser, test@test.com>")

    def test_is_following_true(self):
        """
        Test that is_following() successfully detects when a user is and is not following another.
        """

        user1 = User(
            email="test1@test.com",
            username="testuser1",
            password="HASHED_PASSWORD1"
        )

        user2 = User(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD2"
        )

        with app.app_context():
            db.session.add_all([user1, user2])
            db.session.commit()

            user0 = db.session.get(User, self.user0_id)
            user0.following.append(user1)

            self.assertTrue(user0.is_following(user1))
            self.assertFalse(user0.is_following(user2))

    def test_is_followed_by(self):
        """
        Test that is_followed_by() successfully detects when a user is and is not followed by
        another user.
        """

        user1 = User(
            email="test1@test.com",
            username="testuser1",
            password="HASHED_PASSWORD1"
        )

        user2 = User(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD2"
        )

        with app.app_context():
            db.session.add_all([user1, user2])
            db.session.commit()

            user0 = db.session.get(User, self.user0_id)
            user0.followers.append(user1)

            self.assertTrue(user0.is_followed_by(user1))
            self.assertFalse(user0.is_followed_by(user2))

    def test_signup_success(self):
        """
        Test that a new user is created, given valid credentials.
        """

        with app.app_context():
            user = User.signup("signupuser",
                               "signup@test.com",
                               "SIGNUPPW",
                               "imageurl",
                               "Somewhere")
            db.session.commit()

            self.assertIsInstance(user, User)
            self.assertEqual(user.email, "signup@test.com")
            self.assertEqual(user.username, "signupuser")
            self.assertEqual(user.image_url, "imageurl")
            self.assertTrue(user.password.startswith("$2b"))

    def test_signup_failure(self):
        """
        Test that a new user is not created, given invalid credentials.
        """

        with app.app_context():

            # Violates uniqueness
            User.signup("testuser", "test@test.com", "SIGNUPPW", "imageurl", "Somewhere")
            self.assertRaises(IntegrityError, db.session.commit)
            db.session.rollback()

            # Violates non-nullable field constraints
            User.signup(None, None, "SIGNUPPW", "imageurl", "Somewhere")
            self.assertRaises(IntegrityError, db.session.commit)
            db.session.rollback()

    def test_authentication_success(self):
        """
        Test that the correct user is returned when valid credentials (username and password) are
        given.
        """

        hashed_pwd = bcrypt.generate_password_hash("HASHED_PASSWORD1").decode('UTF-8')
        user1 = User(
            email="test1@test.com",
            username="testuser1",
            password=hashed_pwd
        )

        with app.app_context():
            db.session.add(user1)
            db.session.commit()

            found_user = User.authenticate("testuser1", "HASHED_PASSWORD1")

        self.assertIsInstance(found_user, User)
        self.assertEqual(found_user.username, "testuser1")
        self.assertEqual(found_user.email, "test1@test.com")

    def test_authentication_failure(self):
        """
        Test that no user is returned when invalid credentials are given.
        """

        hashed_pwd = bcrypt.generate_password_hash("HASHED_PASSWORD1").decode('UTF-8')
        user1 = User(
            email="test1@test.com",
            username="testuser1",
            password=hashed_pwd
        )

        with app.app_context():
            db.session.add(user1)
            db.session.commit()

            self.assertFalse(User.authenticate("nonexistent", "HASHED_PASSWORD1"))
            self.assertFalse(User.authenticate("testuser1", "NONEXISTENT"))
