from django.urls import path
from .views import * 

urlpatterns = [
    path('get-auth-url', getAuthURL),
    path('redirect', spotify_callback),
    path('is-authenticated', isAuthenticated),
    path('current-song', getCurrentSong),
    path('get-saved-playlists', getSavedPlaylists),
    path('get-playlist/<str:playlist_id>', getSinglePlaylist),
    path('play-track/<str:uri>', playSong),
    path('get-featured-playlists', getFeaturedPlaylists),
    path('get-categorized-playlists', getCategorizedPlaylists),
]