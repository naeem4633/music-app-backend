from django.urls import path, include
from . import views

urlpatterns = [
    path('liked-songs/<int:pk>', views.get_liked_songs),
    path('playlists/<int:pk>', views.get_user_playlists),
    path('register/', views.register_user),
    path('users/', views.get_all_users),
    path('users/delete/<int:pk>/', views.delete_user),
    path('playlists/create/', views.create_playlist),
    path('playlists/', views.get_all_playlists),
    path('songs/', views.get_all_songs),
    path('add-liked-song/<int:pk>/', views.add_liked_song),
    path('create-playlist/', views.create_playlist),
    path('get-songs-in-playlist/<int:pk>/', views.get_songs_in_playlist),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
]