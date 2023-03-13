# Ioana A Mititean
# Unit 26: Warbler (Twitter Clone)

"""
Message model tests for Warbler.
"""

from unittest import TestCase
from datetime import datetime

from app import app
from models import db, connect_db, User, Message, Follow

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///warbler_test"
app.config['SQLALCHEMY_ECHO'] = False

app.config['TESTING'] = True
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

connect_db(app)

with app.app_context():
    db.create_all()


class MessageModelTestCase(TestCase):
    """
    Test Message model.
    """

    def setUp(self) -> None:
        """
        Create test client; empty tables of data; insert test data.
        """

        with app.app_context():
            User.query.delete()
            Message.query.delete()
            Follow.query.delete()

            # Add a user
            user0 = User(
                email="test@test.com",
                username="testuser",
                password="HASHED_PASSWORD"
            )

            db.session.add(user0)
            db.session.commit()

            self.user0_id = user0.id

            # Add 2 messages
            msg0 = Message(
                text="Message text 0",
                user_id=self.user0_id
            )

            msg1 = Message(
                text="Message text 1",
                user_id=self.user0_id
            )

            db.session.add_all([msg0, msg1])
            db.session.commit()

            self.msg0_id = msg0.id
            self.msg1_id = msg1.id

        self.client = app.test_client()
        return super().setUp()

    def tearDown(self) -> None:
        """
        Clean up any fouled transaction.
        """

        with app.app_context():
            db.session.rollback()

        return super().tearDown()

    def test_message_model(self):
        """
        Test basic Message model.
        """

        with app.app_context():
            msg = db.session.get(Message, self.msg0_id)

        # Message should have the correct attributes/types
        self.assertEqual(msg.text, "Message text 0")
        self.assertIsInstance(msg.timestamp, datetime)

        # Message should have the correct user ID
        msg.user_id = self.user0_id

    def test_message_user_relationship(self):
        """
        Test that a user is associated with the expected messages and vice versa.
        """

        with app.app_context():
            user = db.session.get(User, self.user0_id)
            msg0 = db.session.get(Message, self.msg0_id)
            msg1 = db.session.get(Message, self.msg1_id)

            self.assertIs(msg0.user, user)
            self.assertIs(msg1.user, user)

            u_messages = user.messages
            self.assertEqual(len(u_messages), 2)
            self.assertIn(msg0, u_messages)
            self.assertIn(msg1, u_messages)

    def test_repr(self):
        """
        Test message __repr__ method output.
        """

        with app.app_context():
            msg0 = db.session.get(Message, self.msg0_id)
            self.assertEqual(repr(msg0), f"<Message #{self.msg0_id}: User #{msg0.user.id}>")
