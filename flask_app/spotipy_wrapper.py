from flask_app import spotify
from datetime import timedelta


def get_album_artist(artist):    
    artist_dict = {
        'name': artist['name'],
        'spotify_artist_uri': artist['uri'],
        'spotify_artist_id': artist['id']
    }
    
    return artist_dict


def convert_duration(duration_ms):
    delta = timedelta(seconds=duration_ms/1000)
    return delta


def get_album_tracks(album_tracks):
    album_tracks_list = []
    album_duration = timedelta(seconds=0)
    for track in album_tracks:
        track_duration = convert_duration(track['duration_ms'])
        album_duration += track_duration
        track_dict = {
            'track_number': track['track_number'],
            'name': track['name'],
            'explicit': track['explicit'],
            'track_duration': str(track_duration).split('.')[0],
            'spotify_track_id': track['id'],
            'spotify_track_uri': track['uri']
        }
        album_tracks_list.append(track_dict)
        
    return album_duration, album_tracks_list


def get_album_info(album_id):
    album = spotify.album(album_id)
    
    album_info = {
        'name': album['name'],
        'release_date': album['release_date'],
        'total_tracks': album['total_tracks'],
        'label': album['label'],
        'img_src': album['images'][1]['url'],
        'spotify_album_id': album['id'],
        'spotify_album_uri': album['uri']
    }
    
    album_artist = get_album_artist(album['artists'][0])
    album_duration, album_tracks = get_album_tracks(album['tracks']['items'])
    
    album_info['album_artist'] = album_artist
    album_info['album_duration'] = str(album_duration).split('.')[0]
    album_info['tracks'] = album_tracks
    
    return album_info