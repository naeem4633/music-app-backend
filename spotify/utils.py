from .models import SpotifyToken
from django.utils import timezone
from datetime import timedelta
from .credentials import CLIENT_ID, CLIENT_SECRET
from requests import post

def get_user_tokens(session_id):
    print("sessionId:"+str(session_id))
    user_tokens = SpotifyToken.objects.filter(user=session_id)
    
    if user_tokens.exists():
        return user_tokens[0]
    else:
        return None

def is_spotify_authenticated(session_id):
    tokens = get_user_tokens(session_id)
    if tokens:
        expiry = tokens.expires_in
        if expiry <= timezone.now():
            print("expired" + expiry)
            refresh_spotify_token(session_id)
        return True
    return False
    
def refresh_spotify_token(session_id):
    refresh_token = get_user_tokens(session_id).refresh_token  
    
    response = post('https://accounts.spotify.com/api/token', data={
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }).json()
    
    access_token = response.get('access_token')
    token_type = response.get('token_type')
    expires_in = response.get('expires_in')
    refresh_token = response.get('refresh_token')
    
    SpotifyToken.objects.update_or_create(
    user=session_id,
    defaults={
        'access_token': access_token,
        'token_type': token_type,
        'expires_in': expires_in,
        'refresh_token': refresh_token
    }
)
