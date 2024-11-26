from flask import Flask, redirect, url_for, session, request
from authlib.integrations.flask_client import OAuth
import os

# Initialize Flask app
app = Flask(__name__)

# Load the secret key and Google OAuth credentials from environment variables
app.secret_key = os.getenv('SECRET_KEY')  # SECRET_KEY should be set in Render's environment variables

# Validate environment variables (make sure they are set correctly in Render's environment)
if not app.secret_key:
    raise ValueError("SECRET_KEY is not set in the environment variables.")
if not os.getenv('GOOGLE_CLIENT_ID') or not os.getenv('GOOGLE_CLIENT_SECRET'):
    raise ValueError("Google OAuth credentials are missing in the environment variables.")

# Initialize OAuth
oauth = OAuth(app)

# Register Google OAuth with credentials from environment variables
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
    # Make sure the redirect URI matches the one you registered in Google Developer Console
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
    # Render will automatically handle starting the app; no need for app.run()
    pass