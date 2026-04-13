# importing libraries
import datetime
import sqlite3
#H#
import json #add json integration
from frontend import main as startFrontend

# main code sequence
def main():
    sqlConnection = sqlite3.connect('humidity.db')
    sqlCursor = sqlConnection.cursor()
    sqlCursor.execute("""
    CREATE TABLE IF NOT EXISTS logActions (
        action TEXT,
        timestamp TEXT
    );
    """)
    sqlCursor.execute("""
    INSERT INTO logActions (action, timestamp)
    VALUES (?, ?);
    """, (
        "Startup", datetime.datetime.now().isoformat()
    ))
    sqlConnection.commit()
    sqlConnection.close()

    #H# Resolving zone sequencing issue by creating tables in main.py, zone profiles loaded from zones.json rather than hardcoded
    sqlConnection = sqlite3.connect('humidity.db')
    sqlCursor = sqlConnection.cursor()
    
    #load json data
    with open("zones.json", "r") as file:
        data = json.load(file)

    #create sql tables from zones.json
    for zone in data ["zones"]:
        tableName = f"zone{zone['zoneNum']}_{zone['zoneName']}"
        sqlCursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {tableName} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            humidity REAL
        )
        """)
    sqlConnection.commit()
    sqlConnection.close()

    #launches frontend.py, which handels simulation, processing, actuation, and presentation layers
    startFrontend()

# executes main code
main()