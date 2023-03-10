# Ioana A Mititean
# Unit 26: Warbler (Twitter Clone)

"""
Form models definitions (WTForms).
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import InputRequired, Optional, Email, Length


class MessageForm(FlaskForm):
    """
    Form for adding/editing messages.
    """

    text = TextAreaField('text', validators=[InputRequired()])


class UserAddForm(FlaskForm):
    """
    Form for adding users.
    """

    username = StringField('Username', validators=[InputRequired()])
    email = StringField('E-mail', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])
    image_url = StringField('(Optional) Profile image URL', validators=[Optional()])


class LoginForm(FlaskForm):
    """
    Login form.
    """

    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])


class UserEditForm(FlaskForm):
    """
    Form for editing user profiles.
    """

    username = StringField('Username', validators=[InputRequired()])
    email = StringField('E-mail', validators=[InputRequired(), Email()])
    image_url = StringField('(Optional) Profile image URL', validators=[Optional()])
    header_image_url = StringField('(Optional) Header image URL', validators=[Optional()])
    bio = TextAreaField("Bio", validators=[Optional()])
    password = PasswordField("Current password", validators=[InputRequired(), Length(min=6)])
