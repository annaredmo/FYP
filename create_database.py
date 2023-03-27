import mysql.connector
import os

host = os.environ.get('MYSQL_HOST', 'localhost')
user = os.environ.get('MYSQL_USER', 'yourusername')
password = os.environ.get('MYSQL_PASSWORD', 'yourpassword')

# get the MySQL database name from the environment or use a default value
database_name = os.environ.get('MYSQL_DATABASE', 'annas-other-db')

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
