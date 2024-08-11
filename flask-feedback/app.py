"""Feedback Flask app."""

from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from werkzeug.exceptions import Unauthorized

from models import connect_db, db, User, Feedback
from forms import RegisterForm, LoginForm, FeedbackForm, DeleteForm

# Create a new Flask application instance
app = Flask(__name__)

# Configuration settings for the Flask app
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///flask-feedback"  # Database URI for SQLAlchemy
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable modification tracking to save resources
app.config['SQLALCHEMY_ECHO'] = True  # Enable SQL query logging (useful for debugging)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "your_default_secret_key")  # Use environment variable for secret key
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False  # Allow redirects to occur without interruption by the debug toolbar

# Initialize the debug toolbar
toolbar = DebugToolbarExtension(app)

# Connect the database to the Flask app
connect_db(app)


@app.route("/")
def homepage():
    """Homepage route; redirect to the registration page."""
    return redirect("/register")


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration: show registration form and process form submission."""

    # Redirect to user's page if already logged in
    if "username" in session:
        return redirect(f"/users/{session['username']}")

    form = RegisterForm()  # Instantiate the registration form

    if form.validate_on_submit():
        # Extract data from the form
        username = form.username.data
        password = form.password.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data

        try:
            # Register the user and add to the database
            user = User.register(username, password, first_name, last_name, email)
            db.session.commit()  # Commit changes to the database
            session['username'] = user.username  # Store username in session
            return redirect(f"/users/{user.username}")  # Redirect to the user's profile page
        except Exception as e:
            db.session.rollback()  # Rollback in case of error
            flash("An error occurred while registering. Please try again.", "error")
            print(f"Error: {e}")

    # Render the registration form if not submitted or validation failed
    return render_template("users/register.html", form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login: show login form and process form submission."""

    # Redirect to user's page if already logged in
    if "username" in session:
        return redirect(f"/users/{session['username']}")

    form = LoginForm()  # Instantiate the login form

    if form.validate_on_submit():
        # Extract data from the form
        username = form.username.data
        password = form.password.data

        # Authenticate the user
        user = User.authenticate(username, password)  # Returns User object or False
        if user:
            session['username'] = user.username  # Store username in session
            return redirect(f"/users/{user.username}")  # Redirect to the user's profile page
        else:
            form.username.errors = ["Invalid username/password."]  # Add error message to form
            flash("Invalid username or password. Please try again.", "error")

    # Render the login form if not submitted or validation failed
    return render_template("users/login.html", form=form)


@app.route("/logout")
def logout():
    """Handle user logout."""
    session.pop("username", None)  # Remove username from session
    return redirect("/login")  # Redirect to the login page


@app.route("/users/<username>")
def show_user(username):
    """Display user's profile page if logged in as the correct user."""

    # Check if user is logged in and if they are accessing their own profile
    if "username" not in session or username != session['username']:
        raise Unauthorized()

    user = User.query.get(username)  # Query user by username
    form = DeleteForm()  # Instantiate the delete form

    # Render the user's profile page
    return render_template("users/show.html", user=user, form=form)


@app.route("/users/<username>/delete", methods=["POST"])
def remove_user(username):
    """Handle user deletion and redirect to login page."""

    # Check if user is logged in and if they are deleting their own account
    if "username" not in session or username != session['username']:
        raise Unauthorized()

    user = User.query.get(username)  # Query user by username
    try:
        db.session.delete(user)  # Delete user from database
        db.session.commit()  # Commit changes to the database
        session.pop("username", None)  # Remove username from session
    except Exception as e:
        db.session.rollback()  # Rollback in case of error
        flash("An error occurred while deleting the user. Please try again.", "error")
        print(f"Error: {e}")

    return redirect("/login")  # Redirect to the login page


@app.route("/users/<username>/feedback/new", methods=["GET", "POST"])
def new_feedback(username):
    """Display form to add new feedback and handle form submission."""

    # Check if user is logged in and if they are adding feedback for their own account
    if "username" not in session or username != session['username']:
        raise Unauthorized()

    form = FeedbackForm()  # Instantiate the feedback form

    if form.validate_on_submit():
        # Extract data from the form
        title = form.title.data
        content = form.content.data

        # Create new feedback instance and add to database
        feedback = Feedback(
            title=title,
            content=content,
            username=username,
        )
        try:
            db.session.add(feedback)
            db.session.commit()  # Commit changes to the database
        except Exception as e:
            db.session.rollback()  # Rollback in case of error
            flash("An error occurred while adding feedback. Please try again.", "error")
            print(f"Error: {e}")
            return render_template("feedback/new.html", form=form)

        return redirect(f"/users/{feedback.username}")  # Redirect to the user's profile page

    # Render the feedback form if not submitted or validation failed
    return render_template("feedback/new.html", form=form)


@app.route("/feedback/<int:feedback_id>/update", methods=["GET", "POST"])
def update_feedback(feedback_id):
    """Display form to update feedback and handle form submission."""

    feedback = Feedback.query.get(feedback_id)  # Query feedback by ID

    # Check if user is logged in and if they are updating their own feedback
    if "username" not in session or feedback.username != session['username']:
        raise Unauthorized()

    form = FeedbackForm(obj=feedback)  # Instantiate the feedback form with existing data

    if form.validate_on_submit():
        # Update feedback details
        feedback.title = form.title.data
        feedback.content = form.content.data
        try:
            db.session.commit()  # Commit changes to the database
        except Exception as e:
            db.session.rollback()  # Rollback in case of error
            flash("An error occurred while updating feedback. Please try again.", "error")
            print(f"Error: {e}")
            return render_template("feedback/edit.html", form=form, feedback=feedback)

        return redirect(f"/users/{feedback.username}")  # Redirect to the user's profile page

    # Render the feedback update form
    return render_template("feedback/edit.html", form=form, feedback=feedback)


@app.route("/feedback/<int:feedback_id>/delete", methods=["POST"])
def delete_feedback(feedback_id):
    """Handle feedback deletion."""

    feedback = Feedback.query.get(feedback_id)  # Query feedback by ID

    # Check if user is logged in and if they are deleting their own feedback
    if "username" not in session or feedback.username != session['username']:
        raise Unauthorized()

    form = DeleteForm()  # Instantiate the delete form

    if form.validate_on_submit():
        try:
            db.session.delete(feedback)  # Delete feedback from database
            db.session.commit()  # Commit changes to the database
        except Exception as e:
            db.session.rollback()  # Rollback in case of error
            flash("An error occurred while deleting feedback. Please try again.", "error")
            print(f"Error: {e}")

    return redirect(f"/users/{feedback.username}")  # Redirect to the user's profile page

