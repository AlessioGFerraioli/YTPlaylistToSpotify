import spotipy
from spotipy.oauth2 import SpotifyOAuth
import json
from spotify_searcher import SpotifySearcher

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

        # inizializza il searcher
        self.searcher = SpotifySearcher(client_id, client_secret)

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
        
    def add_tracks_to_playlist(self, playlist_id, track_ids):
        '''
        aggiunga una traccia a una playlist
        returns true se ha successo
        
        '''
        if isinstance(track_ids, str): # se è una signola canzone ho una stringa invece che lista, converto in lista
            track_ids = [track_ids]
        
        track_uris = []        
        for track_id in track_ids:
            # utilizza lo uri che è spotify:track:track_id
            if track_id.startswith('spotify:track:'):
                track_uris.append(track_id)
            else:
                track_uris.append(f"spotify:track:{track_id}")
            
            print("Track uris list created: ", track_uris)
            print("Provo ad aggiungere alla playlist ID ", playlist_id)
        try:
            self.sp.playlist_add_items(playlist_id, track_uris)
            print(f"{len(track_uris)} tracce aggiunte alla playlist.")
            return True
        except Exception as e:
            print("Errore nell'aggiungere traccia: {e}")
            return False
        
    def get_track_id(self, query_title, query_artist=None, query_duration=None, duration_err=1000, limit=20):
        track, flags = self.searcher.get_best_match(query_title, query_artist, query_duration, duration_err=duration_err, limit=limit)
        return track["id"]

    def search_and_add(self, playlist_id):
        track_id = self.get_track_id("old enough", "long stay", 236000)
        print("Track id trovato:", track_id)
        self.add_tracks_to_playlist(playlist_id, track_id)

    def create_playlist_from_search(self):
        playlist = self.create_playlist("test_aggiunta_debug6", "test playlist dove aggiungo una canzone cercata da python")
        self.search_and_add(playlist["id"])

                


with open('params.json') as f:
    params = json.load(f)

client_id = params["client_id"]
client_secret = params["client_secret"]

manager = SpotifyPlaylistManager(client_id, client_secret)

print("\ncreo playlist con una canzone")
my_playlist = manager.create_playlist_from_search()