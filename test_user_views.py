# Ioana A Mititean
# Unit 26: Warbler (Twitter Clone)

"""
User view tests.
"""

from unittest import TestCase

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

    def test_list_users(self):
        """
        Test that all users are displayed by default on the users listing page.
        """

        with self.client as c:
            resp = c.get("/users")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)

            for username in ["testuser0", "testuser1", "testuser2", "testuser3"]:
                self.assertIn(username, html)

    def test_list_users_search(self):
        """
        Test that only a single user is displayed on page when search (by username) is used.
        """

        with self.client as c:
            resp = c.get("/users", query_string={"q": "testuser3"})
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("testuser3", html)

            for username in ["testuser0", "testuser1", "testuser2"]:
                self.assertNotIn(username, html)

    def test_show_user_profile(self):
        """
        Test displaying of a user profile page.
        """

        with self.client as c:
            resp0 = c.get(f"/users/{self.user0_id}")
            resp1 = c.get(f"/users/{self.user1_id}")

            html0 = resp0.get_data(as_text=True)
            html1 = resp1.get_data(as_text=True)

            self.assertEqual(resp0.status_code, 200)
            self.assertEqual(resp1.status_code, 200)

            self.assertIn('<h4 id="sidebar-username">@testuser0</h4>', html0)
            self.assertIn('<h4 id="sidebar-username">@testuser1</h4>', html1)

    def test_show_following_logged_out(self):
        """
        Test that logged-out users will be redirected to homepage if they try to access any user's
        following display page.
        """

        with self.client as c:
            resp = c.get(f"/users/{self.user0_id}/following")

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, "/")

    def test_show_following(self):
        """
        For logged-in users:

        Test that a user can view a display of users they are following, as well as a display of
        users that another user is following.
        """

        with self.client as c:

            # 'Log in' as user 0
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user0_id

            resp_self = c.get(f"/users/{self.user0_id}/following")
            resp_other = c.get(f"/users/{self.user1_id}/following")

            html_self = resp_self.get_data(as_text=True)
            html_other = resp_other.get_data(as_text=True)

            self.assertEqual(resp_self.status_code, 200)
            self.assertEqual(resp_other.status_code, 200)

            self.assertIn('<h4 id="sidebar-username">@testuser0</h4>', html_self)
            self.assertIn('<h1 class="display-6">Users That This User is Following</h1>',
                          html_self)

            self.assertIn('<h4 id="sidebar-username">@testuser1</h4>', html_other)
            self.assertIn('<h1 class="display-6">Users That This User is Following</h1>',
                          html_other)

    def test_show_followers_logged_out(self):
        """
        Test that logged-out users will be redirected to homepage if they try to access any user's
        followers display page.
        """

        with self.client as c:
            resp = c.get(f"/users/{self.user0_id}/followers")

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, "/")

    def test_show_followers(self):
        """
        For logged-in users:

        Test that a user can view a display of their followers, as well as a display of the
        followers of another user.
        """

        with self.client as c:

            # 'Log in' as user 0
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user0_id

            resp_self = c.get(f"/users/{self.user0_id}/followers")
            resp_other = c.get(f"/users/{self.user1_id}/followers")

            html_self = resp_self.get_data(as_text=True)
            html_other = resp_other.get_data(as_text=True)

            self.assertEqual(resp_self.status_code, 200)
            self.assertEqual(resp_other.status_code, 200)

            self.assertIn('<h4 id="sidebar-username">@testuser0</h4>', html_self)
            self.assertIn('<h1 class="display-6">Followers</h1>', html_self)

            self.assertIn('<h4 id="sidebar-username">@testuser1</h4>', html_other)
            self.assertIn('<h1 class="display-6">Followers</h1>', html_other)

    # ---------------------------------------------------------------------------------------------

    # TESTS FOR AUTH: SIGNUP, LOGIN, LOGOUT -------------------------------------------------------

    # ---------------------------------------------------------------------------------------------

    # TESTS FOR UPDATING USER PROFILE -------------------------------------------------------------

    # ---------------------------------------------------------------------------------------------

    # TESTS FOR DELETING A USER -------------------------------------------------------------------

    # ---------------------------------------------------------------------------------------------

    # TESTS FOR ADDING/REMOVING LIKES AND FOLLOWING -----------------------------------------------

    # ---------------------------------------------------------------------------------------------
