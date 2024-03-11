import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import streamlit as st


client_id = st.secrets["spotify_client_id"]
client_secret = st.secrets["spotify_client_secret"]

# Initialize Spotipy with Spotify Developer credentials
client_credentials_manager = SpotifyClientCredentials(
    client_id=client_id, client_secret=client_secret
)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


def get_playlist_details(playlist_id):
    playlist = sp.playlist(playlist_id)
    name = playlist["name"]
    image_url = playlist["images"][0]["url"] if playlist["images"] else None
    return name, image_url
