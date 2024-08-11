"""Models for flask-feedback."""

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

# Initialize Bcrypt for password hashing
bcrypt = Bcrypt()
# Initialize SQLAlchemy for database interactions
db = SQLAlchemy()


def connect_db(app):
    """Connect this database to the provided Flask app.

    This function binds the SQLAlchemy instance to the given Flask app. 
    It should be called in your Flask app's setup to ensure that the 
    database connection is properly configured.
    
    Args:
        app (Flask): The Flask application instance to bind with SQLAlchemy.
    """
    db.app = app  # Associate the app with the SQLAlchemy instance
    db.init_app(app)  # Initialize SQLAlchemy with the Flask app


class User(db.Model):
    """Represents a user in the application."""

    __tablename__ = "users"  # Name of the table in the database

    # Define the 'username' column, which will also be the primary key
    username = db.Column(
        db.String(20),
        nullable=False,
        unique=True,
        primary_key=True,
    )
    # Define the 'password' column to store hashed passwords
    password = db.Column(db.Text, nullable=False)
    # Define the 'email' column to store user email addresses
    email = db.Column(db.String(50), nullable=False)
    # Define the 'first_name' column to store user's first name
    first_name = db.Column(db.String(30), nullable=False)
    # Define the 'last_name' column to store user's last name
    last_name = db.Column(db.String(30), nullable=False)

    # Set up a one-to-many relationship with the Feedback model
    # This means one user can have many feedback entries
    feedback = db.relationship(
        "Feedback",  # The related model
        backref="user",  # Name of the back-reference from Feedback to User
        cascade="all,delete"  # Ensure that all related feedback is deleted if the user is deleted
    )

    # Convenience method for user registration
    @classmethod
    def register(cls, username, password, first_name, last_name, email):
        """Register a new user, hashing their password for security.

        This method creates a new user instance with a hashed password and 
        adds it to the database session.

        Args:
            username (str): The username of the user.
            password (str): The password for the user.
            first_name (str): The user's first name.
            last_name (str): The user's last name.
            email (str): The user's email address.

        Returns:
            User: The newly created user instance.
        """
        # Hash the provided password
        hashed = bcrypt.generate_password_hash(password)
        hashed_utf8 = hashed.decode("utf8")  # Convert hash to UTF-8 string
        # Create a new User instance with the provided details
        user = cls(
            username=username,
            password=hashed_utf8,
            first_name=first_name,
            last_name=last_name,
            email=email
        )

        # Add the user instance to the database session
        db.session.add(user)
        return user

    # Convenience method for user authentication
    @classmethod
    def authenticate(cls, username, password):
        """Authenticate a user by checking their username and password.

        This method verifies if a user exists with the given username and 
        if the provided password matches the stored hashed password.

        Args:
            username (str): The username of the user.
            password (str): The password provided by the user.

        Returns:
            User or bool: The user instance if authentication is successful; 
                          False otherwise.
        """
        # Query for a user with the given username
        user = User.query.filter_by(username=username).first()

        # Check if the user exists and if the password is correct
        if user and bcrypt.check_password_hash(user.password, password):
            return user
        else:
            return False


class Feedback(db.Model):
    """Represents feedback provided by users."""

    __tablename__ = "feedback"  # Name of the table in the database

    # Define the 'id' column as the primary key for the feedback table
    id = db.Column(db.Integer, primary_key=True)
    # Define the 'title' column for the feedback title
    title = db.Column(db.String(100), nullable=False)
    # Define the 'content' column to store the feedback content
    content = db.Column(db.Text, nullable=False)
    # Define the 'username' column to link feedback to a user
    username = db.Column(
        db.String(20),
        db.ForeignKey('users.username'),  # Foreign key constraint linking to 'users' table
        nullable=False,
    )

    # Set up a back-reference to the User model
    # This allows access to the user who submitted the feedback
    # via feedback.user


