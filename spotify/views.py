from django.shortcuts import render
from .credentials import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from requests import Request, post
from .models import SpotifyToken
from django.shortcuts import redirect
from .utils import get_user_tokens, is_spotify_authenticated, refresh_spotify_token, execute_spotify_api_request
from datetime import datetime, timedelta
from django.utils import timezone

class AuthURL(APIView):
    def get(self, request, format=None):
        print("AuthURL get function called")
        scopes = 'user-read-playback-state user-modify-playback-state user-read-currently-playing'

        url = Request('GET', 'https://accounts.spotify.com/authorize', params={
            'scope': scopes,
            'response_type': 'code',
            'redirect_uri': REDIRECT_URI,
            'client_id': CLIENT_ID
        }).prepare().url

        return Response({'url': url}, status=status.HTTP_200_OK)

def spotify_callback(request, format=None):

    code = request.GET.get('code')
    print("code from url: " + code)
    error = request.GET.get('error')
    response = post('https://accounts.spotify.com/api/token', data={
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }).json()
    access_token = response.get('access_token')
    token_type = response.get('token_type')
    refresh_token = response.get('refresh_token')

    expires_in = response.get('expires_in')
    expires_at = timezone.now() + timedelta(seconds=int(expires_in))

    error = response.get('error')
    # print("session_key in spotify callback: " + str(request.session.session_key))
    if not request.session.exists(request.session.session_key):
        request.session.create()
        SpotifyToken.objects.update_or_create(
            user=request.session.session_key,
            defaults={
                'access_token': access_token,
                'token_type': token_type,
                'expires_in': expires_at,
                'refresh_token': refresh_token
            }
        )
        request.session.modified = True
    return redirect('http://127.0.0.1:8000/')

class IsAuthenticated(APIView):
    def get(self, request, format=None):
        # print("isAuthenticated get function called")
        # print("session_key in isAuth: " + str(self.request.session.session_key))
        is_authenticated = is_spotify_authenticated(self.request.session.session_key)
        return Response({'status': is_authenticated}, status=status.HTTP_200_OK)

class CurrentSong(APIView):
    def get(self, request, format=None):
        session_id = self.request.session.session_key
        endpoint = "player/currently-playing"
        response = execute_spotify_api_request(session_id, endpoint)

        if 'error' in response or 'item' not in response:
            return Response({}, status=status.HTTP_204_NO_CONTENT)

        item = response.get('item')
        duration = item.get('duration_ms')
        progress = response.get('progress_ms')
        album_cover = item.get('album').get('images')[0].get('url')
        is_playing = response.get('is_playing')
        song_id = item.get('id')

        artist_string = ""

        for i, artist in enumerate(item.get('artists')):
            if i > 0:
                artist_string += ", "
            name = artist.get('name')
            artist_string += name

        song = {
            'title': item.get('name'),
            'artist': artist_string,
            'duration': duration,
            'progress': progress,
            'image_url': album_cover,
            'is_playing': is_playing,
            'votes': 0,
            'id': song_id
        }

        return Response(song, status=status.HTTP_200_OK)