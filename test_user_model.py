# Ioana A Mititean
# Unit 26: Warbler (Twitter Clone)

"""
User model tests for Warbler.
"""

from unittest import TestCase
from sqlalchemy.exc import IntegrityError

from app import app
from models import db, connect_db, User, Message, Follow

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///warbler_test"
app.config['SQLALCHEMY_ECHO'] = False

app.config['TESTING'] = True
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

connect_db(app)

with app.app_context():
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

        user = User(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD"
        )

        with app.app_context():
            db.session.add(user)
            db.session.commit()

            # User should have no messages, likes, followers, and following
            self.assertEqual(len(user.messages), 0)
            self.assertEqual(len(user.likes), 0)
            self.assertEqual(len(user.followers), 0)
            self.assertEqual(len(user.following), 0)

        # User should have the correct attributes
        self.assertEqual(user.email, "test2@test.com")
        self.assertEqual(user.username, "testuser2")
        self.assertEqual(user.image_url, "/static/images/default-pic.png")
        self.assertEqual(user.header_image_url, "/static/images/warbler-hero.jpg")
        self.assertIsNone(user.bio)
        self.assertIsNone(user.location)
        self.assertEqual(user.password, "HASHED_PASSWORD")

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
            user = User.signup("signupuser", "signup@test.com", "SIGNUPPW", "imageurl")
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
            User.signup("testuser", "test@test.com", "SIGNUPPW", "imageurl")
            self.assertRaises(IntegrityError, db.session.commit)
            db.session.rollback()

            # Violates non-nullable field constraints
            User.signup(None, None, "SIGNUPPW", "imageurl")
            self.assertRaises(IntegrityError, db.session.commit)
            db.session.rollback()

    def test_authentication_success(self):
        """
        Test that the correct user is returned when valid credentials (username and password) are
        given.
        """

        assert False

    def test_authentication_failure(self):
        """
        Test that no user is returned when invalid credentials are given.
        """

        assert False
