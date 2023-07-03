from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializers import SongSerializer, PlaylistSerializer, CustomUserSerializer
from .models import CustomUser, Playlist, Song
from django.contrib.auth import authenticate, login, logout


@api_view(['GET'])
def get_liked_songs(request, pk):
    try:
        user = CustomUser.objects.get(pk=pk)  
        liked_songs = user.liked_songs.all()
        serializer = SongSerializer(liked_songs, many=True)
        return Response(serializer.data)
    except CustomUser.DoesNotExist:
        return Response(status=404)

@api_view(['GET'])
def get_user_playlists(request, pk):
    try:
        user = CustomUser.objects.get(pk=pk)
        playlists = user.playlists.all()
        serializer = PlaylistSerializer(playlists, many=True)
        return Response(serializer.data)
    except CustomUser.DoesNotExist:
        return Response(status=404)

@api_view(['GET'])
def all_playlists_view(request):
    playlists = Playlist.objects.all()
    serializer = PlaylistSerializer(playlists, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def register_user(request):
    password = request.data.get('password')
    user = CustomUser()
    user.set_password(password)
    user.first_name = request.data.get('first_name')
    user.last_name = request.data.get('last_name')
    user.username = request.data.get('username')
    user.email = request.data.get('email')
    user.save()

    serializer = CustomUserSerializer(user, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)

@api_view(['POST'])
def login_user(request):
    username = request.data.get('username')
    password = request.data.get('password')

    # user = authenticate(request, username=username, password=password)
    customUser = CustomUser.objects.get(username=username, password=password)

    if customUser is not None:
        login(request, customUser)
        return Response({'message': 'Login successful'})
    else:
        return Response({"error": "Invalid credentials"}, status=401)
    
@api_view(['GET'])
def logout_user(request):
    if request.user.is_authenticated:
        logout(request)  # Logout the user
        return Response({'message': 'Logout successful'})
    else:
        return Response({'message': 'User is not authenticated'}, status=401)

@api_view(['GET'])
def get_all_users(request):
    users = CustomUser.objects.all()
    serializer = CustomUserSerializer(users, many=True)
    return Response(serializer.data)

@api_view(['DELETE'])
def delete_user(request, pk):
    try:
        user = CustomUser.objects.get(pk=pk)
        user.delete()
        return Response(status=204)
    except CustomUser.DoesNotExist:
        return Response(status=404)
    
@api_view(['POST'])
def create_playlist(request):
    name = request.data.get('name')
    description = request.data.get('description')
    songs = request.data.get('songs')
    likes = request.data.get('likes')
    playlist = Playlist(name=name, description=description, likes=likes)
    playlist.save()
    if songs:
        playlist.songs.set(songs)

    serializer = PlaylistSerializer(playlist, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors)

@api_view(['POST'])
def create_song(request):
    title = request.data.get('title')
    artist = request.data.get('artist')
    album = request.data.get('album')
    release_date = request.data.get('release_date')
    genre = request.data.get('genre')
    likes = request.data.get('likes')
    song = Song(title=title, artist=artist, album=album, release_date=release_date, genre=genre, likes=likes)
    song.save()

    serializer = SongSerializer(song, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors)

@api_view(['GET'])
def get_all_playlists(request):
    playlists = Playlist.objects.all()
    serializer = PlaylistSerializer(playlists, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_all_songs(request):
    songs = Song.objects.all()
    serializer = SongSerializer(songs, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def add_liked_song(request):
    song_id = request.data.get('song')
    user_id = request.data.get('user')
    
    try:
        user = CustomUser.objects.get(pk=int(user_id))
        song = Song.objects.get(pk=int(song_id))
        user.liked_songs.add(song)
        return Response(status=200)
    except (CustomUser.DoesNotExist, Song.DoesNotExist):
        return Response(status=404)
    
@api_view(['POST'])
def create_playlist(request):
    playlist_id = request.data.get('playlist')
    user_id = request.data.get('user')
    
    try:
        user = CustomUser.objects.get(pk=int(user_id))
        playlist = Playlist.objects.get(pk=int(playlist_id))
        user.playlists.add(playlist)
        return Response(status=201)
    except (CustomUser.DoesNotExist, Playlist.DoesNotExist):
        return Response(status=404)

@api_view(['GET'])
def get_songs_in_playlist(request, pk):
    try:
        playlist = Playlist.objects.get(pk=pk)
        songs = playlist.songs.all()
        serializer = SongSerializer(songs, many=True)
        return Response(serializer.data)
    except Playlist.DoesNotExist:
        return Response(status=404)