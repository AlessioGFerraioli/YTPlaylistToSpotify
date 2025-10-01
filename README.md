# YTPlaylistToSpotify
A script to convert a youtube playlist of songs into a spotify playlist

The script fetches data from a yt playlist and creates a new spotify playlist 

Requires a params.json file with the private client_id and client_secret for accessing a spotify account.

Since titles of youtube videos have a lot variability it is difficult to be sure of finding the exact match.
I'm trying to solve the problem by implementing a way to clean the title from common filler words (like "official video"), to extrapolate the name of the artist when there are sufficient clues (for example "artist - topic"), and comparing the durations. 
This is a work in progress and for now these implementations are sketchy at best, but it already works at a sufficient level for my needs, even if sometimes a song is not found or an incorrect song is added to playlist instead.  
