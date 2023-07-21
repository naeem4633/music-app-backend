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
from rest_framework.decorators import api_view

@api_view(['GET'])
def getAuthURL(request, format=None):
        print("AuthURL get function called")
        scopes = 'user-read-playback-state user-modify-playback-state user-read-currently-playing streaming playlist-read-private playlist-read-collaborative'

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

@api_view(['GET'])
def isAuthenticated(request, format=None):
        # print("isAuthenticated get function called")
        # print("session_key in isAuth: " + str(self.request.session.session_key))
        is_authenticated = is_spotify_authenticated(request.session.session_key)
        return Response({'status': is_authenticated}, status=status.HTTP_200_OK)

@api_view(['GET'])
def getCurrentSong(request, format=None):
        session_id = request.session.session_key
        endpoint = "me/player/currently-playing"
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
    
@api_view(['GET'])
def getSavedPlaylists(request, format=None):
    session_id = request.session.session_key
    endpoint = "me/playlists"
    response = execute_spotify_api_request(session_id, endpoint)

    if 'error' in response or 'items' not in response:
        return Response({}, status=status.HTTP_204_NO_CONTENT)

    playlists = []
    for playlist in response['items']:
        playlist_id = playlist['id']
        playlist_name = playlist['name']
        playlist_image = playlist['images'][0]['url']
        number_of_songs = playlist['tracks']['total']

        playlist_data = {
            'id': playlist_id,
            'name': playlist_name,
            'image_url': playlist_image,
            'number_of_songs': number_of_songs
        }
        playlists.append(playlist_data)
        # print("saved playlists" + str(playlist_data))

    return Response(playlists, status=status.HTTP_200_OK)


@api_view(['GET'])
def getFeaturedPlaylists(request, format=None):
    session_id = request.session.session_key
    endpoint = "browse/featured-playlists"
    response = execute_spotify_api_request(session_id, endpoint)

    if 'error' in response or 'playlists' not in response:
        print("error in response")
        print(response)
        return Response({}, status=status.HTTP_204_NO_CONTENT)

    playlists = []

    for playlist in response['playlists']['items']:
        playlist_id = playlist['id']
        playlist_name = playlist['name']
        # playlist_description : playlist['description'] if playlist['description'] else None
        playlist_image = playlist['images'][0]['url']
        number_of_songs = playlist['tracks']['total']

        playlist_data = {
            'id': playlist_id,
            'name': playlist_name,
            # 'description' : playlist_description if playlist_description else "",
            'image_url': playlist_image,
            'number_of_songs': number_of_songs
        }

        playlists.append(playlist_data)
        # print("featured playlists" + str(playlist_data))

    return Response(playlists, status=status.HTTP_200_OK)


@api_view(['GET'])
def getSinglePlaylist(request, playlist_id, format=None):
    session_id = request.session.session_key
    endpoint = f"playlists/{playlist_id}"
    response = execute_spotify_api_request(session_id, endpoint)

    if 'error' in response:
        return Response({}, status=status.HTTP_204_NO_CONTENT)

    playlist_data = {
        'name': response.get('name'),
        'description': response.get('description'),
        'image_url': response.get('images')[0].get('url'),
        'followers': response.get('followers').get('total'),
        'songs': []
    }

    # artist_string = ""

    # for i, artist in enumerate(response.get('tracks').get('items').get('track').get('artists')):
    #     if i > 0:
    #         artist_string += ", "
    #     name = artist.get('name')
    #     artist_string += name

    tracks = response.get('tracks').get('items')
    for track in tracks:
        song = {
            'image_url': track.get('track').get('album').get('images')[0].get('url'),
            'name': track.get('track').get('name'),
            'uri': track.get('track').get('uri'),
            'artist': track.get('track').get('artists'),
            'album': track.get('track').get('album').get('name'),
            'duration': track.get('track').get('duration_ms')
        }
        playlist_data['songs'].append(song)

    return Response(playlist_data, status=status.HTTP_200_OK)


@api_view(['PUT'])
def playSong(request, uri, format=None):
    print("playSong function called")
    session_id = request.session.session_key
    endpoint = "me/player/play"

    # Get the device_id from the request data (if available)
    device_id = request.data.get('device_id', None)
    print("uri" + uri)

    # Construct the request body
    request_body = {
        "context_uri":  uri,
        "offset": {"position": 0},
        "position_ms": 0
    }

    # Execute the Spotify API request
    api_response = execute_spotify_api_request(session_id, endpoint, put_=True, data=request_body)

    # Handle the response
    if 'error' in api_response:
        print(api_response)
        return Response({'error': api_response['error']}, status=api_response['status'])
    else:
        return Response(api_response, status=api_response['status'])


@api_view(['GET'])
def getCategorizedPlaylists(request, format=None):
    print("getCategorizedPlaylists function called")
    session_id = request.session.session_key
    endpoint = "browse/categories/rock/playlists"
    response = execute_spotify_api_request(session_id, endpoint)

    if 'error' in response:
        print(response)
        return Response({}, status=status.HTTP_204_NO_CONTENT)

    playlists = []
    for playlist in response['playlists']['items']:
        playlist_id = playlist['id']
        playlist_name = playlist['name']
        playlist_image = playlist['images'][0]['url']
        number_of_songs = playlist['tracks']['total']

        playlist_data = {
            'id': playlist_id,
            'name': playlist_name,
            'image_url': playlist_image,
            'number_of_songs': number_of_songs
        }
        playlists.append(playlist_data)

    return Response(playlists, status=status.HTTP_200_OK)
