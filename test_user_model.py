# Ioana A Mititean
# Unit 26: Warbler (Twitter Clone)

"""
User model tests for Warbler.
"""

from unittest import TestCase

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
