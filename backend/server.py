from flask import Flask, session, redirect, url_for, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import os
import openai
from flask_cors import CORS
from geopy.geocoders import Nominatim  # For converting latitude + longitude
from wiki_scraper import fetch_wikipedia_page
from gpt_prompt_maker import gpt_prompt_maker
from sentiment_analysis import analyze_sentiment
from sentiment_prompt import generate_sentiment_prompt
import bcrypt
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import secrets
import random
import re
from datetime import datetime

# Initialize Flask and SQLAlchemy
app = Flask(__name__) 

CORS(app, supports_credentials=True, resources={
    r"/*": {
        "origins": ["http://localhost:3000"],  # Replace with your frontend URL
        "methods": ["GET", "POST", "OPTIONS", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"],
    }
})
# App Configuration
database_uri = os.getenv(
    "SQLALCHEMY_DATABASE_URI", 
    "postgresql://phantom_user:secret_password@db:5432/phantom_db"  # Default URI if env var is missing
)

# Debugging: Check if database URI is correctly set
if not database_uri:
    print("ERROR: SQLALCHEMY_DATABASE_URI is not set!")
else:
    print(f"Using database URI: {database_uri}")

app.config["SQLALCHEMY_DATABASE_URI"] = database_uri
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = os.getenv("FLASK_SECRET_KEY", "default_secret_key")

# Initialize SQLAlchemy
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    confirmation_code = db.Column(db.String(6))
    is_email_verified = db.Column(db.Boolean, default=False)
    reset_token = db.Column(db.String(256))

    # Relationship with Conversation
    conversations = db.relationship('Conversation', backref='user', lazy=True)

class Ghost(db.Model):
    __tablename__ = "ghosts"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    prompt = db.Column(db.Text, nullable=False)
    city = db.Column(db.String(80))
    state = db.Column(db.String(80))
    image_url = db.Column(db.String(200))

class Conversation(db.Model):
    __tablename__ = 'conversations'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    ghost_name = db.Column(db.String(255), nullable=False, default="Unknown")  # Ensure ghost_name exists
    chat_log = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(255), nullable=True)  # Add location column
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)



# Define your routes here
@app.route("/")
def welcome_page():
    """Display the welcome page if the user is not logged in."""
    if "user_id" not in session:
        return redirect(url_for("login"))
    return redirect(url_for("home"))
#
@app.route("/home")
def home():
    """Homepage - Only accessible if logged in."""
    if "user_id" not in session:
        return redirect(url_for("login"))  # Redirect to login if not authenticated
    return "Welcome to the Home Page!"  # Replace this with your actual homepage content

#

#
#
@app.route("/send-confirmation-email", methods=["POST"])
def send_confirmation_email():
    # Extract email from the request payload
    data = request.json
    recipient = data.get("email")

    if not recipient:
        return jsonify({"error": "Recipient email address is required"}), 400

    try:
        # Generate a 6-digit confirmation code
        confirmation_code = str(random.randint(100000, 999999))

        # Create email content
        msg = MIMEText(f"Your Phantom-Link confirmation code is: {confirmation_code}")
        msg["Subject"] = "Phantom-Link Confirmation Code"
        sender = "no-reply@phantom-link.com"
        msg["From"] = sender
        msg["To"] = recipient

        # Connect to Zoho SMTP server
        with smtplib.SMTP_SSL("smtp.zoho.com", 465) as server:
            server.login(sender, "")  
            server.sendmail(sender, recipient, msg.as_string())

        # Save confirmation code to the database
        user = User.query.filter_by(email=recipient).first()
        if user:
            user.confirmation_code = confirmation_code
            db.session.commit()

        return jsonify({"message": f"Confirmation email sent to {recipient}"}), 200

    except smtplib.SMTPAuthenticationError as auth_error:
        return jsonify({"error": f"Authentication failed: {auth_error}"}), 401
    except smtplib.SMTPException as smtp_error:
        return jsonify({"error": f"SMTP error occurred: {smtp_error}"}), 500
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500


@app.route("/verify-email", methods=["POST"])
def verify_email():
    data = request.json
    email = data.get("email")
    code = data.get("confirmation_code")

    if not all([email, code]):
        return jsonify({"error": "Email and confirmation code are required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    if user.confirmation_code == code:
        user.is_email_verified = True  # Mark email as verified
        user.confirmation_code = None  # Clear the confirmation code
        db.session.commit()
        return jsonify({"message": "Email verified successfully!"}), 200
    else:
        return jsonify({"error": "Invalid confirmation code"}), 400
# -------------------
# Configuration
# -------------------

# OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")
if openai.api_key is None:
    raise ValueError("OpenAI API key is not set")

# Geolocator initialization
geolocator = Nominatim(user_agent="phantomlink")


@app.route("/register", methods=["POST"])
def register_user():
    data = request.json
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not all([username, email, password]):
        return jsonify({"error": "All fields are required"}), 400

    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters long"}), 400

    hashed_password_bytes = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    hashed_password_str = hashed_password_bytes.decode("utf-8")  # Decode hashed password to UTF-8 string
    confirmation_code = f"{secrets.randbelow(1000000):06}"  # Generate a 6-digit code

    try:
        # Check for existing username
        if User.query.filter_by(username=username).first():
            return jsonify({"error": "The username is already taken. Please choose another."}), 400

        # Check for existing email
        if User.query.filter_by(email=email).first():
            return jsonify({"error": "The email is already registered. Please use a different email."}), 400

        # Create a new user
        new_user = User(
            username=username,
            email=email,
            password=hashed_password_str,
            confirmation_code=confirmation_code,
            is_email_verified=False
        )
        db.session.add(new_user)
        db.session.commit()

        return jsonify({"message": "User registered successfully. Please confirm your email."}), 201

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500




@app.route("/api/forgot-password", methods=["POST"])
def forgot_password():
    data = request.json
    email = data.get("email")

    if not email:
        return jsonify({"error": "Email is required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "No user found with this email"}), 404

    try:
        # Generate a unique token (reset link)
        reset_token = secrets.token_urlsafe(16)
        reset_link = f"http://localhost:3000/reset-password?token={reset_token}"

        # Save the reset token in the database (for verification later)
        user.reset_token = reset_token
        db.session.commit()

        # Send email with the reset link and include the username
        msg = MIMEText(f"Your Username is - {user.username}\n\nClick the link below to reset your password:\n\n{reset_link}")
        msg["Subject"] = "Password Reset - Phantom-Link"
        sender = "no-reply@phantom-link.com"
        msg["From"] = sender
        msg["To"] = email

        with smtplib.SMTP_SSL("smtp.zoho.com", 465) as server:
            server.login(sender, "")
            server.sendmail(sender, email, msg.as_string())

        return jsonify({"message": "Password reset link sent to your email"}), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

    

from flask import request, jsonify

@app.route("/api/reset-password", methods=["POST"])
def reset_password():
    data = request.json
    token = data.get("token")
    new_password = data.get("password")

    if not token or not new_password:
        return jsonify({"error": "Token and new password are required"}), 400

    user = User.query.filter_by(reset_token=token).first()
    if not user:
        return jsonify({"error": "Invalid or expired reset token"}), 400

    try:
        # Hash the new password
        hashed_password_bytes = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt())
        hashed_password_str = hashed_password_bytes.decode("utf-8")

        # Update the user's password and clear the reset token
        user.password = hashed_password_str
        user.reset_token = None
        db.session.commit()

        return jsonify({"message": "Password reset successfully"}), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500




# --------------------------
# NEW ENDPOINT: Check session
# --------------------------
@app.route("/api/me", methods=["GET"])
def get_user_session():
    """
    Returns the current logged-in user's username if any.
    Otherwise, returns {"username": None}.
    """
    user_id = session.get("user_id")
    if user_id:
        user = User.query.get(user_id)
        if user:
            return jsonify({"username": user.username})
    return jsonify({"username": None})


@app.route("/api/login", methods=["POST", "OPTIONS"])
def login():
    if request.method == "OPTIONS":
        
        # Handle preflight request
        response = jsonify({"message": "Preflight request handled"})
        response.headers.add("Access-Control-Allow-Origin", "http://localhost:3000")
        response.headers.add("Access-Control-Allow-Credentials", "true")
        response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type")
        return response, 200

    # Handle POST request
    data = request.json
    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"error": "Invalid username or password"}), 401

    # Check email verification status
    if not user.is_email_verified:
        # Send the confirmation email if the email is not verified
        send_confirmation_email()
        
        # Return error message and redirect URL for verification
        return jsonify({
            "error": "Email not verified. Please verify your email.",
            "is_email_verified": False,
            "email": user.email,
            "redirect_url": "/verify"  # Return URL for frontend to handle redirection
        }), 403

    # Verify the user's password
    if bcrypt.checkpw(password.encode("utf-8"), user.password.encode("utf-8")):
        session["user_id"] = user.id  # Save user ID in the session
        response = jsonify({"message": "Login successful", "is_email_verified": True})
        response.headers.add("Access-Control-Allow-Origin", "http://localhost:3000")
        response.headers.add("Access-Control-Allow-Credentials", "true")
        return response, 200

    # If the password is incorrect
    return jsonify({"error": "Invalid username or password"}), 401

@app.route("/api/logout", methods=["POST"])
def logout():
    """
    Clears the user session to log out the current user.
    """
    session.clear()
    return jsonify({"message": "Logged out"}), 200
# -------------------
# -------------------
# -------------------
# -------------------
# -------------------

# OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

#This is for the chat session
app.secret_key = os.getenv("FLASK_SECRET_KEY", "default_secret_key")
print(f"Using secret key: {app.secret_key}")

# Configure session cookie settings
app.config.update(
    SESSION_COOKIE_NAME='phantomlink_session',  
    SESSION_COOKIE_SAMESITE='Lax',  
    SESSION_COOKIE_SECURE=False,  
    PERMANENT_SESSION_LIFETIME=3600  
)


# Check if the OpenAI API key is set
if openai.api_key is None:
    raise ValueError("OpenAI API key is not set")

# Initialize the geolocator
geolocator = Nominatim(user_agent="phantomlink")

# Variable to store the last city found
last_city = None
last_state = None  # Store the last known state if available

@app.before_request
def reset_sentiment():
    """Reset the user sentiment when a new session starts."""
    if 'user_sentiment' not in session:
        session['user_sentiment'] = 0  # Initialize sentiment score


@app.route("/chat", methods=["POST"])
def chat():
    global last_city, last_state
    data = request.json
    user_message = data.get("message")

    # Initialize the conversation in session if not already set
    if 'conversation' not in session:
        print("No conversation in session, initializing.")
        session['conversation'] = [{"role": "system", "content": f"Pretend you are a ghost from {last_city}, {last_state}, you are talking to a modern-day person."}]
        session['user_sentiment'] = 0  # Initialize sentiment score
        session['gpt_prompt_applied'] = False  # Track if the custom GPT prompt has been applied
        session['ghost_name'] = "Unknown Ghost"  # Initialize ghost name
        print(f"Initialized session conversation: {session['conversation']}")

    # Debugging: Check session before proceeding
    print(f"Session before conversation: {session.get('conversation')}")

    # Update sentiment based on the user's message
    sentiment = analyze_sentiment(user_message)
    session['user_sentiment'] += sentiment  # Update the sentiment score in session
    print(f"Updated user sentiment: {session['user_sentiment']}")

    # Apply GPT prompt only if the sentiment score is >= 2 and not already applied
    if session['user_sentiment'] >= 2 and not session.get('gpt_prompt_applied'):
        # Fetch data from Wikipedia scraper
        result, paragraphs = fetch_wikipedia_page(last_city, last_state)
        if result:
            name, birth_year, death_year, occupation = result
            prompt = gpt_prompt_maker(name, birth_year, death_year, occupation, paragraphs)
            session['ghost_name'] = name  # Store ghost name in session
        else:
            prompt = f"Pretend you are a ghost from {last_city}, {last_state}, you are talking to a modern-day person."

        session['conversation'][0]["content"] = prompt
        session['gpt_prompt_applied'] = True  # Mark the custom GPT prompt as applied
        print(f"Applied GPT prompt: {prompt}")

    # Add the user's message to the conversation
    session['conversation'].append({"role": "user", "content": user_message})
    print(f"Added user message to session: {session['conversation']}")

    try:
        # Call OpenAI API with the updated conversation
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=session['conversation'],
            temperature=1,
        )
        reply = response.choices[0].message["content"]

        # Add the ghost's response to the conversation
        session['conversation'].append({"role": "assistant", "content": reply})
        print(f"Assistant reply added to session: {session['conversation']}")

        return jsonify({"reply": reply}), 200  # Success response
    except openai.error.RateLimitError:
        return jsonify({"error": "Rate limit exceeded. Please try again later."}), 429
    except openai.error.InvalidRequestError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "An internal error occurred."}), 500


@app.route("/end-conversation", methods=["POST"])
def end_conversation():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "User not logged in"}), 401  # Return error if user is not logged in

    try:
        # Ensure conversation exists in session
        if 'conversation' not in session:
            return jsonify({"error": "No conversation in session"}), 400

        # Get the conversation data from the session
        conversation_data = session['conversation']

        # Retrieve ghost name from the session
        ghost_name = session.get("ghost_name", "Unknown Ghost")

        # Get the location from global variables
        global last_city, last_state
        location = f"{last_city}, {last_state}" if last_city and last_state else "Unknown Location"

        # Filter out system messages and process the roles
        filtered_messages = [
            {
                "sender": "User" if message['role'] == "user" else "Ghost",
                "content": message['content']
            }
            for message in conversation_data
            if message['role'] in ["user", "assistant"]  # Include only user and assistant roles
        ]

        # Combine messages into a single chat log
        chat_log = "\n".join(
            [f"{message['sender']}: {message['content']}" for message in filtered_messages]
        )

        # Insert the new conversation into the database
        new_conversation = Conversation(
            user_id=user_id,
            ghost_name=ghost_name,
            chat_log=chat_log,
            location=location,  # Save the location
            timestamp=datetime.utcnow()
        )
        db.session.add(new_conversation)
        db.session.commit()

        # Clear the conversation and ghost name from the session
        session.pop("conversation", None)
        session.pop("ghost_name", None)

        return jsonify({"message": "Conversation saved successfully."}), 200
    except Exception as e:
        db.session.rollback()  # Rollback in case of error
        print(f"Error occurred while saving conversation: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500





@app.route("/api/conversations", methods=["GET"])
def get_conversations():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "User not logged in"}), 401

    try:
        # Fetch conversations for the logged-in user
        conversations = Conversation.query.filter_by(user_id=user_id).all()

        conversations_data = []
        for conversation in conversations:
            # Retrieve the ghost's name using the ghost_id
            ghost = Ghost.query.get(conversation.ghost_id)
            ghost_name = ghost.name if ghost else "Unknown Ghost"
            conversations_data.append({
                "ghost_name": ghost_name,
                "message": conversation.message,
                "timestamp": conversation.timestamp
            })

        return jsonify({"conversations": conversations_data}), 200
    except Exception as e:
        return jsonify({"error": f"Error retrieving conversations: {str(e)}"}), 500

    
@app.route("/error")
def error_page():
    return jsonify({"error": "City and state information are required."}), 400


@app.route("/api/reset-session", methods=["POST"])
def reset_session():
    print("Resetting session...")  # Debug print

    # Keep the user logged in, but reset the conversation
    session.pop("conversation", None)  # Remove the conversation from the session
    session.pop("user_sentiment", None)  # Optionally reset any other relevant session state

    # Create a response without logging the user out
    response = jsonify({"message": "Session reset successful, starting new ghost conversation."})

    print("Session after reset:", session)  # Debug: Should not clear the user info, only conversation state

    return response


# New endpoint to receive location data and convert to city name
@app.route("/api/location", methods=["POST"])
def receive_location():
    global last_city, last_state
    data = request.json
    latitude = data.get("latitude")
    longitude = data.get("longitude")
    location_allowed = data.get("location_allowed")

    if latitude is None or longitude is None:
        return jsonify({"error": "Latitude and longitude are required."}), 400

    try:
        # Convert latitude and longitude to a city name using geopy
        location = geolocator.reverse((latitude, longitude), exactly_one=True)
        if location and location.raw.get("address"):
            city = location.raw["address"].get("city", "an unknown place")
            state = location.raw["address"].get("state", None)
            last_city = city  # Store the last found city
            last_state = state  # Store the last found state
            print(f"Determined city from coordinates: {city}, {state}")
        else:
            city = "an unknown place"
            state = None
            last_city = None  #1 Clear if not found
            last_state = None
            print("Could not determine a city from coordinates.")

        return jsonify({
            "message": f"Location received successfully. latitude={latitude}, longitude={longitude}, city={city}, state={state}"
        }), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred while processing location data: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)