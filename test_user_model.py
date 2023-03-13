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

            db.session.commit()

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
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        with app.app_context():
            db.session.add(user)
            db.session.commit()

            # User should have no messages & no followers
            self.assertEqual(len(user.messages), 0)
            self.assertEqual(len(user.followers), 0)
