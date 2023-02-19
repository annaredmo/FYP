from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from flask_mail import Mail, Message
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
import webbrowser
from errorList import errorlist

import os
from bs4 import BeautifulSoup
import requests
from requests.exceptions import ConnectionError
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

import json
from flask import jsonify
from imdb import Cinemagoer


ia = Cinemagoer()


spotifyObjectG = 0
spotifyIdG = 0
userData={}

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'  # TODO: env variables??
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'annas_db'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)



# TODO: ISSUE if I dont put global here it crashes ???? even though i am only checking it - dont understand
def spotipyConnection():
    global spotifyObjectG, spotifyIdG # it sees I assign it further down so need global!!

    if spotifyObjectG != 0:  # alreadt connected may have to re-connect here
        return spotifyObjectG, spotifyIdG
    try:

        clientID = '6c68091ecfa44fe9b55ff6bcc5d81c97'
        clientSecret = '36582bf60f224dc3a1035a0335700bef'
        redirectURI = 'https://google.com/'
        oauth_object = spotipy.SpotifyOAuth(clientID, clientSecret, redirectURI)
        token_dict = oauth_object.get_access_token()  # can cause an error if there but has an issue # looks in cache file for token - if none goes to spotify
        token = token_dict['access_token']

        spotifyObjectG = spotipy.Spotify(auth=token)
        me=spotifyObjectG.me()['id'] #gives info about current user

        spotifyIdG = spotifyObjectG.me()['id']
        userData['spotifyObject'] = spotifyObjectG
        userData['spotifyId'] = spotifyIdG

        return spotifyObjectG, spotifyIdG
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



@app.errorhandler(Exception)
def basic_error(e):
    print("An error occured:" + str(e))
    # render an error page
    return redirect(url_for('dashboard'))

# Default route of the server - if someone types http://127.0.0.1:5000/ into browser
@app.route('/')
def welcome():
    return render_template('welcome.html')

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
        username = request.form['username']  # the username is gotten from the data givin to the form
        password_candidate = request.form['password']  # TODO: needed ?? password candidate is the password from rhe form
        cur = mysql.connection.cursor()  # open connection to db
        result = cur.execute("SELECT * FROM friends WHERE username= %s", [username])  # find that username in the db
        if result > 0:  # if a user is found - check password - TODO do both checks in if
            data = cur.fetchone()  # fetch only the first row (the first user that comes up)
            password = data['password']  ## TODO: needed ??  getting the password from the data
            # TODO passwords are not being compared and letting any password to log in
            if password_candidate == password:  # todo taking out encryption - but good for security	#sha256_crypt.verify(password_candidate,password):
                spotfyObject, spotifyId = spotipyConnection()  # spotify object assignment
                if (spotifyId):  # if there is a spotify id to be found
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
            return render_template('login.html', error=error)  # keep them on the login page
            cur.close()  # close connection
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
            flash('Please login ', 'danger')
            return redirect(url_for('login'))

    return wrap


def clearUser():
    global spotifyIdG, spotifyObjectG
    session.clear()
    spotifyIdG, spotifyObjectG =0, 0

@app.route('/delete_user')
def delete_user():
    try:
        myCursor = mysql.connection.cursor()

        myCursor.execute("delete  FROM friends WHERE spotifyId =%s", (spotifyIdG,))    #deleting from db
        mysql.connection.commit()
        myCursor.close()    #close db connection
        clearUser() #clear session and everything else
        flash("Your account has been deleted, until next time friend <3", 'success')
    except:
        flash ("Sorry Having trouble deleting your account right now :( we dont want you to leave ", 'error')
        pass
    return redirect(url_for('/')) # TODO: anna changed this from home !1 is this correct - test



@app.route('/logout')
def logout():
    clearUser()
    flash('you are now logged out')
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
def storeMovieInDB(movieId,movieList):
    theMovieName=movieList[0]
    poster=movieList[1]
    print('movie name',movieId,theMovieName,poster)
    try:
        spotifyObject, spotifyId = spotipyConnection()  # spotify object assignment

        spotifyPlaylistId = spotifyObject.user_playlist_create(userData['spotifyId'], theMovieName)  # getting the link for the sptify playlist

        cur = mysql.connection.cursor()  # oprning sql connection
        # Check if playlist already exists
        if cur.execute("SELECT * FROM playlist WHERE userid= %s AND playlisttitle = %s", (session['id'], theMovieName)):
            msg = 'Playlist already exists:' + theMovieName
            # TODO:  send back to calling function do not render here
            return render_template('add_playlist.html', msg=msg)  # open it in the add_playlist html page
        print("before add",theMovieName)
        print("DETAILS ", session['id'], theMovieName, spotifyPlaylistId['id'], poster)

        cur.execute("INSERT INTO playlist(userid,playlisttitle,spotifylink,imgLink) VALUES (%s,%s,%s,%s)",
                    (session['id'], theMovieName, spotifyPlaylistId['id'],poster))  # getting the id from the link
        mysql.connection.commit()  # comming connection to sql
        flash('success')  # success message
        msg = 'Added playlist ' + theMovieName
        print("after add",msg)

    except spotipy.SpotifyException as e:  # if it doesnt connect
        flash("Failed create playlist into spotify", 'danger')  # fail message
        msg = 'Failed to add playlist ' + theMovieName
        pass
    except Exception as e:  # if it doesnt connect
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

        # TODO can't get this from global?? So just reconnecting SH
        spotifyObject, spotifyId = spotipyConnection()  # spotify object assignment
        print(userData['spotifyId'])
        user_name = spotifyObject.current_user()  # user name assignmenet
        try:

            movieList = ia.search_movie(playlist)
            print('movie match list',movieList)
            # rerender this page to display table of movied with select button - see recomended.html

            #todo - commenting out so you can add display table to pick from
            #theMovieName = movieList[0]
            #storeMovieInDB(movieList)

            #render add_playlist - sending in movieResults

            myMovieList={}
            for movie in movieList:
                print(movie.movieID,movie.data['title'], movie.data.get('cover url'))
                if not movie.data.get('cover url'): #todo: check this
                    print("no img ",movie)
                    movie['cover url']='.\\static\\images\\banner.jpg'
                #generate dict storing movie id, title and image - for access later - and access via id if needed
                myMovieList[movie.movieID]=[movie.data['title'], movie.data.get('cover url')]

            session['currentMovieList']= myMovieList

            return render_template('pickMovie.html', movieList=movieList)

        except Exception as e:  # if it doesnt connect
            print(e)

    #Get just display input for name
    return render_template('add_playlist.html', form=form)  # open function in add_playlist.html

@app.route('/pickMovie' ,methods=['GET', 'POST'])
@is_logged_in
def pickMovie(): #(playlist):
    if request.method == 'GET' :  # if the request is POST
        print("IN  GET")
    movie = request.form.get("movie")

    # using the Name get the spoitify link - if it suceeds - delete from database
    if movie != None:
        #print("MOVIE =",movie)
        #need more error checking
        movieDict=session.get('currentMovieList',None)
        selectedMovie=movieDict.get(movie)
        if selectedMovie != None:
            storeMovieInDB(movie,selectedMovie)
        else:
            flash("Movie didn't exist", 'error')
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
            spotfyObject, spotifyId = spotipyConnection()  # spotify object assignment
            spotfyObject.user_playlist_unfollow(spotifyId, spotifyLink)
            myCursor.execute("delete  FROM playlist WHERE spotifylink =%s", (spotifyLink,))
            mysql.connection.commit()
        else:
            msg = "NO PLAYLIST FOUND "

        myCursor.close()
        flash("Playlist successfully deleted", 'success')
    except:
        flash("Playlist didnt get deleted", 'error')
        pass
    # message??
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

        spotfyObject, spotifyId = spotipyConnection()  # spotify object assignment

        if (spotifyId): #if there is a spotify id to be found
            cur.execute("INSERT INTO friends(name,email,username,password,spotifyId) VALUES(%s,%s,%s,%s,%s)",
                    (name, email, name, password,spotifyId)) #insert these persons details into the db
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
          spotifyObject, spotifyId = spotipyConnection()  # spotify object assignment

          spotifyObject.playlist_replace_items(spotifyPlayListId, table_data)  # it wants id as list

  except Exception as e:
      print(e)

  return 'Table data received and processed successfully'


@app.route('/get_song_data',methods=['GET', 'POST'])
def get_song_data():
    # Your code to fetch the list of songs goes here
    #
    data = request.get_json()
    table_data = data['table_data']
    print(session['playListName'], table_data)


    spotifyObject, spotifyId = spotipyConnection()  # spotify object assignment
    trackList=[]
    results = spotifyObject.search(session['playListName'] + ' soundtrack', 1, 0, type="album")
    album_id = results['albums']['items'][0]['id']  # todo picking up first only - shhould we ask
    lst = spotifyObject.album_tracks(album_id)
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
    #playlistName = request.form['playlistTitle'] #.title.data  # get the data entered in the form and use that as the name for the playlist
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
                    #tracks = spotfyObject.??getplaylistcontent??(spotifyId, spotifyLink)
                    # get songs in your playlist and send them to screen
                    lst = spotifyObject.playlist_items(spotifyLink)
                    print('CONTENTS OF LIST: ', playListName)
                    tracks=[]
                    for j in lst['items']:
                        tracks.append(j['track']['name'])
                        session["playListTracks"].append([j['track']['name'],j['track']['id']])
            except:
                flash("Error getting Playlist tracks from Spotify", 'error')
                return redirect(url_for('dashboard'))

    # TODO do we set back to 0 every time ??
    # add/remove and then click official - even if you have saved - goes back to original list
    # can add get from spotify each time - but it still won't get non-saved ??
    session["selectTracksFrom"] = []
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
            track_name = request.form['song_name']
            spotifyObject, spotifyId = spotipyConnection()  # spotify object assignment
            results = spotifyObject.search(track_name, 10, 0, "track")
            songs_dict = results['tracks']
            song_items = songs_dict['items']
            song = song_items[0]['external_urls']['spotify']

            lst=results['tracks']
            for j in lst['items']:
                # only add to list if not already in not in playlist
                if [j['name'], j['id']] not in session["playListTracks"]:
                    print(j['name'])  ######yessssssss prints out all songs
                    session["selectTracksFrom"].append([j['name'], j['id']])  ####put in a list

    return render_template('recomended.html')


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


if __name__ == '__main__':
    app.secret_key = 'secret123'
    app.run(debug=True) #set the application to run in debug mode to get better feedback about errors.


#todo issues
# if tracks list is empty issue in js cloning
# save-tracks - have names not id's - bac to spotipy will it pick up correct songs??
# seting playListName to false in dashboard
#playlist name breaking on space in dashboard form

