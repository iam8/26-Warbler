# Ioana A Mititean
# Unit 26: Warbler (Twitter Clone)

"""
Message view tests.
"""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py

from unittest import TestCase
from sqlalchemy import select

from app import app, CURR_USER_KEY
from models import db, connect_db, User, Message

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///warbler_test"
app.config['SQLALCHEMY_ECHO'] = False

app.config['TESTING'] = True
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

# Don't have WTForms use CSRF at all, since it's a pain to test
app.config['WTF_CSRF_ENABLED'] = False

connect_db(app)

with app.app_context():
    db.create_all()


class MessageViewTestCase(TestCase):
    """
    Test views for messages.
    """

    print("In setup function!")

    def setUp(self):
        """
        Create test client, add sample data.
        """

        with app.app_context():
            User.query.delete()
            Message.query.delete()

            user = User.signup(username="testuser",
                               email="test@test.com",
                               password="testuser",
                               image_url=None)

            db.session.commit()
            self.user_id = user.id

        self.client = app.test_client()
        return super().setUp()

    def tearDown(self) -> None:
        """
        Clean up any fouled transaction.
        """

        with app.app_context():
            db.session.rollback()

        return super().tearDown()

    def test_add_message(self):
        """
        Can users successfully add a message?
        """

        # Since we need to change the session to mimic logging in, we need to use the
        # changing-session trick:
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user_id

            # Now, that session setting is saved, so we can have the rest of our tests
            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, f"/users/{self.user_id}")

            msg = db.session.scalars(select(Message)).one()
            self.assertEqual(msg.text, "Hello")
