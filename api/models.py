from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class Song(models.Model):
    title = models.CharField(max_length=100)
    artist = models.CharField(max_length=100, null=True, blank=True)
    album = models.CharField(max_length=100, null=True, blank=True)
    release_date = models.DateField(null=True, blank=True)
    genre = models.CharField(max_length=100, null=True, blank=True)
    likes = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.title
    
class Playlist(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100, null=True, blank=True)
    songs = models.ManyToManyField(Song, related_name='playlists', blank=True)
    likes = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name

class CustomUser(AbstractUser):
    playlists = models.ManyToManyField(Playlist, related_name='users', blank=True)
    liked_songs = models.ManyToManyField(Song, related_name='users', blank=True)

    def __str__(self):
        return self.username