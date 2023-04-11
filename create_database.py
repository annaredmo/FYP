import mysql.connector
import os
import subprocess


# Setting up the database for FanTrax
#Please set envirooment cariables for MYSQL_USER and MYSQL_PASSWORD or update the python variables

host = os.environ.get('MYSQL_HOST', 'localhost')
user = os.environ.get('MYSQL_USER', 'root')
password = os.environ.get('MYSQL_PASSWORD', 'password')

database_name = "fan_tracks"


try:
    # establish a connection to the MySQL server
    mydb = mysql.connector.connect(
      host=host,
      user=user,
      password=password
    )

    # check if the database exists
    mycursor = mydb.cursor()
    mycursor.execute("SHOW DATABASES")
    databases = mycursor.fetchall()
    database_exists = False
    for database in databases:
        if database[0] == database_name:
            database_exists = True

    # if the database does not exist, create it
    if not database_exists:
        mycursor.execute("CREATE DATABASE {}".format(database_name))
        print("Database created successfully")
    else:
        print("Database already exists")
        
    dir = os.path.dirname(os.path.abspath(__file__))
    sqlFile = os.path.join(dir, "fan_tracks.sql")

    subprocess.run(['mysql', '-u', user, '-p' + password, 'fan_tracks', '<', sqlFile], shell=True)
    print("==================== CREATED DATABASE - Please run - flask run (or python app.py) =====================")
 
except Exception as e:
    print("==================== ERROR =====================")
    print("Error creating database for FanTrax database")
    print("check username and password for MYSql - set as environment variables or update python variables: ")
    print(e)
 