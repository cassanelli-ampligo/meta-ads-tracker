import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

client_id = '55ab58c295f64c74ae147c1f7a2583bc' 
client_secret = '2efddfec41bd4954b2223123d157259f'  

# Initialize Spotipy with Spotify Developer credentials
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def get_playlist_details(playlist_id):
    playlist = sp.playlist(playlist_id)
    name = playlist['name']
    image_url = playlist['images'][0]['url'] if playlist['images'] else None
    return name, image_url