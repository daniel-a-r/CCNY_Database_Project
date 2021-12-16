from flask_app import mysql
from flask import session
from pprint import pprint


def last_insert_id():
    cursor = mysql.connection.cursor()
    query = '''
    SELECT LAST_INSERT_ID()
    '''
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    return result[0][0]


def insert_into_user_album(album_id):
    cursor = mysql.connection.cursor()
    query = '''
    INSERT INTO user_album (user_id, album_id)
    VALUES (%s, %s);
    '''
    data = [session['user_id'], album_id]
    cursor.execute(query, data)
    mysql.connection.commit()
    cursor.close()
    print('inserted into user_album')


def insert_into_album_artist(artist_id, album_id):
    cursor = mysql.connection.cursor()
    query = '''
    INSERT INTO album_artist (artist_id, album_id)
    VALUES (%s, %s);
    '''
    data = [artist_id, album_id]
    cursor.execute(query, data)
    mysql.connection.commit()
    cursor.close()
    print('inserted int0 album_artist')

def insert_into_album_tracks(album_id, tracks):
    pprint(tracks)
    cursor = mysql.connection.cursor()
    for track in tracks:
        pprint(track)
        query = '''
        INSERT INTO album_tracks (track_number, name, explicit, duration, spotify_track_id, spotify_track_uri, album_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s);
        '''
        data = [track['track_number'],
                track['name'],
                track['explicit'],
                track['track_duration'],
                track['spotify_track_id'],
                track['spotify_track_uri'],
                album_id]
        cursor.execute(query, data)
    
    mysql.connection.commit()
    cursor.close()
    print('inserted into album_tracks table')


def insert_into_album(album, artist_id):
    cursor = mysql.connection.cursor()
    query = '''
    INSERT INTO album (name, total_tracks, duration, release_date, label, img_src, spotify_album_id, spotify_album_uri)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
    '''
    data = [album['name'],
            album['total_tracks'],
            album['album_duration'],
            album['release_date'],
            album['label'],
            album['img_src'],
            album['spotify_album_id'],
            album['spotify_album_uri']]

    cursor.execute(query, data)
    mysql.connection.commit()
    album_id = last_insert_id()
    cursor.close()
    print('inserted into album table')
    insert_into_album_tracks(album_id, album['tracks'])
    insert_into_album_artist(artist_id, album_id)
    insert_into_user_album(album_id)


def insert_into_artist(album):
    cursor = mysql.connection.cursor()
    query = '''
    INSERT INTO artist (name, spotify_artist_id, spotify_artist_uri)
    VALUES (%s, %s, %s);
    '''
    data = [album['album_artist']['name'], 
            album['album_artist']['spotify_artist_id'], 
            album['album_artist']['spotify_artist_uri']]
            
    cursor.execute(query, data)
    mysql.connection.commit()
    artist_id = last_insert_id()
    cursor.close()
    print('inserted into artist table')
    insert_into_album(album, artist_id)
