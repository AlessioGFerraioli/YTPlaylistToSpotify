import spotipy
from spotipy.oauth2 import SpotifyOAuth
import json


class SpotifyPlaylistManager:
    def __init__(self, client_id, client_secret, redirect_url="http://127.0.0.1:8000/callback"):

        # scopes per modificare e creare playslti
        scope = "playlist-modify-public playlist-modify-private user-library-read"

        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_url,
            scope=scope
        ))

        # salva id utente
        self.user_id = self.sp.current_user()["id"]
        print(f"Autentcato come: {self.sp.current_user()['display_name']} (ID: {self.user_id})")

    def create_playlist(self, name, description="", public=True):

        try:
            playlist = self.sp.user_playlist_create(
                user=self.user_id,
                name=name,
                public=public,
                description=description
            )

            print(f"Playlsit {name} creata.")
            print(f"iD: {playlist['id']}")
            print(f"URL: {playlist['external_urls']['spotify']}")

            return playlist
        
        except Exception as e:
            print(f"Errore creazione playlist: {e}")
            return None
        

with open('params.json') as f:
    params = json.load(f)

client_id = params["client_id"]
client_secret = params["client_secret"]

manager = SpotifyPlaylistManager(client_id, client_secret)

print("\ncreo playlist vuota")
my_playlist = manager.create_playlist(
    name="Test-Playlist-Python",
    description="Creata con Python e Spotify API",
    public=True
)