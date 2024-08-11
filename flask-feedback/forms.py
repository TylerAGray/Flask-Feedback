"""Forms for flask-feedback."""

from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Length, Email
from flask_wtf import FlaskForm

# Define forms using Flask-WTF and WTForms for various functionalities in the application

class LoginForm(FlaskForm):
    """Form for user login."""

    # Field for the username with validation
    username = StringField(
        "Username",
        validators=[
            InputRequired(),  # Ensures the field is not left empty
            Length(min=1, max=20)  # Username must be between 1 and 20 characters long
        ],
    )
    # Field for the password with validation
    password = PasswordField(
        "Password",
        validators=[
            InputRequired(),  # Ensures the field is not left empty
            Length(min=6, max=55)  # Password must be between 6 and 55 characters long
        ],
    )


class RegisterForm(FlaskForm):
    """Form for user registration."""

    # Field for the username with validation
    username = StringField(
        "Username",
        validators=[
            InputRequired(),  # Ensures the field is not left empty
            Length(min=1, max=20)  # Username must be between 1 and 20 characters long
        ],
    )
    # Field for the password with validation
    password = PasswordField(
        "Password",
        validators=[
            InputRequired(),  # Ensures the field is not left empty
            Length(min=6, max=55)  # Password must be between 6 and 55 characters long
        ],
    )
    # Field for the email with validation
    email = StringField(
        "Email",
        validators=[
            InputRequired(),  # Ensures the field is not left empty
            Email(),  # Validates that the input is a properly formatted email address
            Length(max=50)  # Email must be 50 characters or fewer
        ],
    )
    # Field for the user's first name with validation
    first_name = StringField(
        "First Name",
        validators=[
            InputRequired(),  # Ensures the field is not left empty
            Length(max=30)  # First name must be 30 characters or fewer
        ],
    )
    # Field for the user's last name with validation
    last_name = StringField(
        "Last Name",
        validators=[
            InputRequired(),  # Ensures the field is not left empty
            Length(max=30)  # Last name must be 30 characters or fewer
        ],
    )


class FeedbackForm(FlaskForm):
    """Form for submitting feedback."""

    # Field for the feedback title with validation
    title = StringField(
        "Title",
        validators=[
            InputRequired(),  # Ensures the field is not left empty
            Length(max=100)  # Title must be 100 characters or fewer
        ],
    )
    # Field for the feedback content with validation
    content = StringField(
        "Content",
        validators=[
            InputRequired()  # Ensures the field is not left empty
        ],
    )


class DeleteForm(FlaskForm):
    """Form for deletion actions -- intentionally left blank.

    This form is used as a placeholder for delete actions where no additional data is required.
    """
    pass  # No fields are needed for this form

