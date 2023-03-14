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

    # TESTS FOR ADDING MESSAGES -------------------------------------------------------------------

    def test_add_message_form_logged_out(self):
        """
        Test that logged-out users will be redirected to homepage if they try to access the page
        for adding new messages.
        """

        with self.client as c:
            resp = c.get("/messages/new")

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, "/")

    def test_add_message_form(self):
        """
        For logged-in users:

        Test that accessing the page for new messages displays a form for adding new messages.
        """

        # Change session to mimic logging in
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user_id

            resp = c.get("/messages/new")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('form method="POST"', html)
            self.assertIn("What&#39;s happening?", html)

    def test_add_message_as_self(self):
        """
        For logged-in users:

        Can users successfully add a message as themselves?
        """

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user_id

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, f"/users/{self.user_id}")

            msg = db.session.scalars(select(Message)).one()
            self.assertEqual(msg.text, "Hello")
            self.assertEqual(msg.user.id, self.user_id)

    # ---------------------------------------------------------------------------------------------

    # TESTS FOR SHOWING MESSAGES ------------------------------------------------------------------

    def test_view_message_logged_out(self):
        """
        Test that logged-out users will be redirected to homepage if they try to view any message.
        """

        with self.client as c:
            resp = c.get("/messages/new")

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, "/")

    def test_view_own_message(self):
        """
        For logged-in users:

        Test that a user can view their own message.
        """

        # Add message
        msg = Message(text="Message text",
                      user_id=self.user_id)

        with app.app_context():
            db.session.add(msg)
            db.session.commit()

            # 'Log in' as first user and view message
            with self.client as c:
                with c.session_transaction() as sess:
                    sess[CURR_USER_KEY] = self.user_id

                resp = c.get(f"/messages/{msg.id}")
                html = resp.get_data(as_text=True)

                self.assertEqual(resp.status_code, 200)
                self.assertIn('class="single-message"', html)
                self.assertIn(msg.text, html)

    def test_view_other_message(self):
        """
        For logged-in users:

        Test that a user can view the messages of a different user.
        """

        with app.app_context():

            # Add a new user
            user1 = User.signup(username="testuser1",
                                email="test1@test.com",
                                password="testuser1",
                                image_url=None)

            db.session.commit()

            # Add message for new user
            msg1 = Message(text="Message text 1",
                           user_id=user1.id)

            db.session.add(msg1)
            db.session.commit()

            # 'Log in' as first user and view message
            with self.client as c:
                with c.session_transaction() as sess:
                    sess[CURR_USER_KEY] = self.user_id

                resp = c.get(f"/messages/{msg1.id}")
                html = resp.get_data(as_text=True)

                self.assertEqual(resp.status_code, 200)
                self.assertIn('class="single-message"', html)
                self.assertIn(msg1.text, html)

    # ---------------------------------------------------------------------------------------------

    # TESTS FOR DELETING MESSAGES -----------------------------------------------------------------

    def test_delete_message_logged_out(self):
        """
        Test that logged-out users will be redirected to homepage if they try to delete a message.
        """

        with app.app_context():

            # Add message for initial user
            msg = Message(text="Message text",
                          user_id=self.user_id)

            db.session.add(msg)
            db.session.commit()

            init_num_msgs = Message.query.count()

            # Try deleting a message
            with self.client as c:
                resp = c.post(f"/messages/{msg.id}/delete")

                self.assertEqual(resp.status_code, 302)
                self.assertEqual(resp.location, "/")

            # Check that no message was deleted
            self.assertEqual(Message.query.count(), init_num_msgs)

    def test_delete_own_message(self):
        """
        For logged-in users:

        Test that a user can delete their own message.
        """

        with app.app_context():

            # Add messages for user
            msg0 = Message(text="Message text 0",
                           user_id=self.user_id)

            msg1 = Message(text="Message text 1",
                           user_id=self.user_id)

            db.session.add_all([msg0, msg1])
            db.session.commit()

            init_num_msgs = Message.query.count()

            # 'Log in' and delete a message
            with self.client as c:
                with c.session_transaction() as sess:
                    sess[CURR_USER_KEY] = self.user_id

                resp = c.post(f"/messages/{msg0.id}/delete")

                self.assertEqual(resp.status_code, 302)
                self.assertEqual(resp.location, f"/users/{self.user_id}")

            # Check that correct message was deleted
            msgs = Message.query.all()
            self.assertEqual(len(msgs), init_num_msgs - 1)
            self.assertIn(msg1, msgs)

    def test_delete_other_message(self):
        """
        For logged-in users:

        Test that a user can NOT delete the message of another user.
        """

        with app.app_context():

            # Add new user
            user1 = User.signup(username="testuser1",
                                email="test1@test.com",
                                password="testuser1",
                                image_url=None)

            db.session.commit()

            # Add message for new user
            msg = Message(text="Message text 1",
                          user_id=user1.id)

            db.session.add(msg)
            db.session.commit()

            init_num_msgs = Message.query.count()

            # 'Log in' as initial user and try deleting a message
            with self.client as c:
                with c.session_transaction() as sess:
                    sess[CURR_USER_KEY] = self.user_id

                resp = c.post(f"/messages/{msg.id}/delete")

                self.assertEqual(resp.status_code, 302)
                self.assertEqual(resp.location, "/")

            # Check that no message was deleted
            self.assertEqual(Message.query.count(), init_num_msgs)

    # ---------------------------------------------------------------------------------------------
