import yt_dlp
import json

with open('params.json') as f:
    playlist_url = json.load(f)["yt_playlist_url"]


def clean_title(title):

    known_bad_words = ["cover", "original version", "official version", "music video", "official music video", "remastered", "bonus track"]
    caratteri_da_rimuovere_sempre = ["|"]

    for word in known_bad_words: 
        word_tra_parentesi_tonde = "(" + word + ")"
        word_tra_parentesi_quadre = "[" + word + "]"
        word_tra_parentesi_graffe = "{" + word + "}"

        for substring in ["(" + word + ")", "[" + word + "]", "{" + word + "}", word]:
            title = title.replace(substring, '')
        
    return title.strip()


def get_playlist_info(playlist_url, clean_titles=True):
    ''
    ''

    params = {
        'extract_flat': True, # Ottiene solo le informazioni di base della playlist e degli entry senza processare ogni video completamente
        'force_generic_extractor': True, # Aiuta in alcuni casi con URL complessi
        'dump_single_json': True, # Per ottenere l'output JSON completo
        'simulate': True, # Non scaricare nulla, solo estrarre metadati
        'quiet': True, # Sopprime l'output della console di yt-dlp
        'ignoreerrors': True, # Continua anche se alcuni video non possono essere processati
    }

    try:
        with yt_dlp.YoutubeDL(params) as ydl:
            info_dict = ydl.extract_info(playlist_url, download="False")
            if info_dict is None:
                print(f"Errore: Impossibile estrarre informazioni dall'URL: {playlist_url}")
                return None
        
        playlist_info = {}
        playlist_info["title"] = info_dict.get("title", "N/A")
        playlist_info["author"]  = info_dict.get("channel", "N/A")
        num_videos = len(info_dict["entries"]) 
        if num_videos is None:
            num_videos = 0 # empty playlist
        else:
            playlist_info["num_videos"] = num_videos

        print("Informazioni playlist")
        print("........................")
        print()
        print(f"title: ", playlist_info["title"])
        print()
        print(f"author: ", playlist_info["author"])
        print()
        print(f"number of videos: ", playlist_info["num_videos"])
        print()
        print("........................")
        print("........................................")

        print("--------- VIDEOS ----------")
        videos_info = []
        for (i, video_info) in enumerate(info_dict["entries"]):
            video_dict = {}
            title = clean_title(video_info["title"].lower())
            video_dict["title"] = title
            video_dict["duration"] = video_info.get("duration", 0)
            uploader = video_info["uploader"].lower()
            video_dict["uploader"] = uploader 
            if " - topic" in uploader:
                video_dict["artist"] = uploader.replace(" - topic", "")
            elif uploader in video_dict["title"]:
                video_dict["artist"] = uploader
            else:
                video_dict["artist"] = "N/A"
            videos_info.append(video_dict)

            print()
            print("title: ", video_dict["title"])
            print("uploaded by: ", video_dict["uploader"])
            print("artist: ", video_dict["artist"])
            print("duration: ", video_dict["duration"])

        
    except yt_dlp.utils.DownloadError as e:
        print(f"Errore durante l'estrazione delle informazioni: {e}")
        return None
    except Exception as e:
        print(f"Si è verificato un errore inatteso: {e}")
        return None

    return playlist_info, videos_info

playlist_info, videos_infos = get_playlist_info(playlist_url)

