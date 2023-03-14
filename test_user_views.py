# Ioana A Mititean
# Unit 26: Warbler (Twitter Clone)

"""
User view tests.
"""

from unittest import TestCase
from flask_bcrypt import Bcrypt

from app import app, CURR_USER_KEY
from models import db, connect_db, User

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///warbler_test"
app.config['SQLALCHEMY_ECHO'] = False

app.config['TESTING'] = True
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

# Don't have WTForms use CSRF at all, since it's a pain to test
app.config['WTF_CSRF_ENABLED'] = False

bcrypt = Bcrypt()

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

    def test_display_likes_logged_out(self):
        """
        Test that logged-out users will be redirected to homepage if they try to access any user's
        likes display page.
        """

        with self.client as c:
            resp = c.get(f"/users/{self.user0_id}/likes")

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, "/")

    def test_display_likes(self):
        """
        For logged-in users:

        Test that a user can view a display of their likes, as well as a display of the likes of
        another user.
        """

        with self.client as c:

            # 'Log in' as user 0
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user0_id

            resp_self = c.get(f"/users/{self.user0_id}/likes")
            resp_other = c.get(f"/users/{self.user1_id}/likes")

            html_self = resp_self.get_data(as_text=True)
            html_other = resp_other.get_data(as_text=True)

            self.assertEqual(resp_self.status_code, 200)
            self.assertEqual(resp_other.status_code, 200)

            self.assertIn('<h4 id="sidebar-username">@testuser0</h4>', html_self)
            self.assertIn('<h1 class="display-6">Liked Warbles</h1>', html_self)

            self.assertIn('<h4 id="sidebar-username">@testuser1</h4>', html_other)
            self.assertIn('<h1 class="display-6">Liked Warbles</h1>', html_other)

    # ---------------------------------------------------------------------------------------------

    # TESTS FOR UPDATING USER PROFILE -------------------------------------------------------------

    def test_update_profile_logged_out(self):
        """
        Test that logged-out users will be redirected to homepage if they try to access a profile
        edit page.
        """

        with self.client as c:
            resp = c.get("/users/profile")

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, "/")

    def test_update_profile_form(self):
        """
        For logged-in users:

        Test that the form for updating a user profile is displayed when accessing a user profile
        page.
        """

        with self.client as c:

            # 'Log in' as user 0
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user0_id

            resp = c.get("/users/profile")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h2 class="join-message">Edit Your Profile.</h2>', html)

    def test_update_profile(self):
        """
        For logged-in users:

        Test that a user can successfully update their profile.
        """

        # Add new user with encrypted password
        with app.app_context():
            hashed_pw = bcrypt.generate_password_hash("EXTRA_PW").decode('UTF-8')
            extra_user = User(username="extra",
                              password=hashed_pw,
                              email="extra@extra.com")

            db.session.add(extra_user)
            db.session.commit()

            with self.client as c:

                # 'Log in' as new user
                with c.session_transaction() as sess:
                    sess[CURR_USER_KEY] = extra_user.id

                resp = c.post("/users/profile", data={"username": "NEW_UNAME",
                                                      "email": "NEW_EMAIL@EMAIL.COM",
                                                      "image_url": "NEW_IMAGE_URL",
                                                      "header_image_url": "NEW_HEADER_IMG",
                                                      "bio": "NEW BIO",
                                                      "password": "EXTRA_PW"})

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, f"/users/{extra_user.id}")

            # Check that user attributes have been changed accordingly
            self.assertEqual(extra_user.username, "NEW_UNAME")
            self.assertEqual(extra_user.email, "NEW_EMAIL@EMAIL.COM")
            self.assertEqual(extra_user.image_url, "NEW_IMAGE_URL")
            self.assertEqual(extra_user.header_image_url, "NEW_HEADER_IMG")
            self.assertEqual(extra_user.bio, "NEW BIO")

    # ---------------------------------------------------------------------------------------------

    # TESTS FOR DELETING A USER -------------------------------------------------------------------

    def test_delete_user_logged_out(self):
        """
        Test that logged-out users will be redirected to homepage if they try to delete a user.
        """

        with self.client as c:
            resp = c.post("/users/delete")

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, "/")

    def test_delete_user(self):
        """
        For logged-in users:

        Test that a user is successfully deleted.
        """

        with app.app_context():
            curr_user = db.session.get(User, self.user0_id)
            init_num_users = User.query.count()

            with self.client as c:

                # 'Log in' as user 0 and delete the user
                with c.session_transaction() as sess:
                    sess[CURR_USER_KEY] = self.user0_id

                resp = c.post("/users/delete")

                self.assertEqual(resp.status_code, 302)
                self.assertEqual(resp.location, "/signup")

            # Check that the correct user was deleted
            users = User.query.all()
            self.assertEqual(len(users), init_num_users - 1)
            self.assertNotIn(curr_user, users)

    # ---------------------------------------------------------------------------------------------

    # TESTS FOR ADDING/REMOVING LIKES AND FOLLOWING -----------------------------------------------

    # ---------------------------------------------------------------------------------------------
