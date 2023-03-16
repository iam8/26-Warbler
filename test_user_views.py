# Ioana A Mititean
# Unit 26: Warbler (Twitter Clone)

"""
User view tests.
"""

from unittest import TestCase
from flask_bcrypt import Bcrypt

from app import app, CURR_USER_KEY
from models import db, connect_db, User, Message, Follow, Like

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

    def test_update_profile_failed_auth(self):
        """
        For logged-in users:

        Test that the user is redirected and not updated if password authentication fails.
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
                                                      "location": "US",
                                                      "password": "WRONG_PW"})

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, "/")

            # Check that user attributes have not been changed
            self.assertEqual(extra_user.username, "extra")
            self.assertEqual(extra_user.email, "extra@extra.com")
            self.assertEqual(extra_user.image_url, User.image_url.server_default.arg)
            self.assertEqual(extra_user.header_image_url, User.header_image_url.server_default.arg)
            self.assertEqual(extra_user.location, "Planet Earth")
            self.assertIsNone(extra_user.bio)

    def test_update_profile_invalid_inputs(self):
        """
        For logged-in users:

        Test that the profile page is re-rendered and that the user is not updated if invalid
        inputs are given (existing username or email).
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

                resp = c.post("/users/profile", data={"username": "testuser0",
                                                      "email": "test0@test.com",
                                                      "image_url": "NEW_IMAGE_URL",
                                                      "header_image_url": "NEW_HEADER_IMG",
                                                      "bio": "NEW BIO",
                                                      "location": "US",
                                                      "password": "EXTRA_PW"})

                html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h2 class="join-message">Edit Your Profile.</h2>', html)

            # Check that user attributes have not been changed
            self.assertEqual(extra_user.username, "extra")
            self.assertEqual(extra_user.email, "extra@extra.com")
            self.assertEqual(extra_user.image_url, User.image_url.server_default.arg)
            self.assertEqual(extra_user.header_image_url, User.header_image_url.server_default.arg)
            self.assertEqual(extra_user.location, "Planet Earth")
            self.assertIsNone(extra_user.bio)

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
                                                      "location": "US",
                                                      "password": "EXTRA_PW"})

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, f"/users/{extra_user.id}")

            # Check that user attributes have been changed accordingly
            self.assertEqual(extra_user.username, "NEW_UNAME")
            self.assertEqual(extra_user.email, "NEW_EMAIL@EMAIL.COM")
            self.assertEqual(extra_user.image_url, "NEW_IMAGE_URL")
            self.assertEqual(extra_user.header_image_url, "NEW_HEADER_IMG")
            self.assertEqual(extra_user.location, "US")
            self.assertEqual(extra_user.bio, "NEW BIO")

    # ---------------------------------------------------------------------------------------------

    # TESTS FOR DELETING A USER -------------------------------------------------------------------

    def test_delete_user_logged_out(self):
        """
        Test that logged-out users will be redirected to homepage if they try to delete a user, and
        that no user is deleted from the database.
        """

        with app.app_context():
            init_user_count = User.query.count()

            with self.client as c:
                resp = c.post("/users/delete")

                self.assertEqual(resp.status_code, 302)
                self.assertEqual(resp.location, "/")

            self.assertEqual(User.query.count(), init_user_count)

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

    def test_add_follow_logged_out(self):
        """
        Test that logged-out users will be redirected to homepage if they try to add a follow, and
        that no new follow is added to database.
        """

        with app.app_context():
            init_num_follows = Follow.query.count()

            with self.client as c:
                resp = c.post(f"/users/follow/{self.user1_id}")

                self.assertEqual(resp.status_code, 302)
                self.assertEqual(resp.location, "/")

            self.assertEqual(Follow.query.count(), init_num_follows)

    def test_add_follow_self(self):
        """
        For logged-in users:

        Test that a user cannot follow themselves.
        """

        with app.app_context():
            init_num_follows = Follow.query.count()

            with self.client as c:

                # 'Log in' as user 0
                with c.session_transaction() as sess:
                    sess[CURR_USER_KEY] = self.user0_id

                resp = c.post(f"/users/follow/{self.user0_id}")
                self.assertEqual(resp.status_code, 302)
                self.assertEqual(resp.location, "/")

            self.assertEqual(Follow.query.count(), init_num_follows)

    def test_add_follow_existing(self):
        """
        For logged-in users:

        Test that nothing changes if a user tries to follow someone they are already following.
        """

        # Create a new following: user0 follows user1
        follow = Follow(user_being_followed_id=self.user1_id,
                        user_following_id=self.user0_id)

        with app.app_context():
            db.session.add(follow)
            db.session.commit()

            init_num_follows = Follow.query.count()

            with self.client as c:

                # 'Log in' as user 0
                with c.session_transaction() as sess:
                    sess[CURR_USER_KEY] = self.user0_id

                c.post(f"/users/follow/{self.user1_id}")

            self.assertEqual(Follow.query.count(), init_num_follows)
            self.assertIn(follow, Follow.query.all())

    def test_add_follow(self):
        """
        For logged-in users:

        Test that a user can successfully follow another user.
        """

        with app.app_context():
            user0 = db.session.get(User, self.user0_id)
            user1 = db.session.get(User, self.user1_id)
            init_num_follows = Follow.query.count()

            with self.client as c:

                # 'Log in' as user 0
                with c.session_transaction() as sess:
                    sess[CURR_USER_KEY] = self.user0_id

                resp = c.post(f"/users/follow/{self.user1_id}")

                self.assertEqual(resp.status_code, 302)
                self.assertEqual(resp.location, f"/users/{self.user0_id}/following")

            self.assertIn(user1, user0.following)
            self.assertIn(user0, user1.followers)
            self.assertEqual(Follow.query.count(), init_num_follows + 1)

    def test_stop_following_logged_out(self):
        """
        Test that logged-out users will be redirected to homepage if they try to remove a follow,
        and that no follow is removed from the database.
        """

        # Create a new following: user1 follows user0
        follow = Follow(user_being_followed_id=self.user0_id,
                        user_following_id=self.user1_id)

        with app.app_context():
            db.session.add(follow)
            db.session.commit()

            init_follows_count = Follow.query.count()

            with self.client as c:
                resp = c.post(f"/users/stop_following/{self.user0_id}")

                self.assertEqual(resp.status_code, 302)
                self.assertEqual(resp.location, "/")

            self.assertEqual(Follow.query.count(), init_follows_count)

    def test_stop_following_nonexistent(self):
        """
        For logged-in users:

        Test that nothing changes if a user tries to unfollow a user that they were not following
        in the first place.
        """

        with app.app_context():
            user0 = db.session.get(User, self.user0_id)
            init_user0_following = len(user0.following)
            init_follows_count = Follow.query.count()

            with self.client as c:

                # 'Log in' as user 0
                with c.session_transaction() as sess:
                    sess[CURR_USER_KEY] = self.user0_id

                c.post(f"/users/stop_following/{self.user1_id}")

            self.assertEqual(len(user0.following), init_user0_following)
            self.assertEqual(Follow.query.count(), init_follows_count)

    def test_stop_following(self):
        """
        For logged-in users:

        Test that a user can successfully remove a follow.
        """

        with app.app_context():
            user0 = db.session.get(User, self.user0_id)
            user1 = db.session.get(User, self.user1_id)
            user0.following.append(user1)

            db.session.commit()

            init_num_follows = Follow.query.count()

            with self.client as c:

                # 'Log in' as user 0
                with c.session_transaction() as sess:
                    sess[CURR_USER_KEY] = self.user0_id

                resp = c.post(f"/users/stop_following/{self.user1_id}")

                self.assertEqual(resp.status_code, 302)
                self.assertEqual(resp.location, f"/users/{self.user0_id}/following")

            self.assertNotIn(user1, user0.following)
            self.assertNotIn(user0, user1.followers)
            self.assertEqual(Follow.query.count(), init_num_follows - 1)

    def test_add_like_logged_out(self):
        """
        Test that logged-out users will be redirected to homepage if they try to add a like, and
        that no likes are added to the database.
        """

        # Add a message to user 0
        msg0 = Message(text="Message 0 text", user_id=self.user0_id)

        with app.app_context():
            db.session.add(msg0)
            db.session.commit()

            init_like_count = Like.query.count()

            with self.client as c:
                resp = c.post(f"/users/add_like/{msg0.id}")

                self.assertEqual(resp.status_code, 302)
                self.assertEqual(resp.location, "/")

            self.assertEqual(Like.query.count(), init_like_count)

    def test_add_like_self(self):
        """
        For logged-in users:

        Test that a user cannot like their own message.
        """

        # Create a message for user 0
        msg = Message(text="Message text", user_id=self.user0_id)

        with app.app_context():
            db.session.add(msg)
            db.session.commit()

            init_num_likes = Like.query.count()

            with self.client as c:

                # 'Log in' as user 0
                with c.session_transaction() as sess:
                    sess[CURR_USER_KEY] = self.user0_id

                resp = c.post(f"/users/add_like/{msg.id}")
                self.assertEqual(resp.status_code, 302)
                self.assertEqual(resp.location, "/")

            self.assertEqual(Like.query.count(), init_num_likes)

    def test_add_like_existing(self):
        """
        For logged-in users:

        Test that nothing changes if a user tries to like a message they already liked.
        """

        # Create a new message for user 1
        msg = Message(text="Message text", user_id=self.user1_id)

        with app.app_context():
            user0 = db.session.get(User, self.user0_id)
            user0.likes.append(msg)

            db.session.add(msg)
            db.session.commit()

            init_user0_likes = len(user0.likes)
            init_num_likes = Like.query.count()

            with self.client as c:

                # 'Log in' as user 0
                with c.session_transaction() as sess:
                    sess[CURR_USER_KEY] = self.user0_id

                c.post(f"/users/add_like/{msg.id}")

            self.assertEqual(len(user0.likes), init_user0_likes)
            self.assertEqual(Like.query.count(), init_num_likes)

    def test_add_like(self):
        """
        For logged-in users:

        Test that a user can successfully add a like.
        """

        # Create a new message for user 1
        msg = Message(text="Message text", user_id=self.user1_id)

        with app.app_context():
            db.session.add(msg)
            db.session.commit()

            user0 = db.session.get(User, self.user0_id)
            init_num_likes = Like.query.count()

            with self.client as c:

                # 'Log in' as user 0
                with c.session_transaction() as sess:
                    sess[CURR_USER_KEY] = self.user0_id

                resp = c.post(f"/users/add_like/{msg.id}")

                self.assertEqual(resp.status_code, 302)
                self.assertEqual(resp.location, f"/users/{self.user0_id}/likes")

            self.assertIn(msg, user0.likes)
            self.assertEqual(Like.query.count(), init_num_likes + 1)

    def test_remove_like_logged_out(self):
        """
        Test that logged-out users will be redirected to homepage if they try to remove a like, and
        that no likes are removed from the database.
        """

        # Add a message to user 1
        msg1 = Message(text="Message 1 text", user_id=self.user1_id)

        with app.app_context():
            db.session.add(msg1)
            db.session.commit()

            # Add this message as a like to user 0
            user0 = db.session.get(User, self.user0_id)
            user0.likes.append(msg1)

            init_likes_count = Like.query.count()

            with self.client as c:
                resp = c.post(f"/users/remove_like/{msg1.id}")

                self.assertEqual(resp.status_code, 302)
                self.assertEqual(resp.location, "/")

            self.assertEqual(Like.query.count(), init_likes_count)

    def test_remove_like_nonexistent(self):
        """
        For logged-in users:

        Test that nothing changes if a user tries to remove a like that they were not liking in the
        first place.
        """

        # Add a message to user 1
        msg1 = Message(text="Message 1 text", user_id=self.user1_id)

        with app.app_context():
            db.session.add(msg1)
            db.session.commit()

            user0 = db.session.get(User, self.user0_id)
            init_user0_likes = len(user0.likes)
            init_likes_count = Like.query.count()

            with self.client as c:

                # 'Log in' as user 0
                with c.session_transaction() as sess:
                    sess[CURR_USER_KEY] = self.user0_id

                c.post(f"/users/remove_like/{msg1.id}")

            self.assertEqual(len(user0.likes), init_user0_likes)
            self.assertEqual(Like.query.count(), init_likes_count)

    def test_remove_like(self):
        """
        For logged-in users:

        Test that a user can successfully remove a like.
        """

        # Add a message to user 1
        msg1 = Message(text="Message 1 text", user_id=self.user1_id)

        with app.app_context():
            db.session.add(msg1)
            db.session.commit()

            # Add this message as a like to user 0
            user0 = db.session.get(User, self.user0_id)
            user0.likes.append(msg1)

            init_num_likes = Like.query.count()

            with self.client as c:

                # 'Log in' as user 0
                with c.session_transaction() as sess:
                    sess[CURR_USER_KEY] = self.user0_id

                resp = c.post(f"/users/remove_like/{msg1.id}")

                self.assertEqual(resp.status_code, 302)
                self.assertEqual(resp.location, f"/users/{self.user0_id}/likes")

            self.assertNotIn(msg1, user0.likes)
            self.assertEqual(Like.query.count(), init_num_likes - 1)

    # ---------------------------------------------------------------------------------------------
