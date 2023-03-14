# Ioana A Mititean
# Unit 26: Warbler (Twitter Clone)

"""
User view tests.
"""

from unittest import TestCase
from sqlalchemy import select

from app import app, CURR_USER_KEY
from models import db, connect_db, User, Follow

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
                email="test0@test.com",
                username="testuser0",
                password="HASHED_PASSWORD0"
            )

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

            user3 = User(
                email="test3@test.com",
                username="testuser3",
                password="HASHED_PASSWORD3"
            )

            db.session.add_all([user0, user1, user2, user3])
            db.session.commit()

            self.user0_id = user0.id
            self.user1_id = user1.id
            self.user2_id = user2.id
            self.user3_id = user3.id

        self.client = app.test_client()
        return super().setUp()

    def tearDown(self) -> None:
        """
        Clean up any fouled transaction.
        """

        with app.app_context():
            db.session.rollback()

        return super().tearDown()

    # TESTS FOR VIEWING USER INFO -----------------------------------------------------------------

    # ---------------------------------------------------------------------------------------------

    # TESTS FOR AUTH: SIGNUP, LOGIN, LOGOUT -------------------------------------------------------

    # ---------------------------------------------------------------------------------------------

    # TESTS FOR UPDATING USER PROFILE -------------------------------------------------------------

    # ---------------------------------------------------------------------------------------------

    # TESTS FOR DELETING A USER -------------------------------------------------------------------

    # ---------------------------------------------------------------------------------------------

    # TESTS FOR ADDING/REMOVING LIKES AND FOLLOWING -----------------------------------------------

    # ---------------------------------------------------------------------------------------------
