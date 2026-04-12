#H# Actuation Engine: recieves zoneComparison reading from processing.py and makes actuation decisions

#importing libraies
import sqlite3
import datetime
from processing import zoneComparison

#zone name mapping for readble log messages
zoneNames = {
    "1": "zone1_propagation",
    "2": "zone2_vegetation",
    "3": "zone3_flowering",
    "4": "zone4_storage"
}

#actuation function
def actuate():
    #connect to database
    sqlConnection = sqlite3.connect('humidity.db')
    sqlCursor = sqlConnection.cursor()

    #create actuation log table if it doesn't exist
    sqlCursor.execute("""
    CREATE TABLE IF NOT EXISTS logActuation (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        zoneNum TEXT,
        action TEXT,
        reason TEXT,
        timestamp TEXT
    );
    """)

    #actuation process for each reading
    for zoneNum, comparison in zoneComparison.items():
        #recieve zone information and transfer to 'zoneName' variable
        zoneName = zoneNames.get(zoneNum, f"zone{zoneNum}")

        #output action and reason for each reading
        if comparison == "<":
            action = "HUMIDIFER ON"
            reason = f"{zoneName} humidity below threshold"
        elif comparison == ">":
            action = "DEHUMIDIFIER ON"
            reason = f"{zoneName} humidity above range"
        else:
            action = "IDLE"
            reason = f"{zoneName} humidity within range"
        
        print(f"[ACTUATION] Zone {zoneNum}: {action} | {reason}")

        #log into sql
        sqlCursor.execute("""
        INSERT INTO logActuation (zoneNum, action, reason, timestamp)
        VALUES (?, ?, ?, ?)
        """, (zoneNum, action, reason, datetime.datetime.now().isoformat()))

    sqlConnection.commit()
    sqlConnection.close()