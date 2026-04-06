# Importing the SQL library
import sqlite3

# Simple SQL connection to humidity.db
sqlConnection = sqlite3.connect('humidity.db')
sqlCursor = sqlConnection.cursor()

# sqlCursor.execute()

sqlConnection.commit()
sqlConnection.close()

name = "Name"
time = "12:00"
