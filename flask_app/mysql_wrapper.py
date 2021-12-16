from flask_app import mysql
from flask import session
from pprint import pprint


def last_insert_id():
    query = '''
    SELECT LAST_INSERT_ID()
    '''
    cursor = mysql.connection.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    return result[0][0]


def insert_into_user_album(album_id):
    query = '''
    INSERT INTO user_album (user_id, album_id)
    VALUES (%s, %s);
    '''
    data = [session['user_id'], album_id]
    cursor = mysql.connection.cursor()
    cursor.execute(query, data)
    mysql.connection.commit()
    cursor.close()


def insert_into_album_artist(artist_id, album_id):
    query = '''
    INSERT INTO album_artist (artist_id, album_id)
    VALUES (%s, %s);
    '''
    data = [artist_id, album_id]
    cursor = mysql.connection.cursor()
    cursor.execute(query, data)
    mysql.connection.commit()
    cursor.close()


def insert_into_album_tracks(album_id, tracks):
    cursor = mysql.connection.cursor()
    for track in tracks:
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


def insert_into_album(album, artist_id):
    
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
    cursor = mysql.connection.cursor()
    cursor.execute(query, data)
    mysql.connection.commit()
    album_id = last_insert_id()
    cursor.close()

    insert_into_album_tracks(album_id, album['tracks'])
    insert_into_album_artist(artist_id, album_id)
    insert_into_user_album(album_id)


def insert_into_artist(album):
    
    query = '''
    INSERT INTO artist (name, spotify_artist_id, spotify_artist_uri)
    VALUES (%s, %s, %s);
    '''
    data = [album['album_artist']['name'], 
            album['album_artist']['spotify_artist_id'], 
            album['album_artist']['spotify_artist_uri']]

    cursor = mysql.connection.cursor()
    cursor.execute(query, data)
    mysql.connection.commit()
    artist_id = last_insert_id()
    cursor.close()

    insert_into_album(album, artist_id)


def create_dict_list(result, keys):
    dict_list = []
    for values in result:
        album_dict = dict(zip(keys, values))
        dict_list.append(album_dict)

    return dict_list


def get_collection():
    user_id = session['user_id']
    query = '''
    SELECT AR.name, AL.name, AA.album_id, AL.img_src
    FROM album_artist AA
    INNER JOIN album AL ON AL.id = AA.album_id
    INNER JOIN artist AR ON AR.id = AA.artist_id
    INNER JOIN user_album UA ON UA.album_id = AA.album_id
    WHERE UA.user_id = %s
    ORDER BY AR.name, AL.release_date;
    '''
    cursor = mysql.connection.cursor()
    cursor.execute(query, [user_id])
    result = cursor.fetchall()
    cursor.close()

    keys = ['artist_name', 'album_name', 'album_id', 'album_img_src']

    return create_dict_list(result, keys)


def get_album_info_from_db(album_id):
    query= '''
    SELECT AR.name, AL.name, AL.total_tracks, AL.duration, AL.release_date, AL.label, AL.img_src, AL.spotify_album_id, AR.spotify_artist_id
    FROM album_artist AA
    INNER JOIN album AL ON AL.id = AA.album_id
    INNER JOIN artist AR ON AR.id = AA.artist_id
    WHERE AL.id = %s;
    '''
    cursor = mysql.connection.cursor()
    cursor.execute(query, [album_id])
    result = cursor.fetchall()
    cursor.close()


    keys = ['artist_name', 'album_name', 'total_tracks', 'album_duration', 'release_date', 'label', 'img_src', 'spotify_album_id', 'spotify_artist_id']
    album_dict = dict(zip(keys, result[0]))

    return album_dict


def get_album_tracks_from_db(album_id):
    query = '''
    SELECT track_number, name, explicit, duration
    FROM album_tracks
    WHERE album_id = %s;
    '''
    cursor = mysql.connection.cursor()
    cursor.execute(query, [album_id])
    result = cursor.fetchall()
    cursor.close()

    keys = ['track_number', 'track_name', 'explicit', 'track_duration']

    return create_dict_list(result, keys)


def get_user_info():
    query = '''
    SELECT name, email
    FROM user
    WHERE id = %s;
    '''
    cursor = mysql.connection.cursor()
    cursor.execute(query, [session['user_id']])
    result = cursor.fetchall()
    cursor.close()

    user_info_dict = {'name': result[0][0], 'email': result[0][1]}

    pprint(user_info_dict)

    return user_info_dict