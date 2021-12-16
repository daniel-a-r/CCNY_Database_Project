from datetime import datetime, date
from flask import redirect, url_for, render_template, flash, request, session
from flask_app import app, mysql, bcrypt, spotify
from flask_app.forms import RegisterForm, LoginForm, AlbumSearchForm, UpdateNameForm, UpdateEmailForm, UpdatePasswordForm
from pprint import pprint
from flask_app.spotipy_wrapper import get_album_info
from flask_app.mysql_wrapper import get_collection, insert_into_artist, insert_into_album, insert_into_user_album, get_album_info_from_db, get_album_tracks_from_db, get_user_info


@app.route('/', methods=['GET', 'POST'])
@app.route('/home/', methods=['GET', 'POST'])
def home():
    search_results_list = []
    album_collection = []
    if 'user_id' in session:
        album_collection = get_collection()

    album_search_form = AlbumSearchForm()
    if album_search_form.validate_on_submit():
        album_name = album_search_form.album_name.data.strip().lower()
        search_results = spotify.search(q='album:' + f'{album_name}', type='album')
        
        for item in search_results['albums']['items']:
            item_dict = {
                'artist': item['artists'][0]['name'],
                'id': item['id'],
                'img_src': item['images'][1]['url'],
                'name': item['name']
            }
            search_results_list.append(item_dict)
        print(search_results_list)

    return render_template('index.html', 
                           title='Album Search', 
                           form=album_search_form, 
                           results=search_results_list,
                           collection=album_collection, 
                           session=session)


@app.route('/register/', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        flash('Already logged in', 'warning')
        return redirect(url_for('home'))
    else:
        register_form = RegisterForm()
        if register_form.validate_on_submit():
            email = register_form.email.data.lower()
            query = '''
            SELECT * FROM user
            WHERE email = %s
            '''
            cursor = mysql.connection.cursor()
            cursor.execute(query, [email])
            result = cursor.fetchall()
            if result:
                flash('Email already in use. Please use another', 'warning')
            else:
                name = register_form.name.data.strip()
                hashed_password = bcrypt.generate_password_hash(register_form.password.data).decode('utf-8')
                print('hashed password:',hashed_password)
                query = '''
                INSERT INTO user (name, email, password)
                VALUES(%s, %s, %s)
                '''
                data = [name, email, hashed_password]
                cursor.execute(query, data)
                mysql.connection.commit()
                flash('Account successfully created! You may now login.', 'success')
                return redirect(url_for('login'))
            cursor.close()
        return render_template('register.html', title='Register', form=register_form)


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        flash('Already logged in', 'warning')
        return redirect(url_for('home'))
    else:
        login_form = LoginForm()
        if login_form.validate_on_submit():
            email = login_form.email.data
            query = '''
            SELECT * FROM user
            WHERE email = %s
            '''
            cursor = mysql.connection.cursor()
            cursor.execute(query, [email])
            result = cursor.fetchall()
            cursor.close()

            if result:
                hashed_password = result[0][3]
                password_match = bcrypt.check_password_hash(hashed_password, login_form.password.data)
                if password_match:
                    session['user_id'] = result[0][0]
                    session['name'] = result[0][1]
                    print('session user_id:', session['user_id'])
                    flash('You may now start adding albums to your collection.', 'success')
                    return redirect(url_for('home'))
                else:
                    flash('Invalid password', 'danger')
            else:
                flash('That email does not exist. Please double check email or register for an account.', 'warning')
        return render_template('login.html', title='Login', form=login_form)


@app.route('/add-to-collection/<string:spotify_album_id>', methods=['GET', 'POST'])
def search(spotify_album_id):
    #checks if the user is logged in
    if 'user_id' not in session:
        flash('Must create an account to add to collection', 'warning')
        return redirect(url_for('login'))
    else:        
        album = get_album_info(spotify_album_id)
        pprint(album)
        cursor = mysql.connection.cursor()

        # checks if the artist is in the db already
        query = '''
        SELECT * FROM artist
        WHERE spotify_artist_id = %s
        '''
        cursor = mysql.connection.cursor()
        cursor.execute(query, [album['album_artist']['spotify_artist_id']])
        artist_found = cursor.fetchall()

        # if artist not in db, this means album not in db therefore user hasn't saved the album
        # if the artist is found, this indicates there is at least one album from that artist in the db already
        if not artist_found:
            # artist and album not found
            # need to insert into all tables

            # inserts into artist all tables
            insert_into_artist(album)
        else:
            artist_db_id = artist_found[0][0]
            # Checks if album is in db already 
            query = '''
            SELECT * FROM album
            WHERE spotify_album_id = %s
            '''        
            cursor.execute(query, [spotify_album_id])
            album_found = cursor.fetchall()

            # if the album is found, this indicates that a user has the album in their collection
            # if not, then no user has it in their collection
            if not album_found:
                # artist exists in db but album does not
                # need to add album, album_tracks, and album_artist to db
                insert_into_album(album, artist_db_id)
            else:
                album_id = album_found[0][0]
                # checks if the user already has album in collection
                query = '''
                SELECT * FROM user_album
                WHERE user_id = %s AND album_id = %s
                '''
                cursor.execute(query, [session['user_id'], album_id])
                user_album_found = cursor.fetchall()
                if user_album_found:
                    flash('Album already added to collection')
                else:
                    # album and artist already exist in db
                    # only need need to add to user_album

                    #insert into user_album
                    insert_into_user_album(album_id)
                

        return redirect(url_for('home'))


def get_hours_minutes_seconds(duration):
    duration_str = str(duration)
    duration_datetime = datetime.strptime(duration_str, '%H:%M:%S')
    duration_formatted = duration_datetime.strftime('%H:%M:%S')

    hours = int(duration_formatted[:2])
    minutes = int(duration_formatted[3:5])
    seconds = int(duration_formatted[6:])

    return hours, minutes, seconds


def format_album_duration(duration):
    hours, minutes, seconds = get_hours_minutes_seconds(duration)

    if hours >= 1:
        return f'{hours} hr {minutes} min'
    else:
        return f'{minutes} min {seconds} sec'


def format_track_duration(duration):
    hours, minutes, seconds = get_hours_minutes_seconds(duration)
    
    if hours >= 1:
        return f'{hours}:{minutes:02d}:{seconds:02d}'
    else:
        return f'{minutes}:{seconds:02d}'


def format_release_date(release_date):
    months = {
        1: 'January',
        2: 'February ',
        3: 'March',
        4: 'April',
        5: 'May',
        6: 'June',
        7: 'July',
        8: 'August',
        9: 'September',
        10: 'October',
        11: 'November',
        12: 'December'
    }

    year = release_date.year
    month = release_date.month
    day = release_date.day

    return f'{months[month]} {day}, {year}'


@app.route('/album_info/<int:album_id>', methods=['GET', 'POST'])
def album_info(album_id):
    album_info = get_album_info_from_db(album_id)
    album_tracks = get_album_tracks_from_db(album_id)

    album_info['album_duration'] = format_album_duration(album_info['album_duration'])
    album_info['release_date'] = format_release_date(album_info['release_date'])

    for track in album_tracks:
        track['track_duration'] = format_track_duration(track['track_duration'])

    in_collection = True

    return render_template('album_info.html', album_info=album_info, album_tracks=album_tracks, in_collection=in_collection)

'''
@app.route('/album_info/<string:spotify_album_id>', methods=['GET', 'POST'])
def album_info(spotify_album_id):
    album_info = get_album_info(spotify_album_id)
    album_tracks = None

    album_info['album_duration'] = format_album_duration(album_info['album_duration'])
    album_info['release_date'] = format_release_date(album_info['release_date'])

    for track in album_tracks:
        track['track_duration'] = format_track_duration(track['track_duration'])

    if 'user_id' in session:
        # checks if album is in collection
        pass

    return render_template('album_info.html', album_info=album_info, album_tracks=album_tracks)
'''


@app.route('/profile/', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        flash('Must login to view profile', 'warning')
        return redirect(url_for('login'))
    else:
        update_name_form = UpdateNameForm()
        update_email_form = UpdateEmailForm()
        update_password_form = UpdatePasswordForm()
        
        user_info = get_user_info()

        return render_template('profile.html', 
                               title='Profile', 
                               update_name_form=update_name_form, 
                               update_email_form=update_email_form, 
                               update_password_form=update_password_form,
                               user_info=user_info)


@app.route("/logout/")
def logout():
    session.pop('user_id', None)
    session.pop('name', None)
    flash('You have successfully logged out!', 'success')
    return redirect(url_for("home"))
