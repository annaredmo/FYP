# WHAT IS THIS
	Annas FanTrax ... user interface that allows a user to create their own 
            soundtrack for a film of their choice 
	
# WHAT PLATFORMS ARE SUPPORTED
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
        OR change the values in the app.py
		
# INSTALL APPLICATION
	- unzip FanTrax.zip into you folder (venv)
	- cd into FanTrax

# INSTALL PACKAGES
	- pip install -r requirements.txt

# INSTALL MYSQL DATABASE
	- python create_database.py (make sure you set env variables OR edit script and set manually) 
		OR create the database fan_tracks using MySQL)

# RUN FanTrax
	- flask run OR python app.py
	- Open Web Browser on 127.0.0.1:5000
	
# OVERVIEW
	- The Database is pre-loaded with users and Playlists - to login to this app you can use
            username:coolguy password:123 (different to the spotify account). Many app user accounts
            can use the one spotify account.
	- On Login or Register you will be directed to Spotify to authenticate - on completion you will 
		be brought back to FanTrax - you have to complete this step
    - If you do not have a Spotify account - this account and password are available
        until August 2023 username:annaredmo@gmail.com password:fyppassword


# POSSIBLE ISSUES
    - multiple FanTrax servers running on the one machine could cause issues. As session data persists in 
        memory
