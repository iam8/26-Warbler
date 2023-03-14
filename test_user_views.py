# Ioana A Mititean
# Unit 26: Warbler (Twitter Clone)

"""
User view tests.
"""

from unittest import TestCase
from sqlalchemy import select

from app import app, CURR_USER_KEY
from models import db, connect_db, User

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///warbler_test"
app.config['SQLALCHEMY_ECHO'] = False

app.config['TESTING'] = True
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

# Don't have WTForms use CSRF at all, since it's a pain to test
app.config['WTF_CSRF_ENABLED'] = False

connect_db(app)

with app.app_context():
    db.create_all()


class UserViewTestCase(TestCase):
    """
    Test views for users.
    """

    def setUp(self):
        """
        Create test client, add sample data.
        """

        with app.app_context():
            User.query.delete()

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
