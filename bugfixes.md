# Warbler App: Bugfixes and Other Changes

Ioana A Mititean<br>
Unit 26: Warbler<br>

- File models.py: changed 'default' to 'server_default'
- File models.py: changed functions used to get the current datetime for default message timestamp
- File models.py: changed SQLA model names to be all singular, for consistency
- File models.py: change 'secondary' in User.likes relationship to 'backref'
- File models.py: added back_populates for model relationships
- File models.py: change 'backref' in User.likes relationship back to 'secondary'

- File app.py: set image_url to correct default if no URL provided in form

- File edit.jinja2: fixed href link for cancel button
- File app.py, signup view: fixed IntegrityError flash message to indicate that username OR email
is already taken

- File tests/test_user_model.py: connect explicitly to test database
- File tests/test_user_model.py: edited name of test database to include an underscore instead of a
hyphen (Postres complained)
- File tests/test_user_model.py: added app contexts around code that needs it
- File tests/test_user_model.py: add database commit after emptying tables in setUp
- File tests/test_user_model.py: add tearDown method