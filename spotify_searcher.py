import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import json



class SpotifySearcher:
    def __init__(self, client_id, client_secret):
        """
        inizializza con credenziali
        """

        self.client_credentials_manager = SpotifyClientCredentials(client_id=client_id, 
                                                                   client_secret=client_secret)
        self.sp = spotipy.Spotify(client_credentials_manager=self.client_credentials_manager)

    def search_tracks(self, query, limit=10):
        ''' 
        cerca una traccia su spotify in base alla query
        
        query: keyword da cercare
        limit (int) massimo numero di rulstati

                return: dict risultati ricerca
        '''
        
        try: 
            results = self.sp.search(q=query, type="track", limit=limit)
            return results["tracks"]["items"]
        except Exception as e:
            print("Errore ricerca: ", e)
            return None
              
    def ms_to_min(self, ms):
        '''
        input: time in ms
        output: formatted string for time in min:sec human readable format
        '''
        s = round(ms/1000, 1) # converto da ms a s approssimando (non mi interessano le frazioni di secondo)
        return f"{round(s // 60)}:{round(s % 60):02d}"
     

    def parse_track_info(self, track):
        title = track["name"]
        artists = [artist["name"] for artist in track["artists"]] 
        duration = track["duration_ms"]
        id = track["id"]
        return title, artists, duration, id

    def print_track_info(self, title, artists, duration):
            print("Title: ", title)
            if isinstance(artists, list):
                artists_str = ", ".join(artist for artist in artists)
                print("Artists: ", artists_str)               
            else:
                print("Artist: ", artists)
            print("Duration: ", self.ms_to_min(duration))

    def search_and_display(self, query, limit=10):
        
        print(f'Searching "{query}" tracks..')
        print(f"First {limit} results:")
        print()
        tracks = self.search_tracks(query, limit)

        for i, track in enumerate(tracks):
            print(i+1)
            title, artists, duration, id = self.parse_track_info(track)
            self.print_track_info(title, artists, duration)
            print()


    def get_best_match(self, query_title, query_artist=None, query_duration=None, duration_err=1000, limit=20, print_info=False):
        query = f"{query_title} {query_artist}"

        tracks = self.search_tracks(query, limit)

        best_match_index = 0
        title_match = False
        artist_match = False
        duration_match = False

        for i, track in enumerate(tracks):
            title, artists, duration, id = self.parse_track_info(track)
            if title.lower() == query_title.lower():
                if title_match == False:  # se il titolo corrisponde ma ancora non era stato matchato, assegna questo
                    best_match_index = i
                    title_match = True
                
                # assunto che il titolo corrisponda, controlliamo gli artisti
                if artists is not None:
                    for artist in artists: #controllo artista per artista
                        if query_artist.lower() in artist.lower() or artist.lower() in query_artist.lower(): # se artista corrisponde
                            if artist_match == False: # se non era stato trovato ancora, assegna questo - non mi curo del fatto che piu artisti possono esserci, me ne basta una corrispondeza
                                best_match_index = i
                                artist_match = True
                            # assunto che l'artista corrisponda, controllo la durata
                            if abs(duration - query_duration) <= duration_err: #se la durata corrisponde
                                if duration_match == False:
                                    best_match_index = i
                                    duration_match = True
                            break # una volta che tra tutti gli artisti ho trovato uno che corrisponda è inutile che continui nella lista di artisti della traccia
            
                if abs(duration - query_duration) <= duration_err: #se la durata corrisponde (e il titolo pure)
                    if duration_match == False:
                        best_match_index = i
                        duration_match = True

            if title_match and artist_match and duration_match: # se hai trovata una traccia che corrisponde a tutte e tre le cose è inutile continuare
                break
                        
        if True: # print_info == True:
            print("------------")
            print()
            print("Best Match Found:")
            print("")
            title, artist, duration, id = self.parse_track_info(tracks[best_match_index])
            self.print_track_info(title, artist, duration)
            print("")
            print("Matching:")
            print("Title: ", title_match)
            print("Artist: ", artist_match)
            print(f"Duration within a {duration_err} ms error: ", duration_match)
            print(f"ID: ", id)
            print()
            print("_____________________________________")

        return tracks[best_match_index], (title_match, artist_match, duration_match, duration_err)

def main():
    '''esempio di utilizzo'''
    with open('params.json') as f:
        params = json.load(f)

    client_id = params["client_id"]
    client_secret = params["client_secret"]

    searcher = SpotifySearcher(client_id, client_secret)

    searcher.get_best_match(query_title="old enough", query_artist="long stay", query_duration=236000, print_info=True)


