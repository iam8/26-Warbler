# Warbler App: Bugfixes and Other Changes

Ioana A Mititean<br>
Unit 26: Warbler<br>

- Changed 'default' in models.py to 'server_default'
- Changed functions used to get the current datetime for default message timestamp
- Changed SQLA model names to be all singular, for consistency
- Line 128, models.py, User model: change 'secondary' to 'backref' in 'likes' relationship