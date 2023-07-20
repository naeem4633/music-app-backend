from rest_framework import serializers
from .models import Song, Playlist, CustomUser
from django.contrib.auth import get_user_model


User = get_user_model()

class SongSerializer(serializers.ModelSerializer):
    class Meta:
        model = Song
        fields = '__all__'

class PlaylistSerializer(serializers.ModelSerializer):
    songs = SongSerializer(many=True, read_only=True)
    class Meta:
        model = Playlist
        fields = '__all__'

class CustomUserSerializer(serializers.ModelSerializer):
    playlists = PlaylistSerializer(many=True, read_only=True)
    liked_songs = SongSerializer(many=True, read_only=True)

    class Meta:
        model = CustomUser
        fields = '__all__'