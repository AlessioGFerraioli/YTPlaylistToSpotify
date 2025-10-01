import spotipy
from spotipy.oauth2 import SpotifyOAuth
import json
from spotify_searcher import SpotifySearcher
from yt_playlist_scraper import YTPlaylistScraper
import time

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
        aggiunga tracce a una playlist
        spotify api ha un limite di 100 tracce per chiamata API, quindi le divido in batch da max
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
            
            # print("Track uris list created.") # debug
            # print("Provo ad aggiungere alla playlist..", playlist_id) debug

            # divido le tracce in batch da 100
            batch_size = 100 
            batches = [track_uris[i:i+batch_size] for i in range(0, len(track_uris), batch_size)] 
        try:
            total_n_tracks_aggiunte = 0
            for track_uris in batches:
                self.sp.playlist_add_items(playlist_id, track_uris)
                total_n_tracks_aggiunte += len(track_uris)
                time.sleep(2) #una piccola pausa per non fare impressionare l'api di spotify
            print(f"{total_n_tracks_aggiunte} tracce aggiunte alla playlist.")    
            return True
        except Exception as e:
            print("Errore nell'aggiungere le tracce: {e}")
            return False
        
    def get_track_id(self, query_title, query_artist=None, query_duration=None, duration_err=1000, limit=20):
        track, flags = self.searcher.get_best_match(query_title, query_artist, query_duration, duration_err=duration_err, limit=limit)
        return track["id"]

    def search_and_add(self, playlist_id, queries, print_query=True):
        track_ids = []
        i = 0
        for query in queries:
            if print_query:
                print("___________________________________________")
                print()
                print(i+1)
                print("CURRENT QUERY: ")
                print(f"Title: {query['title']}")
                print(f"Artist: {query['artist']}")
                print(f"Duration: {query['duration']}")
                print()
                i += 1
            track_ids.append(self.get_track_id(query["title"], query["artist"], query["duration"]))

        self.add_tracks_to_playlist(playlist_id, track_ids)

    def create_playlist_from_search(self, queries, name, description=''):
        playlist = self.create_playlist(name, description)
        self.search_and_add(playlist["id"], queries)
        return playlist
    
    def get_queries_from_YTplaylist(self, YT_playlist_url):
        scraper = YTPlaylistScraper(YT_playlist_url)
        playlist_info, videos_info = scraper.get_playlist_info()
        # crea queries da videos_info
        queries = []
        for video in videos_info:
            query = {
                "title" : video["title"],
                "duration" : video["duration"]
            }
            query["artist"] = video.get("artist", None) # se non ci sono artisti, lascia "None" come artist, che verra gestito dallo spotify searcher
            queries.append(query)
        return queries, playlist_info
    
    def create_playlist_from_YTplaylist(self, YT_playlist_url, name=None, description=None):
        '''
        takes a yt playlist url, fetches the data with YTPlaylistScraper, and creates a n ew playlsit of the same
        name of the yt playlist with create_playlist_from_search
        '''
        # get information aabout the videos in the yt playlsit and about the playlist
        queries, playlist_info = self.get_queries_from_YTplaylist(YT_playlist_url)
        if name is None:
            name = playlist_info["title"]
        if description is None:
            description = f"Automatic porting to Spotify of a playlist called '{name}' created by {playlist_info['author']}"

        # create playlsit and add the songs
        playlist = self.create_playlist_from_search(queries, name, description)    
        return playlist
        
                


with open('params.json') as f:
    params = json.load(f)

client_id = params["client_id"]
client_secret = params["client_secret"]
#yt_playlist_url = params["yt_playlist_url"]


yt_playlist_url = input("Inserire YT playlist url: ")
print("\nCreo playlist spotify da playlist YT..")
manager = SpotifyPlaylistManager(client_id, client_secret)
manager.create_playlist_from_YTplaylist(yt_playlist_url)