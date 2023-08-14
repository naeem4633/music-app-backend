from .models import SpotifyToken
from django.utils import timezone
from datetime import timedelta
from .credentials import CLIENT_ID, CLIENT_SECRET
from requests import post, put,  get


BASE_URL = "https://api.spotify.com/v1/"

def get_user_tokens(session_id):
    # print("sessionId:"+str(session_id))
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
    expires_at = timezone.now() + timedelta(seconds=int(expires_in))
    new_refresh_token = response.get('refresh_token')  # Get the new refresh token if provided
    
    SpotifyToken.objects.update_or_create(
        user=session_id,
        defaults={
            'access_token': access_token,
            'token_type': token_type,
            'expires_in': expires_at,
            'refresh_token': new_refresh_token or refresh_token  # Use the new refresh token if provided, otherwise use the existing one
        }
    )



def execute_spotify_api_request(session_id, endpoint, post_=False, put_=False, data=None):
    tokens = get_user_tokens(session_id)
    # print("tokens access token: " + str(tokens.access_token))
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + tokens.access_token
    }

    if post_:
        response = post(BASE_URL + endpoint, headers=headers, json=data)
    elif put_:
        response = put(BASE_URL + endpoint, headers=headers, json=data)
        print("utils put funtion called")
    else:
        response = get(BASE_URL + endpoint, headers=headers)

    try:
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {'error': str(e), 'status': response.status_code}
    
    
# def play_song(session_id):
#     print("play_song called")
#     return execute_spotify_api_request(session_id, "me/player/play", put_=True)


# def pause_song(session_id):
#     return execute_spotify_api_request(session_id, "me/player/pause", put_=True)