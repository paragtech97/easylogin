from flask import Flask, redirect, url_for, session, request
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv(r'D:\Panoroma\Projects\EasyLogin.env')  # Use raw string for Windows path

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')  # Load SECRET_KEY from .env

# Validate environment variables
if not app.secret_key:
    raise ValueError("SECRET_KEY is not set in the .env file.")
if not os.getenv('GOOGLE_CLIENT_ID') or not os.getenv('GOOGLE_CLIENT_SECRET'):
    raise ValueError("Google OAuth credentials are missing in the .env file.")

# Initialize OAuth
oauth = OAuth(app)

# Register Google OAuth with credentials from .env
google = oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    client_kwargs={'scope': 'email profile'},
)

@app.route('/')
def index():
    return 'Welcome to EasyLogin! <a href="/login">Login with Google</a>'

@app.route('/login')
def login():
    redirect_uri = url_for('authorized', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/auth')
def authorized():
    token = google.authorize_access_token()
    if token is None:
        error_message = request.args.get('error', 'Unknown error')
        return f"Authorization failed: {error_message}"
    session['user'] = google.get('userinfo').json()
    return f"Logged in as: {session['user']['email']}"

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=10000)