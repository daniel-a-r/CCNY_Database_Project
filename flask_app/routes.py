from flask import redirect, url_for, render_template, flash, request, session
from flask_app import app, mysql, bcrypt, spotify
from flask_app.forms import RegisterForm, LoginForm, AlbumSearchForm
from pprint import pprint
from flask_app.spotipy_wrapper import get_album_info
from flask_app.mysql_wrapper import insert_into_artist, insert_into_album, insert_into_user_album


@app.route('/', methods=['GET', 'POST'])
@app.route('/home/', methods=['GET', 'POST'])
def home():
    album_search_form = AlbumSearchForm()
    search_results_list = []
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

    return render_template('index.html', title='Album Search', form=album_search_form, results=search_results_list, session=session)


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


@app.route("/logout/")
def logout():
    session.pop('user_id', None)
    flash('You have successfully logged out!', 'success')
    return redirect(url_for("home"))
