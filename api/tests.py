from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from .models import Song, Playlist

User = get_user_model()

class SongModelTestCase(TestCase):
    def setUp(self):
        self.song = Song.objects.create(title='Song Title', artist='Artist Name')

    def test_song_str_representation(self):
        self.assertEqual(str(self.song), 'Song Title')

class PlaylistModelTestCase(TestCase):
    def setUp(self):
        self.playlist = Playlist.objects.create(name='Playlist Name', description='Playlist Description')

    def test_playlist_str_representation(self):
        self.assertEqual(str(self.playlist), 'Playlist Name')

class CustomUserAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_user_login(self):
        url = reverse('login') 
        data = {'username': 'testuser', 'password': 'testpassword'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('sessionid' in self.client.session)

    def test_user_logout(self):
        url = reverse('logout') 
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse('sessionid' in self.client.session)

