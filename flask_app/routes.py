from re import search
from flask import redirect, url_for, render_template, flash, request, session
from flask_app import app, mysql, bcrypt, spotify
from flask_app.forms import RegisterForm, LoginForm, AlbumSearchForm, UpdateNameForm, UpdateEmailForm, UpdatePasswordForm
from flask_app.format_datetime import format_album_duration, format_track_duration, format_release_date
from flask_app.spotipy_wrapper import get_album_info
from flask_app.mysql_wrapper import *
from pprint import pprint


def create_matrix(albums):
    matrix = []
    row = []
    for i in range(len(albums)):
        row.append(albums[i])
        if i % 3 == 2:
            matrix.append(row)
            row = []
    if row:
        matrix.append(row)
    return matrix


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
        spotify_results = spotify.search(q='album:' + f'{album_name}', limit=12, type='album')
        print(type(spotify_results))
        pprint(spotify_results)
        print('Result total:', spotify_results['albums']['total'])

        if spotify_results['albums']['total'] == 0:
            flash('No results. Try entering something different', 'warning')
        
        for item in spotify_results['albums']['items']:
            item_dict = {
                'artist': item['artists'][0]['name'],
                'id': item['id'],
                'img_src': item['images'][1]['url'],
                'name': item['name']
            }
            search_results_list.append(item_dict)

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
    
    register_form = RegisterForm()
    if register_form.validate_on_submit():
        email = register_form.email.data.lower()
        result = check_email_exists(email)
        if result:
            flash('Email already in use. Please use another', 'warning')
        else:
            name = register_form.name.data.strip()
            hashed_password = bcrypt.generate_password_hash(register_form.password.data).decode('utf-8')
            insert_new_user(name, email, hashed_password)
            flash('Account successfully created! You may now login.', 'success')
            return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=register_form)


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        flash('Already logged in', 'warning')
        return redirect(url_for('home'))
    
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
                flash('You may now start adding albums to your collection.', 'success')
                return redirect(url_for('home'))
            else:
                flash('Invalid password', 'danger')
        else:
            flash('That email does not exist. Please double check email or register for an account.', 'warning')
    return render_template('login.html', title='Login', form=login_form)


@app.route('/add-to-collection/<string:spotify_album_id>', methods=['GET', 'POST'])
def add_to_collection(spotify_album_id):
    #checks if the user is logged in
    if 'user_id' not in session:
        flash('Must create an account to add to collection', 'warning')
        return redirect(url_for('login'))
          
    album = get_album_info(spotify_album_id)

    # checks if the artist is in the db already
    spotify_artist_id = album['album_artist']['spotify_artist_id']
    artist_found = get_artist_by_spotify_id(spotify_artist_id)

    # if artist not in db, this means album not in db therefore user hasn't saved the album
    # if the artist is found, this indicates there is at least one album from that artist in the db already
    if not artist_found:
        # artist and album not found
        # need to insert into all tables

        # inserts into artist all tables
        insert_into_artist(album)
    else:
        artist_db_id = artist_found[0][0]
        # Checks if album is already in db 
        album_found = get_album_by_spotify_id(spotify_album_id)

        # if the album is found, this indicates that a user has the album in their collection
        # if not, then no user has it in their collection
        if not album_found:
            # artist exists in db but album does not
            # need to add album, album_tracks, and album_artist to db
            insert_into_album(album, artist_db_id)
        else:
            album_id = album_found[0][0]
            # checks if the user already has album in collection
            user_album_found = get_user_album(album_id)
            if user_album_found:
                flash('Album already added to collection')
            else:
                # album and artist already exist in db
                # only need need to add to user_album

                #insert into user_album
                insert_into_user_album(album_id)
            
    return redirect(url_for('home'))


@app.route('/album_info/<int:album_id>', methods=['GET', 'POST'])
def album_info_from_collection(album_id):
    album_info = get_album_info_from_db(album_id)
    album_tracks = get_album_tracks_from_db(album_id)

    album_info['album_duration'] = format_album_duration(album_info['album_duration'])
    album_info['release_date'] = format_release_date(album_info['release_date'])

    for track in album_tracks:
        track['track_duration'] = format_track_duration(track['track_duration'])

    in_collection = True

    return render_template('album_info.html', album_info=album_info, album_tracks=album_tracks, in_collection=in_collection)


@app.route('/album_info/<string:spotify_album_id>', methods=['GET', 'POST'])
def album_info_from_search(spotify_album_id):
    album_info = get_album_info(spotify_album_id)
    
    album_info['artist_name'] = album_info['album_artist']['name']
    album_info['spotify_artist_id'] = album_info['album_artist']['spotify_artist_id']
    album_info['album_name'] = album_info.pop('name', None)
    album_info['album_duration'] = format_album_duration(album_info['album_duration'])
    album_info['release_date'] = format_release_date(album_info['release_date'])
    album_info.pop('spotify_album_uri', None)
    album_info.pop('album_artist', None)

    if 'user_id' not in session:
        in_collection = False
    else:
        album_found = get_album_by_spotify_id(spotify_album_id)
        if album_found:
            album_info['db_album_id'] = album_found[0][0]

            user_album_found = get_user_album(album_info['db_album_id'])
            if user_album_found:
                in_collection = True
        else:
            in_collection = False

    album_tracks = album_info['tracks']
    for track in album_tracks:
        track['track_duration'] = format_track_duration(track['track_duration'])
        track['track_name'] = track.pop('name', None)
        track.pop('spotify_track_id', None)
        track.pop('spotify_track_uri', None)

    album_info.pop('tracks', None)

    return render_template('album_info.html', 
                           album_info=album_info, 
                           album_tracks=album_tracks, 
                           in_collection=in_collection)


@app.route('/remove-from-collection/<int:album_id>', methods=['GET', 'POST'])
def remove_from_collection(album_id):
    if 'user_id' not in session:
        flash('Please login to perform that action', 'warning')
        return redirect(url_for('login'))
    
    delete_from_collection(album_id)
    return redirect(url_for('home'))


@app.route('/profile/', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        flash('Must login to view profile', 'warning')
        return redirect(url_for('login'))

    update_name_form = UpdateNameForm()
    update_email_form = UpdateEmailForm()
    update_password_form = UpdatePasswordForm()

    if update_name_form.validate_on_submit():
        new_name = update_name_form.new_name.data
        update_name(new_name)
        flash('Name updated!', 'success')
        return redirect(url_for('profile'))

    if update_email_form.validate_on_submit():
        new_email = update_email_form.new_email.data
        result = check_email_exists_update_email(new_email)

        if result:
            flash('That email is already taken by another user. Please enter a different email.', 'warning')
        else:
            update_email(new_email)
            flash('Email updated!', 'success')

        return redirect(url_for('profile'))

    if update_password_form.validate_on_submit():
        hashed_password = get_hashed_password()
        password_match = bcrypt.check_password_hash(hashed_password, update_password_form.old_password.data)

        if password_match:
            new_hashed_password = bcrypt.generate_password_hash(update_password_form.new_password.data).decode('utf-8')
            update_password(new_hashed_password)
            flash('Password updated!', 'success')
        else:
            flash('Password entered for "Old Password" does not match password in our records', 'warning')

        return redirect(url_for('profile'))
    
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
