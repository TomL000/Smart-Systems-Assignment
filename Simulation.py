import sqlite3
import random
import time

def genHumidity():
    return round (random.uniform(30, 80), 2)

sqlConnection = sqlite3.connect("humidity.db")
sqlCursor = sqlConnection.cursor()

for _ in range(20):
    humidity = genHumidity()

    # cursor.execute("INSERT INTO humidity_reading (humidity) VALUES (?)", (humidity,))
    # sqlConnection.commit()

    print (f"recorded humidity {humidity}%")
    time.sleep(1)
sqlConnection.close()
