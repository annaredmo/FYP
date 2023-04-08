# WHAT IS THIS
	Annas FanTrax ...
	
# WHERE DOES IT RUN
	Runs on Windows 10. 
	
# REQUIREMENTS
	- MySQL - with database create permissions
	- Python 10 
	- Internet
	- Spotify Account
	- Chrome/Edge
	
# SETUP
	Please ensure the following are on the machine
	- python 10 or later - and python Scripts folder is on your path
	- MySQL - with database create permission - username and password
	- set the following environment variables
		- MYSQL_USER <username>
		- MYSQL_PASSWORD <password>
		
# INSTALL APPLICATION
	- unzip FYP-MASTER.zip into you folder (venv)
	- cd into FYP_MASTER

# INSTALL PACKAGES
	- pip install -r requirements.txt

# INSTALL MYSQL DATABASE
	- python create_database.py (make sure you set env variables OR edit script and set manually) OR create the database fan_tracks using MySQL)

# RUN FanTrax
	- flask run OR python app.py
	- Open Web Browser on 127.0.0.1:5000
	
# OVERVIEW
	- The Database is pre-loaded with users and Playlists - try username:coolguy password:123
	- On Login or Register you will be directed to Spotify to authenticate - on completion you will be brought back to FanTrax - you have to complete this step


# POSSIBLE ISSUE