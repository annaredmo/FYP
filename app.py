from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from flask_mysqldb import MySQL
from wtforms import Form, StringField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps
import webbrowser
from errorList import errorlist

import os
import requests
from requests.exceptions import ConnectionError
import spotipy
from flask import jsonify
import imdb
import pickle
import logging


ia = imdb.IMDb()



#logging.basicConfig(filename='app.log', level=logging.ERROR)

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'  # TODO: env variables??
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'annas_db'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

clientID = '6c68091ecfa44fe9b55ff6bcc5d81c97'
clientSecret = '36582bf60f224dc3a1035a0335700bef'
redirectURI = 'https://google.com/'

app.secret_key = 'mysecret1234'


# TODO: ISSUE if I dont put global here it crashes ???? even though i am only checking it - dont understand
def spotipyConnection():
    try:
        if 'spotifyId' in session:  # already connected may have to re-connect here
            # spotipyId seems to be in session when I restart the server ?? Maybe another sesion
            #this will stay in memory for 31 days !!!
            print('spotipyConnection: In spotifyid in session')

            serialized_oath_object = session['spotifyOathObject']
            oauth_object = pickle.loads(serialized_oath_object)

            # Check if the access token has expired
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

            return spotifyObject, spotifyId

        else:
            #first log in for this server session
            print('spotipyConnection: logon the session')

            oauth_object = spotipy.SpotifyOAuth(clientID, clientSecret, redirectURI)
            spotifyObject = spotipy.Spotify(auth_manager=oauth_object)
            spotifyId = spotifyObject.me()['id']
            session['spotifyOathObject'] = pickle.dumps(oauth_object)
            session['spotifyId'] = spotifyId

            return spotifyObject, spotifyId
    except spotipy.SpotifyException as e:
        flash("Failed to log into spotify", 'danger')
        return False
        pass
    except spotipy.SpotifyException:
        print("SpotifyError")
    except spotipy.SpotifyOauthError:
        print("SpotifyOauthError")
    except requests.ConnectionError:
        print("Internet down - try again later")
        flash('Internet is down - try again later', 'danger')
    except requests.RequestException:
        print("ERROR requests")
    except Exception as e: # check for NewConnectionError - no internet
        print("ERROR internat?? ",e)
        return 0,0

def getSpotifyObject():


    sp,spId=spotipyConnection()

    return sp
    #
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
    else:
        # handle all other exceptions
        msg = "Error: "

    flash(msg + str(e), 'danger')  # TODO take str(e) out when finished testing
    return redirect(url_for('dashboard'))

class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [validators.DataRequired(),
                                          validators.EqualTo('confirm', message='Password do not match')])
    confirm = PasswordField('confirm Password')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')  # open on login page after login click
    else:        # POST
        clearUser() #in case session data is cashed

        username = request.form['username']  # the username is gotten from the data givin to the form
        password_candidate = request.form['password']  # TODO: needed ?? password candidate is the password from rhe form
        cur = mysql.connection.cursor()  # open connection to db
        result = cur.execute("SELECT * FROM friends WHERE username= %s", [username])  # find that username in the db
        if result > 0:  # if a user is found - check password - TODO do both checks in if
            data = cur.fetchone()  # fetch only the first row (the first user that comes up)
            password = data['password']  ## TODO: needed ??  getting the password from the data
            # TODO passwords are not being compared and letting any password to log in
            if password_candidate == password:  # todo taking out encryption - but good for security	#sha256_crypt.verify(password_candidate,password):
                #spotfyObject, spotifyId = spotipyConnection()  # spotify object assignment
                if (spotipyConnection()):  # if there is a spotify id to be found
                    session['logged_in'] = True  # session is now logged in
                    session['username'] = username  # session username is username inputted
                    session['id'] = data['id']  # session id is the id from the db
                    flash('login successful', 'success')  # success message
                    return redirect(url_for('dashboard'))  # send user to dashboard
                else:
                    error = 'spotify down'  # wrong password message
                   # flash('login failed - spoify is down - try again later', 'danger')  # success message
                    flash(errorlist[2])
                    return render_template('login.html', error=error)  # keep them on the login page
            else:
                error = errorlist[0]  # wrong password message
                cur.close()  # close connection

            return render_template('login.html', error=error)  # keep them on the login page
        else:
            error = errorlist[0]
            return render_template('login.html', error=error)  # if its GET not POST return an error TODO: not true



# to prevent using of app without login
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):  # !!WHAT!!
        if 'logged_in' in session:
            return f(*args, **kwargs)  # !!WHAT!!
        else:
            print("FORST FLAAAAAAAAAAAAAAAAAAAASH",session)
            flash('Please login ', 'danger')
            return redirect(url_for('login'))

    return wrap


def clearUser():
    session.clear()

@app.route('/delete_user')
def delete_user():
    try:
        myCursor = mysql.connection.cursor()

        myCursor.execute("delete  FROM friends WHERE spotifyId =%s", (session['spotifyId'],))    #deleting from db
        mysql.connection.commit()
        myCursor.close()    #close db connection
        clearUser() #clear session and everything else
        flash("Your account has been deleted, until next time friend <3", 'success')
    except:
        flash ("Sorry Having trouble deleting your account right now :( we dont want you to leave ", 'error')
        pass
    return redirect(url_for('/')) # TODO: changed this from home !1 is this correct - test



@app.route('/logout')
def logout():
    clearUser()
    return redirect(url_for('login'))


@app.route('/dashboard') # 2 ways to get in - via click on button OR from login straight
@is_logged_in  # @ signifys a a decerator which is a function that extends another function
def dashboard():
    #session['playListName']=False
    myCursor = mysql.connection.cursor()
    # TODO: change playlist to use spotifylink as key
    result = myCursor.execute("SELECT playlisttitle,imgLink,spotifylink from playlist WHERE userid = %s", [session['id']]) # TODO: move to spotify id (provider?)
    #playlists = myCursor.fetchall()
    session['playlist']=myCursor.fetchall()
    myCursor.close()
    if result > 0:
        # or can just access from session in dashboard
        return render_template('userDashboard.html', playlists=session['playlist'])  # sends in the playlist we just got from database
    else:
        msg = "NO PLAYLIST FOUND "
        return render_template('userDashboard.html', msg=msg)   # view function is defined to handle requests to the home page


#=====================================================================================
#TODO - could change to store imdbID instead??
def storeMovieInDB(movieId,theMovieName,poster):

    print('movie name',movieId,theMovieName,poster)
    try:
        #spotifyObject, spotifyId = spotipyConnection()  # spotify object assignment

        #todo check if it exists first??
        sp=getSpotifyObject()
        print('sp=',sp)
        print('is=',session['spotifyId'])
        spotifyPlaylistId = getSpotifyObject().user_playlist_create(session['spotifyId'], theMovieName)  # getting the link for the sptify playlist

        cur = mysql.connection.cursor()  # oprning sql connection
        # Check if playlist already exists
        if cur.execute("SELECT * FROM playlist WHERE userid= %s AND playlisttitle = %s", (session['id'], theMovieName)):
            msg = 'Playlist already exists:' + theMovieName
            # TODO:  send back to calling function do not render here
            return render_template('add_playlist.html', msg=msg)  # open it in the add_playlist html page
        print("before add",movieId,theMovieName,poster)
        #print("DETAILS ", session['id'], theMovieName, spotifyPlaylistId['id'], poster)

        cur.execute("INSERT INTO playlist(userid,playlisttitle,spotifylink,imgLink) VALUES (%s,%s,%s,%s)",
                    (session['id'], theMovieName, spotifyPlaylistId['id'],poster))  # getting the id from the link
        mysql.connection.commit()  # comming connection to sql
        flash('success')  # success message
        msg = 'Added playlist ' + theMovieName
        print("after add",msg)

    except spotipy.SpotifyException as e:  # if it doesnt connect
        msg = 'Failed to add playlist ' + theMovieName + "LOGOUT/LOGIN AGAIN "
        print("Error storeMovieInDB: ", e, '.')
        flash(msg, 'danger')
        return redirect(url_for('dashboard'))
    except Exception as e:  # if it doesnt connect
        flash("Failed create playlist into spotify", 'danger')  # fail message
        print(e)

    flash(f"Added playlist for Movie {theMovieName}", 'success')


#=====================================================================================

class make_playlist(Form):
    title = StringField('Name', [validators.Length(min=1, max=25)])

def selectMovie(movieName):
    movieResults = ia.search_movie(movieName)


@app.route('/create_playlist', methods=['GET', 'POST'])
@is_logged_in
def create_playlist():
    form = make_playlist(request.form)  # make the playlist using the form element
    if request.method == 'POST' and form.validate():  # if the request is POST
        playlist = form.title.data  # get the data entered in the form and use that as the name for the playlist
        tracks=[]
        # TODO can't get this from global?? So just reconnecting SH
        #spotifyObject, spotifyId = spotipyConnection()  # spotify object assignment
        #user_name = spotifyObject.current_user()  # user name assignmenet
        try:

            movieList = ia.search_movie(playlist)
            print('movie match list',movieList)
            # rerender this page to display table of movied with select button - see recomended.html

            #todo - commenting out so you can add display table to pick from
            #theMovieName = movieList[0]
            #storeMovieInDB(movieList)

            #render add_playlist - sending in movieResults

            myMovieList=[]
            for movie in movieList:
                print(movie.movieID,movie.data['title'], )

                if not movie.data.get('full-size cover url'):
                    print("no img ",movie)
                    movie['full-size cover url']='.\\static\\images\\banner.jpg'
                    #generate dict storing movie id, title and image - for access later - and access via id if needed
                myMovieList.append([movie.movieID,movie.data['title'], movie.get('full-size cover url')])

            return render_template('pickMovie.html', movieList=myMovieList)

        except Exception as e:  # if it doesnt connect
            print(e)

    #Get just display input for name
    return render_template('add_playlist.html', form=form)  # open function in add_playlist.html
import ast
@app.route('/pickMovie' ,methods=['GET', 'POST'])
@is_logged_in
def pickMovie(): #(playlist):
    if request.method == 'GET' :  # if the request is POST
        print("IN  GET")
    #movie = request.form.get("movie")
    movie_json = request.form['movie']
    print('json',movie_json)  # print the JSON string for debugging

    print('str=',ast.literal_eval(movie_json))
    movie = ast.literal_eval(movie_json)
    print(movie[0])


    print("MOVIE =", movie)

    if movie != None:
        print("MOVIE =",movie)
        storeMovieInDB( movieId=movie[0],theMovieName=movie[1],poster=movie[2])
    else:
            flash("No movie picked", 'error')
    return redirect(url_for('dashboard'))


def get_playlistId(playListName):
    pass


@app.route('/delete_playlist/<string:playlist>')
@is_logged_in
def delete_playlist(playlist):
    playlistName = playlist
    # using the Name get the spoitify link - if it suceeds - delete from database
    try:
        myCursor = mysql.connection.cursor()
        # works         result = myCursor.execute("SELECT spotifylink from playlist WHERE playlisttitle = 'playlist'")
        #todo move this to session storing all lists and links - must make sure users have there own session first
        if myCursor.execute("SELECT spotifyLink FROM playlist WHERE userid= %s AND playlisttitle = %s",
                            (session['id'], playlistName)):
            playlistLinks = myCursor.fetchall()  # TODO: in debug access spotipy link - need it to unfollow
            spotifyLink = playlistLinks[0]['spotifyLink']
            msg = "Found"
            # delete from spotify
            #spotfyObject, spotifyId = spotipyConnection()  # spotify object assignment
            myCursor.execute("delete  FROM playlist WHERE spotifylink =%s", (spotifyLink,))
            mysql.connection.commit()
            myCursor.close()

            getSpotifyObject().user_playlist_unfollow(session['spotifyId'], spotifyLink)
        else:
            msg = "NO PLAYLIST FOUND "

        flash("Playlist successfully deleted", 'success')
    except spotipy.SpotifyException as e:

        if e.http_status == 403 and "Insufficient scope" in e.msg:
            flash("Playlist didnt exist on Spoipy" + str(e), 'error')
        else:
            flash("Spotipy error:" + str(e), 'error')

    return redirect(url_for('dashboard'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data   #assignng input values to variables
        email = form.email.data
        username = form.username.data
        password = form.password.data # sha256_crypt.encrypt(str(form.password.data))   #todo encrypt password

        cur = mysql.connection.cursor()
        result = cur.execute("SELECT * FROM friends WHERE username= %s", [username])    #finding any entrys with the same username
        result2 = cur.execute("SELECT * FROM friends WHERE email=%s", [email])  #finding any entries with the same username
        if result > 0:  #if the same username is found
            error = 'User name already exists,please try another user name'
            return render_template('register.html', form=form, error=error) #send an error and tell them they already exist
        if result2 > 0:
            error = 'Email already exists,please try another Email'
            return render_template('register.html', form=form, error=error) #if email already in use ((this one doesmt seem to work but thast ok for now))
        else:
            flash('A confirmation link has been sent to your email', 'success') #if all is succesful send a cnfirmation email(this doesnt do that but it will)

        # check this is a valid spoitify account

        #spotfyObject, spotifyId = spotipyConnection()  # spotify object assignment

        if (spotipyConnection()): #if there is a spotify id to be found
            cur.execute("INSERT INTO friends(name,email,username,password,spotifyId) VALUES(%s,%s,%s,%s,%s)",
                    (name, email, name, password,session['spotifyId'])) #insert these persons details into the db
            mysql.connection.commit()
            cur.close() #commit and close cursor
            flash('Successfully verified', 'success')
            msg = "Welcome "

            return render_template('userDashboard.html', msg=msg)   #redirect to dashboard for this new user
        else:
            flash('No Spoitfy account', 'fail') #else they do not have  a spotify account

    #TODO: should go to login page if successfull - tried but it didnt work ?? is it render or redirect ?? tried both

    return render_template('registrationPage.html', form=form)  #open this function in the rgisterpage


@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/movie')
def movie():
    return render_template('movie.html')

def getOfficialPlaylist(playlistName):
    lst=[]
    spotifyObject, spotifyId = spotipyConnection()  # spotify object assignment

    return lst

@app.route('/update_table', methods=['POST'])
def update_table():
  data = request.get_json()
  table_data = data['table_data']
  #table_data = json.loads(request.form['table_data'])
  # Do something with the table data (e.g., store it in a database)
  print('Table data received and processed successfully')
  print( session['playListName'],table_data)
  #TODO delete playlist from spotify and re-created it with tracks

  myCursor = mysql.connection.cursor()
  # works         result = myCursor.execute("SELECT spotifylink from playlist WHERE playlisttitle = 'playlist'")
  # todo move this to session storing all lists and links - must make sure users have there own session first
  try:
    if myCursor.execute("SELECT spotifyLink FROM playlist WHERE userid= %s AND playlisttitle = %s",
                      (session['id'], session['playListName'])): #check
          playlistLinks = myCursor.fetchall()  # TODO: in debug access spotipy link - need it to unfollow
          spotifyPlayListId = playlistLinks[0]['spotifyLink'] #the spotify Playlist id
          #spotifyObject, spotifyId = spotipyConnection()  # spotify object assignment

          getSpotifyObject().playlist_replace_items(spotifyPlayListId, table_data)  # it wants id as list

  except Exception as e:
      print(e)

  return 'Table data received and processed successfully'


@app.route('/searchForMatchingTracks', methods=['POST'])
def searchForMatchingTracks():
    searchName = request.json.get('song_name')
    table_data = request.json.get('table_data')

    #spotifyObject, spotifyId = spotipyConnection()  # spotify object assignment
    results = getSpotifyObject().search(searchName, 10, 0, "track")
    songs_dict = results['tracks']
    song_items = songs_dict['items']
    song = song_items[0]['external_urls']['spotify']

    lst = results['tracks']
    trackList=[]

    for j in lst['items']:
        # only add to list if not already in not in playlist
        if j['id'] not in table_data:
            print(j['name'])
            trackList.append([j['name'], j['id']])  #list of lists
    return jsonify(trackList)


@app.route('/getSongData',methods=['GET', 'POST'])
def getSongData():

    #
    data = request.get_json()
    table_data = data['table_data']
    print(session['playListName'], table_data)


    #spotifyObject, spotifyId = spotipyConnection()  # spotify object assignment
    trackList=[]
    results = getSpotifyObject().search(session['playListName'] + ' soundtrack', 1, 0, type="album")
    album_id = results['albums']['items'][0]['id']  # todo picking up first only - shhould we ask
    lst = getSpotifyObject().album_tracks(album_id)
    print(lst['items'][0]['name'])  # name of track
    for j in lst['items']:
        # only add to list if not already in not in playlist
        # todo first time only in session after that in
        if j['id'] not in table_data:
            print(j['name'])  ######yessssssss prints out all songs
            trackList.append([j['name'], j['id']])  #list of lists
    ## TODO FIX ??
    return jsonify(trackList)

#todo - need a save button for updated list - to go to spotify - need function like this savePlayList

class make_recommended(Form): #Not working
    title = StringField('playlistTitle')

#TODO issues:
# Remove and Add do not update the session data - so load buttons will loose all the data and be replaced
# by original??
@app.route('/recomended' ,methods=['GET', 'POST'])#/<string:playlist>') # spell check
@is_logged_in
def recomended(): #(playlist):
    if request.method == 'GET' :  # if the request is POST
        pass
    playListName = request.form.get("playlistTitle")
    action = request.form.get("load_button")
    tracks = []

    if playListName != None:
        session['playListName']=playListName
        # if session.get("playListTracks") is None: # Only load from DB if not already loaded
        if True:  #not sure he need to load every time??
            session["playListTracks"] = []
            try:
                # TODO only get from db if  empty
                myCursor = mysql.connection.cursor()
                # works         result = myCursor.execute("SELECT spotifylink from playlist WHERE playlisttitle = 'playlist'")
                if myCursor.execute("SELECT spotifyLink FROM playlist WHERE userid= %s AND playlisttitle = %s",
                                    (session['id'], playListName)):
                    playlistLink = myCursor.fetchall()  # TODO: in debug access spotipy link - need it to unfollow
                    spotifyLink = playlistLink[0]['spotifyLink']

                    spotifyObject, spotifyId = spotipyConnection()  # spotify object assignment
                    # get songs in your playlist and send them to screen
                    lst = spotifyObject.playlist_items(spotifyLink)
                    for j in lst['items']:
                        tracks.append([j['track']['name'],j['track']['id']])

            except Exception as e:
                print("Error recomended: ", e,'.')
                flash("Error getting Playlist tracks from SpotifyT LOGOTU/LOGIN AGAIN ", 'error')
                return redirect(url_for('dashboard'))

    # TODO do we set back to 0 every time ??
    # add/remove and then click official - even if you have saved - goes back to original list
    # can add get from spotify each time - but it still won't get non-saved ??
    #session["selectTracksFrom"] = []
    if action != None:
        if action == "Recommended": #todo
            pass
            # for j in lst['items']:
            #     session["selectTracksFrom"].append(j['track']['name'])
        # elif action == "Official Soundtrack": #TODO function to get from spotify usingplayListName
        #     spotifyObject, spotifyId = spotipyConnection()  # spotify object assignment
        #
        #     results = spotifyObject.search(session['playListName'] + ' soundtrack', 1, 0, type="album")
        #     album_id = results['albums']['items'][0]['id'] #todo picking up first only - shhould we ask
        #     lst = spotifyObject.album_tracks(album_id)
        #     print(lst['items'][0]['name'])  # name of track
        #     for j in lst['items']:
        #         # only add to list if not already in not in playlist
        #         if [j['name'],j['id']] not in session["playListTracks"]:
        #             print(j['name'])  ######yessssssss prints out all songs
        #             session["selectTracksFrom"].append([j['name'],j['id']])  # list of lists

        elif action == "Search":
            pass

    print('CONTENTS OF LIST: ', playListName,tracks)

    return render_template('recomended.html',playListTracks=tracks )


#
# if request.method == 'POST':
#     if 'load_button' in request.form:
#         if request.form['load_button'] == 'Official Soundtrack':
#             # Handle Official Soundtrack button click
#             pass
#         elif request.form['load_button'] == 'Reccomended':
#             # Handle Reccomended button click
#             pass
#         elif request.form['load_button'] == 'Search':
#             song_name = request.form['song_name']
#             # Handle Search button click with song_name variable
#             pass
#     elif 'save_button' in request.form:
#         # Handle SAVE tracks button click
#         pass


@app.route('/your-url')
def your_url():
    return render_template('your_url.html',
                           username=request.args['username'])  # variable 'code' passed in from home.html

    # return 'message'
    # return render_template('your_url.html', code=request.args['code']) USED THE WRONG NAME FOR YOUR-URL



#======================================================================================================

@app.route('/update_likes', methods=['POST'])
def update_likes():
  data = request.get_json()
  table_data = data['table_data']
  likes=table_data.get('likes')
  spotifyLink=table_data.get('spotifyLink')

  print('supdate_likes: ',likes,spotifyLink,table_data)
  if likes and spotifyLink:
        myCursor = mysql.connection.cursor()
        try:
            myCursor.execute("UPDATE playlist SET likes = %s WHERE spotifyLink = %s", (likes, spotifyLink))
            mysql.connection.commit()

        except Exception as e:
            print(e)

        myCursor.close()

  return 'Table data received and processed successfully'


@app.route('/update_comments', methods=['POST'])
def update_comments():
  data = request.get_json()
  table_data = data['table_data']
  comment=table_data.get('comment')
  spotifyLink=table_data.get('spotifyLink')
  username=table_data.get('username')


  print('update_comments: ',comment,spotifyLink,username)
  if comment and spotifyLink:
        myCursor = mysql.connection.cursor()
        try:
            myCursor.execute("INSERT INTO comments(comment,username,spotifyLink) VALUES(%s,%s,%s)",
                        (comment,username, spotifyLink))

            mysql.connection.commit()

        except Exception as e:
            print(e)

        myCursor.close()

  return 'Table data received and processed successfully'

def dbGetUserName(userId):
    myCursor = mysql.connection.cursor()
    result = myCursor.execute(
        "SELECT username from friends WHERE id = %s", (userId,))
    data = myCursor.fetchone()  #
    myCursor.close()

    name = data.get('username')
    return name



@app.route("/playlist", methods=["POST"])
@is_logged_in
def playlist():
    spotifylink = request.form.get("spotifylink")

    myCursor = mysql.connection.cursor()
    result = myCursor.execute("SELECT userid, playlisttitle,imgLink,likes,spotifylink from playlist WHERE spotifylink = %s", (spotifylink,))

    if result > 0:

        playList = myCursor.fetchone()  #
        myCursor.close()
        username=dbGetUserName(playList['userid'])
        playList['username']=username
        tracks=[]

        spotifyObject, spotifyId = spotipyConnection()  # spotify object assignment
        # get songs in your playlist and send them to screen
        lst = spotifyObject.playlist_items(spotifylink)
        for j in lst['items']:
            tracks.append([j['track']['name'], j['track']['id']])
        playList['tracks']=tracks

        myCursor = mysql.connection.cursor()
        result = myCursor.execute(
            "SELECT comment,username from comments WHERE spotifylink = %s",(spotifylink,))
        comments = myCursor.fetchall()  #

        commentlist=[]
        for j in comments:
            commentlist.append([j['comment'],j['username']])
        playList['comments']=commentlist


        return render_template("playlist.html", playList=playList)
    else:
        myCursor.close()
        flash("Playlist doesn't exist", 'danger')
        return render_template("welcome.html")




# Default route of the server - if someone types http://127.0.0.1:5000/ into browser
@app.route('/') # 2 ways to get in - via click on button OR from login straight
@is_logged_in  # @ signifys a a decerator which is a function that extends another function
def welcome():
    myCursor = mysql.connection.cursor()
    # TODO: change playlist to use spotifylink as key

    result = myCursor.execute("SELECT userid, playlisttitle,imgLink,spotifylink from playlist WHERE userid != %s", [session['id']]) # TODO: move to spotify id (provider?)

    #playlists = myCursor.fetchall()
    friendsPlaylist=myCursor.fetchall()

    #TODO Get username from friends table - shold I store username in playlist instead - is this unique??
    #TODO change id to userid??
    for friends in friendsPlaylist:
        result2 = myCursor.execute("SELECT username from friends WHERE id = %s", (friends.get('userid'),)) #TODO: move to spotify id (provider?)
        username=myCursor.fetchone().get('username')
        friends['username']=username
    myCursor.close()

    if result > 0:
        # or can just access from session in dashboard
        return render_template('welcome.html', playlists=friendsPlaylist)  # sends in the playlist we just got from database
    else:
        return render_template('welcome.html', [])   # view function is defined to handle requests to the home page

#======================================================================================================
#todo print statements still log in production mode - need log file?

if __name__ == '__main__':
    app.config['SECRET_KEY'] = 'mysecret1234'


    app.run() #set the application to run in debug mode to get better feedback about errors.

#todo issues
# if tracks list is empty issue in js cloning
# save-tracks - have names not id's - bac to spotipy will it pick up correct songs??
# seting playListName to false in dashboard
#playlist name breaking on space in dashboard form

#HTTP Error for GET to https://api.spotify.com/v1/playlists/512hrsI8L7e1QlphhNq7On/tracks with Params: {'limit': 100, 'offset': 0, 'fields': None, 'market': None, 'additional_types': 'track,episode'} returned 401 due to The access token expired
