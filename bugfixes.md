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