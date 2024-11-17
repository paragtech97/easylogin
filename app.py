from flask import Flask, redirect, url_for, session
from flask_oauthlib.client import OAuth
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()

app = Flask(__name__)

# Secret key for session management (from .env)
app.secret_key = os.getenv('SECRET_KEY')

# Initialize OAuth object
oauth = OAuth(app)

# Register Google OAuth with credentials from .env
google = oauth.remote_app(
    'google',
    consumer_key=os.getenv('GOOGLE_CLIENT_ID'),  # Client ID from .env
    consumer_secret=os.getenv('GOOGLE_CLIENT_SECRET'),  # Client Secret from .env
    request_token_params={
        'scope': 'email',
    },
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)

@app.route('/')
def index():
    return 'Welcome to EasyLogin! <a href="/login">Login with Google</a>'

@app.route('/login')
def login():
    return google.authorize(callback=url_for('authorized', _external=True))

@app.route('/auth')
def authorized():
    response = google.authorized_response()
    if response is None or response.get('access_token') is None:
        return 'Access denied: reason={} error={}'.format(
            request.args.get('error', 'No reason provided'),
            request.args.get('error_description', 'No description provided')
        )
    
    session['google_token'] = (response['access_token'], '')
    user_info = google.get('userinfo')
    session['user'] = user_info.data
    return f"Logged in as: {user_info.data['email']}"

@app.route('/logout')
def logout():
    session.pop('user', None)  # Remove user from the session
    return redirect(url_for('index'))  # Redirect to the homepage

# To handle Google token for session
@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')

if __name__ == '__main__':
    app.run(debug=True)