from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from flask_mysqldb import MySQL
from MySQLdb import OperationalError, ProgrammingError

from wtforms import Form, StringField, PasswordField, validators
# from passlib.hash import sha256_crypt
from functools import wraps
# import webbrowser
from errorList import errorlist

import os
import requests
# from requests.exceptions import ConnectionError
import spotipy
from flask import jsonify
import imdb
import pickle
import ast
import webview

# import logging

ia = imdb.IMDb()

# logging.basicConfig(filename='app.log', level=logging.ERROR)

app = Flask(__name__)

#mysqldump -u root -p --databases annas_db > annas_db.sql  -> change db name in file/filename - mysql -u root -p < annas_db2.sql
app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD', 'password')
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB', 'mydatabase')
app.config['MYSQL_DB'] = 'fan_tracks'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)  # is not actually connecting to database - waits for first connection

clientID = '6c68091ecfa44fe9b55ff6bcc5d81c97'
clientSecret = '36582bf60f224dc3a1035a0335700bef'
redirectURI = 'https://google.com/'
scope = 'playlist-read-private playlist-modify-private playlist-modify-public ugc-image-upload'

app.secret_key = 'mysecret12345'


def spotipyConnection():
    try:
        if 'spotifyId' in session:  # already connected may have to re-connect here
            # spotipyId seems to be in session when I restart the server ?? Maybe another sesion
            # this will stay in memory for 31 days !!!
            print('spotipyConnection: In spotifyid in session')

            serialized_oath_object = session['spotifyOathObject']
            oauth_object = pickle.loads(serialized_oath_object)

            # Check if the access token has expired
            try:
                if oauth_object.is_token_expired(oauth_object.get_cached_token()):
                    print('spotipyConnection: Access token has expired')

                    new_token = oauth_object.refresh_access_token(oauth_object.get_refresh_token())
                    oauth_object.access_token = new_token['access_token']
                    session['spotifyOathObject'] = pickle.dumps(oauth_object)
                else:
                    # aoth not expired
                    oauth_object = pickle.loads(session['spotifyOathObject'])

                spotifyObject = spotipy.Spotify(auth_manager=oauth_object)
                spotifyId = spotifyObject.me()['id']
            except Exception as e:
                # Error cache file got deleted - user needs to re-authorise
                print('Error spotipyConnection: ', e)
                return connectToSpotify(session['username'])

            return spotifyObject, spotifyId

        else:
            return connectToSpotify(session['username'])  # connect to spotify for the first time

    except spotipy.SpotifyException as e:
        print('SpotifpyConnection:', e)


def connectToSpotify(username):
    try:
        # TODO: test delete cache and create new user
        # TODO don't ask this every time ?? Which time?? - also called when internet goes down - check first
        # first log in for this server session
        print('spotipyConnection: login to Spotipy and approve - then copy the URL below')

        oauth_object = spotipy.SpotifyOAuth(clientID, clientSecret, redirectURI, scope=scope, username=username, requests_timeout=30)
        spotifyObject = spotipy.Spotify(auth_manager=oauth_object)
        spotifyId = spotifyObject.me()['id']
        session['spotifyOathObject'] = pickle.dumps(oauth_object)
        session['spotifyId'] = spotifyId
        return spotifyObject, spotifyId

    except spotipy.SpotifyException as e:
        print("connectToSpotify: SpotifyException", e)

        flash("connectToSpotify: Failed to log into spotify", 'danger')
    except spotipy.SpotifyOauthError as e:
        print("connectToSpotify: SpotifyOauthError", e)
    except requests.ConnectionError:
        print("connectToSpotify: Internet down - try again later")
        flash('Internet is down - try again later', 'danger')
    except requests.RequestException:
        print("connectToSpotify: ERROR requests")
    except Exception as e:  # check for NewConnectionError - no internet
        print("connectToSpotify: ERROR internat?? ", e)
    print("EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE")
    return 0,0 # TODO - is this correct ??


def getSpotifyObject():
    sp, spId = spotipyConnection()
    return sp


# Only handle errors in function if nor returning to dashboard
@app.errorhandler(Exception)
def basic_error(e):
    print("An error occured:" + str(e))
    # render an error page

    # render an error page
    # handle all exceptions
    if isinstance(e, requests.exceptions.ConnectionError):
        # handle connection errors
        msg = "Internet is down: "
    # elif isinstance(e, MySQLdb._mysql_exceptions.Error):
    # handle database errors
    # msg="Database error: "
    elif isinstance(e, ProgrammingError):
        print('Error: Please fix and restart the server', e)
        return render_template('error.html', error_message=e), 500

    elif isinstance(e, OperationalError):  #
        print('Error: Please fix and restart the server', e)
        return render_template('error.html', error_message=e), 500

        # handle OperationalError (e.g. connection error)
    else:
        # handle all other exceptions
        msg = "Error: In basic_error "

    print("Error Basic_Error: ",e)
    flash(msg + str(e), 'danger')  # TODO take str(e) out when finished testing
    return redirect(url_for('dashboard'))  # TODO change to welcome


# @app.route('/favicon.ico')
# def favicon():
#   return url_for('static', filename='static/image/favicon.ico')


class RegisterForm(Form):
    # name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [validators.DataRequired(),
                                          validators.EqualTo('confirm', message='Password do not match')])
    confirm = PasswordField('confirm Password')


def dbGetUserData(username):
    try:
        with mysql.connection.cursor() as cursor:
            if cursor.execute("SELECT * FROM friends WHERE username= %s", [username]):  # find that username in the db
                data = cursor.fetchone()  # fetch only the first row (the first user that comes up)
                return data
    except Exception as e:
        print("dbGetUserData Error: ", e)
    flash("Database Errror getting user data: ", 'danger')
    return False


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')  # open on login page after login click
    else:  # POST
        clearUser()  # in case session data is cashed
        username = request.form['username']  # the username is gotten from the data givin to the form
        password_candidate = request.form[
            'password']  # TODO: needed ?? password candidate is the password from rhe form
        data = dbGetUserData(username)
        password = data['password']
        userId = data['id']
        if password and userId:  # if a user is found - check password - TODO do both checks in if
            # TODO passwords are not being compared and letting any password to log in
            if password_candidate == password:  # todo taking out encryption - but good for security	#sha256_crypt.verify(password_candidate,password):
                if connectToSpotify(username):  # if there is a spotify id to be found
                    session['logged_in'] = True  # session is now logged in
                    session['username'] = username  # session username is username inputted
                    session['id'] = userId  # session id is the id from the db
                    return redirect(url_for('welcome'))  # send user to welcome
                else:
                    flash('login failed - spoify is down - try again later', 'danger')  # success message
            else:
                flash("The username or password does not match any registered please try again", 'danger')
    return render_template('login.html')  # if its GET not POST return an error TODO: not true


# to prevent using of app without login
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):  # !!WHAT!!
        if 'logged_in' in session:
            return f(*args, **kwargs)  # !!WHAT!!
        else:
            flash('Please login ', 'danger')
            return redirect(url_for('login'))
    return wrap


def clearUser():
    session.clear()


# Delete user and their playlists from DB
def dbDeleteUser(userId):
    try:
        with mysql.connection.cursor() as cursor:
            cursor.execute("DELETE FROM playlist WHERE userid = %s", (userId,))
            cursor.execute("DELETE FROM friends WHERE id = %s", (userId,))
            mysql.connection.commit()
            return True

    except Exception as e:
        print("dbDeleteUser Error: ", e)
        flash("Database error deleting user:" + str(e), 'danger')
        return False


@app.route('/delete_user')
@is_logged_in
def delete_user():
    if dbDeleteUser(session['id']):
        clearUser()
        # Don't delete their playlists on spotify - i am soo nice
        flash("Your account has been deleted, until next time friend <3", 'danger')
        return redirect(url_for('login'))
    else:
        flash("Sorry Having trouble deleting your account right now :( we dont want you to leave ", 'danger')
        return redirect(url_for('welcome'))


@app.route('/logout')
@is_logged_in
def logout():
    clearUser()
    return redirect(url_for('login'))


def dbGetUserPlaylists(userId):
    try:
        with mysql.connection.cursor() as cursor:
            # TODO: change playlist to use spotifylink as key
            result = cursor.execute("SELECT playlisttitle,imgLink,spotifylink from playlist WHERE userid = %s",
                                    (userId,))
            if result:
                return cursor.fetchall()
            else:
                flash('No playlists found', 'info')
                return []

    except Exception as e:
        print("dbGetUserPlaylists Error: ", e)
        flash("Database error getting playlists:" + str(e), 'danger')
        return []


@app.route('/dashboard')
@is_logged_in
def dashboard():
    playLists = dbGetUserPlaylists(session['id'])
    # or can just access from session in dashboard
    return render_template('userDashboard.html', playlists=playLists)  # sends in the playlist we just got from database


def storeMovieInDB():  # TODO:ANNA
    msg = ""
    return msg


# =====================================================================================

class make_playlist(Form):
    title = StringField('Name', [validators.Length(min=1, max=25)])


@app.route('/create_playlist', methods=['GET', 'POST'])
@is_logged_in
def create_playlist():
    form = make_playlist(request.form)  # make the playlist using the form element
    if request.method == 'POST' and form.validate():  # if the request is POST
        playlist = form.title.data  # get the data entered in the form and use that as the name for the playlist
        try:
            # if WIFI down imdb causes a dump even though error is caught - checking internet first via spotify - doesnt dump!
            if not getSpotifyObject():
                return redirect(url_for('welcome'))
            movieList = ia.search_movie(playlist)  # TODO - if wifo down - crashes - error not caught
            print('movie match list', movieList)
            if not movieList:
                flash("No movie match found", 'info')
                return render_template('add_playlist.html',
                                       form=form)  # TODO: form=form?? does this work pen function in add_playlist.html

            myMovieList = []
            for movie in movieList:
                if not movie.data.get('full-size cover url'):
                    movie['full-size cover url'] = '.\\static\\images\\banner.jpg'  # todo:anna: new image for no omg
                myMovieList.append([movie.movieID, movie.data['title'], movie.get('full-size cover url')])
            return render_template('pickMovie.html', movieList=myMovieList)

        except imdb.IMDbDataAccessError as e:
            print("Create_playlist: imdb error ", e)
            return redirect(url_for('welcome'))

        except Exception as e:  # if it doesnt connect to imdb
            print("Create_playlist: imdb error ", e)
            flash("Error contacting imdb, check internet", 'danger')
            return redirect(url_for('welcome'))
    return render_template('add_playlist.html', form=form)  # open function in add_playlist.html


def dbCreatePlaylist(userId, theMovieName, playListId, poster):  # todo
    try:
        with mysql.connection.cursor() as cursor:
            # Check if playlist already exists
            if cursor.execute("SELECT * FROM playlist WHERE userid= %s AND playlisttitle = %s",
                              (userId, theMovieName)):
                flash("Playlist already exists", 'info')
                return False
            else:
                cursor.execute("INSERT INTO playlist(userid,playlisttitle,spotifylink,imgLink) VALUES (%s,%s,%s,%s)",
                               (userId, theMovieName, playListId, poster))  # getting the id from the link
                mysql.connection.commit()  # comming connection to sql
                return True

    except Exception as e:
        print("dbGetUserPlaylists Error: ", e)
        flash("Database error getting playlists:" + str(e), 'danger')
        return False


@app.route('/pickMovie', methods=['GET', 'POST'])
@is_logged_in
def pickMovie():
    movie_json = request.form['movie']
    movie = ast.literal_eval(movie_json)
    if movie: #!= None:
        print("MOVIE =", movie)
        theMovieName = movie[1]
        poster = movie[2]
        try:
            sp = getSpotifyObject()
            if not sp:
                flash("Error Creating a Playlist in Spotify", 'danger')
                return redirect(url_for('welcome'))
            else:
                spotifyPlaylist = sp.user_playlist_create(session['spotifyId'],
                                                          theMovieName)
                if dbCreatePlaylist(session['id'], theMovieName, spotifyPlaylist['id'], poster):
                    flash(f"Added playlist for Movie {theMovieName}", 'success')
        except Exception as e:  # if it doesnt connect
            flash("Error Creating a Playlist in Spotify", 'danger')
            print('pickMovie: ', e)
            return redirect(url_for('welcome'))
        # TOdo flash or mrssage ??
    else:
        flash("No movie picked", 'danger')
    return redirect(url_for('dashboard'))


def get_playlistId(playListName):
    pass


def dbDeletePlayList(userId, playlistName):
    try:
        with mysql.connection.cursor() as cursor:
            if cursor.execute("SELECT spotifyLink FROM playlist WHERE userid= %s AND playlisttitle = %s",
                              (userId, playlistName)):
                playlistLinks = cursor.fetchone()
                spotifyLink = playlistLinks['spotifyLink']
                cursor.execute("DELETE  FROM playlist WHERE spotifylink =%s", (spotifyLink,))
                mysql.connection.commit()
                return spotifyLink
            else:
                flash("Database error deleting playlist does not exist:", 'danger')
    except Exception as e:
        print("dbDeletePlayList Error: ", e)
        flash("Database error deleting playlist:" + str(e), 'danger')

    return False


@app.route('/delete_playlist/<string:playlist>')
@is_logged_in
def delete_playlist(playlist):
    playlistName = playlist
    # using the Name get the print link - if it suceeds - delete from database
    try:
        sp = getSpotifyObject()
        if not sp:
            flash("Error deleting from Spotify", 'danger')
        else:
            spotifyLink = dbDeletePlayList(session['id'], playlistName)
            if spotifyLink:
                sp.user_playlist_unfollow(session['spotifyId'], spotifyLink)
                flash("Playlist successfully deleted", 'success')
    except spotipy.SpotifyException as e:
        if e.http_status == 403 and "Insufficient scope" in e.msg:
            flash("Playlist didnt exist on Spotipy" + str(e), 'danger')
        else:
            flash("Spotipy error:" + str(e), 'danger')
    return redirect(url_for('dashboard'))


def dbCheckNameOrEmailExists(username, email):
    #
    try:
        with mysql.connection.cursor() as cursor:
            # if found - flash return false

            if cursor.execute("SELECT * FROM friends WHERE username= %s", [username]):
                flash("User name already exists, please try another user name:", 'danger')
                return True

            if cursor.execute("SELECT * FROM friends WHERE email=%s", [email]):
                flash("Email already exists, please try another Email", 'danger')
                return True

    except Exception as e:
        print("dbDeletePlayList Error: ", e)
        flash("Database error checking user exists :" + str(e), 'danger')

    return False

def dbCreateAccount(username, email, password):
    #

    try:
        with mysql.connection.cursor() as cursor:
            cursor.execute("INSERT INTO friends(email,username,password,spotifyId) VALUES(%s,%s,%s,%s)",
                        (email, username, password,session['spotifyId']))
            mysql.connection.commit()

    except Exception as e:
        print("dbDeletePlayList Error: ", e)
        flash("Database error checking user exists :" + str(e), 'danger')

    return True


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    print('in register')
    try:
        if request.method == 'POST' and form.validate():
            print('in register post')

            email = form.email.data
            username = form.username.data
            password = form.password.data  # sha256_crypt.encrypt(str(form.password.data))   #todo encrypt password
            if dbCheckNameOrEmailExists(username,email):    #if it does exist
                print('register Error: ')

                return render_template('registrationPage.html', form=form)  # open this function in the rgisterpage
            else:

                if connectToSpotify(username):  # if there is a spotify id to be found TODO: corrct way ?? if WIFI down??
                    dbCreateAccount(username,email,password)

                    return redirect(url_for('login'))  # redirect to login for new user
                else:
                    flash('No Spoitfy account', 'danger')  # else they do not have  a spotify account

        # TODO: should go to login page if successfull - tried but it didnt work ?? is it render or redirect ?? tried both

        return render_template('registrationPage.html', form=form)  # open this function in the rgisterpage
    except Exception as e:
        clearUser()
        print('Register Error: ', e)
        flash('Error registering - try again ', 'danger')

    return render_template('registrationPage.html', form=form)  # open this function in the rgisterpage


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/movie')
def movie():
    return render_template('movie.html')


def getOfficialPlaylist(playlistName):
    lst = []
    spotifyObject, spotifyId = spotipyConnection()  # spotify object assignment

    return lst


@app.route('/update_table', methods=['POST'])
def update_table():
    try:
        data = request.get_json()
        table_data = data['table_data']
        print('Table data received and processed successfully')
        print(session['playListName'], table_data)

        myCursor = mysql.connection.cursor()
        if myCursor.execute("SELECT spotifyLink FROM playlist WHERE userid= %s AND playlisttitle = %s",
                            (session['id'], session['playListName'])):  # check
            playlistLinks = myCursor.fetchall()  # TODO: in debug access spotipy link - need it to unfollow
            spotifyPlayListId = playlistLinks[0]['spotifyLink']
            getSpotifyObject().playlist_replace_items(spotifyPlayListId, table_data)  # it wants id as list
        return 'Table data received and processed successfully'

    except Exception as e:
        print('updateTable:', e)
        # dealt with in apotifyconnection
        response = jsonify({'error': 'An error occurred: {}'.format(e)})
        response.status_code = 500
        return response


# Get songs from spoitify that match the search enry
@app.route('/searchForMatchingTracks', methods=['POST'])
def searchForMatchingTracks():
    try:
        searchName = request.json.get('song_name')
        table_data = request.json.get('table_data')

        # spotifyObject, spotifyId = spotipyConnection()  # spotify object assignment
        results = getSpotifyObject().search(searchName, 10, 0, "track")
        songs_dict = results['tracks']
        song_items = songs_dict['items']
        song = song_items[0]['external_urls']['spotify']

        lst = results['tracks']
        trackList = []

        for j in lst['items']:
            # only add to list if not already in not in playlist
            if j['id'] not in table_data:
                print(j['name'])
                trackList.append([j['name'], j['id']])  # list of lists
        return jsonify(trackList)
    except Exception as e:
        print('searchForMatchingTracks: ', e)
        # dealt with in apotifyconnection
        response = jsonify({'error': 'An error occurred: {}'.format(e)})
        response.status_code = 500
        return response


# Get offical movie tracks
@app.route('/getSongData', methods=['GET', 'POST'])
def getSongData():
    try:
        data = request.get_json()
        table_data = data['table_data']
        trackList = []
        # todo
        sp = getSpotifyObject()
        if sp:
            results = sp.search(session['playListName'] + ' soundtrack', 1, 0, type="album")
            if results:
                album_id = results['albums']['items'][0]['id']
                lst = getSpotifyObject().album_tracks(album_id)
                for j in lst['items']:
                    if j['id'] not in table_data:
                        trackList.append([j['name'], j['id']])  # list of lists
            return jsonify(trackList)
    except Exception as e:
        pass #print('getSongData: ', e)

    # dealt with in apotifyconnection
    response = jsonify({'error': 'An error occurred in getSOngData: '})
    response.status_code = 500
    return response


# Add tracks to playlist
@app.route('/recomended', methods=['GET', 'POST'])
@is_logged_in
def recomended():
    try:
        if request.method == 'GET':  # if the request is POST
            pass
        playListName = request.form.get("playlistTitle")
        spotifyLink = request.form.get("spotifylink ")
        tracks = []
        if playListName and spotifyLink:
            print('rec ', playListName, spotifyLink)
            session['playListName'] = playListName
            spotifyObject = getSpotifyObject()  # spotify object assignment
            # get songs in your playlist and send them to screen
            lst = spotifyObject.playlist_items(spotifyLink)
            for j in lst['items']:
                tracks.append([j['track']['name'], j['track']['id']])

    except Exception as e:
        # internet error caught in spotifyconnect - redirect here
        print("Error recomended: ", e)
        flash("Error: Couldn't get playlist details from Spoify ", "danger")
        return redirect(url_for('dashboard'))

    return render_template('recomended.html', playListTracks=tracks)


#
# @app.route('/your-url')
# def your_url():
#     return render_template('your_url.html',
#                            username=request.args['username'])  # variable 'code' passed in from home.html
#
#     # return 'message'
#     # return render_template('your_url.html', code=request.args['code']) USED THE WRONG NAME FOR YOUR-URL


# ======================================================================================================
def dbSetLikes(likes, spotifyLink):
    try:
        with mysql.connection.cursor() as cursor:

            cursor.execute("UPDATE playlist SET likes = %s WHERE spotifyLink = %s", (likes, spotifyLink))
            cursor.connection.commit()
    except Exception as e:
        print('Error: update_likes: ', e)

@app.route('/update_likes', methods=['POST'])
def update_likes():
    data = request.get_json()
    table_data = data['table_data']
    likes = table_data.get('likes')
    spotifyLink = table_data.get('spotifyLink')

    print('supdate_likes: ', likes, spotifyLink, table_data)
    if likes and spotifyLink:
        dbSetLikes(likes, spotifyLink)

    return 'Table data received and processed successfully'

def dbAddComment(comment, username, spotifyLink):
    try:
        with mysql.connection.cursor() as cursor:
            cursor.execute("INSERT INTO comments(comment,username,spotifyLink) VALUES(%s,%s,%s)",
                     (comment, username, spotifyLink))
            mysql.connection.commit()
    except Exception as e:
        print('update_comments: ', e)

@app.route('/update_comments', methods=['POST'])
def update_comments():
    data = request.get_json()
    table_data = data['table_data']
    comment = table_data.get('comment')
    spotifyLink = table_data.get('spotifyLink')
    username = table_data.get('username')

    if comment and username and spotifyLink:
        dbAddComment(comment, username, spotifyLink)

    return 'Table data received and processed successfully'


def dbGetUserName(userId):
    try:
        with mysql.connection.cursor() as cursor:
            if cursor.execute("SELECT username from friends WHERE id = %s", [userId]):
                data = cursor.fetchone()  #
                name = data.get('username', None)
                return name

    except Exception as e:
        print('dbGetUserName: ', e)
        flash("DB Error couldn't get UserName from database", "danger")

    return False


def dbGetPlaylist(spotifylink):
    try:
        with mysql.connection.cursor() as cursor:
            result = cursor.execute(
                "SELECT userid, playlisttitle, imgLink, likes, spotifylink FROM playlist WHERE spotifylink = %s",
                (spotifylink,))
            if result > 0:
                playList = cursor.fetchone()
                return playList
            else:
                return result
    except:
        return None


def dbGetComments(spotifylink):
    with mysql.connection.cursor() as cursor:  # will close the cursor
        try:
            cursor.execute("SELECT comment,username FROM comments WHERE spotifylink = %s", (spotifylink,))
            result = cursor.fetchall()
        except:
            result = None
    return result


# Get data for friends playlist - called from welcome screen
@app.route("/playlist", methods=["POST"])
@is_logged_in
def playlist():
    try:
        spotifylink = request.form.get("spotifylink")
        playList = dbGetPlaylist(spotifylink)
        if not playList:
            flash("Playlist no longer exists", 'danger')
            return redirect(url_for('welcome'))
        username = dbGetUserName(playList['userid'])
        playList['username'] = username
        tracks = []
        spotifyObject, spotifyId = spotipyConnection()  # spotify object assignment

        # get songs in your playlist and send them to screen
        lst = spotifyObject.playlist_items(spotifylink)
        for j in lst['items']:
            tracks.append([j['track']['name'], j['track']['id']])
        playList['tracks'] = tracks

        commentlist = []
        comments = dbGetComments(spotifylink)
        if comments:
            for j in comments:
                commentlist.append([j['comment'], j['username']])
            playList['comments'] = commentlist

        return render_template("playlist.html", playList=playList)
    except:
        print('Playlist Error: ')
        return redirect(url_for('welcome'))


def dbGetFriends(userId):
    try:
        with mysql.connection.cursor() as cursor:
            if not cursor.execute("SELECT userid, playlisttitle,imgLink,spotifylink from playlist WHERE userid != %s",
                                  [userId]):  # TODO: move to spotify id (provider?)
                return []  # No friends ((
            else:
                friendsPlaylist = cursor.fetchall()

                # TODO Get username from friends table - shold I store username in playlist instead - is this unique??
                # TODO change id to userid??
                for friends in friendsPlaylist:
                    result = cursor.execute("SELECT username from friends WHERE id = %s",
                                            (friends.get('userid'),))  # TODO: move to spotify id (provider?)
                    username = cursor.fetchone().get('username')
                    friends['username'] = username

    except Exception as e:
        print("dbGetFriends Error: ", e)
        flash("Database error getting friends playlists :" + str(e), 'danger')
        return []

    return friendsPlaylist


def db_create():
    cursor = mysql.connection.cursor()
    cursor.execute("SHOW DATABASES")
    databases = cursor.fetchall()


# Default route of the server - if someone types http://127.0.0.1:5000/ into browser
@app.route('/')  # 2 ways to get in - via click on button OR from login straight
@is_logged_in  # @ signifys a a decerator which is a function that extends another function
def welcome():
    try:
        db_create()

        friendsPlaylist = dbGetFriends(session['id'])
        return render_template('welcome.html',
                               playlists=friendsPlaylist)  # sends in the playlist we just got from database
    except Exception as e:
        print("dbGetFriends Error: ", e)
        flash("Database error getting friends playlists :" + str(e), 'danger')
        return render_template('welcome.html',
                               playlists=[])  # view function is defined to handle requests to the home page


# ======================================================================================================

def check_and_create_database():
    try:
        # check if the database exists
        cursor = mysql.connection.cursor()
        cursor.execute("SHOW DATABASES")
        databases = cursor.fetchall()
        database_exists = False
        for database in databases:
            if database[0] == app.config['MYSQL_DB']:
                database_exists = True

        # if the database does not exist, create it
        if not database_exists:
            cursor.execute(f"CREATE DATABASE {app.config['MYSQL_DB']}")
            print("Database created successfully")
        else:
            print("Database already exists")

        cursor.close()
    except Exception as e:
        print("check_and_create_database Error: ", e)

    # todo print statements still log in production mode - need log file?


if __name__ == '__main__':
    # check_and_create_database()
    # db_create()

    app.config['SECRET_KEY'] = 'mysecret1234'
    app.run()  # set the application to run in debug mode to get better feedback about errors.

# todo issues
# if tracks list is empty issue in js cloning
# save-tracks - have names not id's - bac to spotipy will it pick up correct songs??
# seting playListName to false in dashboard
# playlist name breaking on space in dashboard form

# HTTP Error for GET to https://api.spotify.com/v1/playlists/512hrsI8L7e1QlphhNq7On/tracks with Params: {'limit': 100, 'offset': 0, 'fields': None, 'market': None, 'additional_types': 'track,episode'} returned 401 due to The access token expired
