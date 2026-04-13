#H# Actuation Engine: recieves zoneComparison reading from processing.py and makes actuation decisions

#importing libraies
import sqlite3
import datetime
import json
from processing import zoneComparison

#actuation function
def actuate():
    #connect to database
    sqlConnection = sqlite3.connect('humidity.db')
    sqlCursor = sqlConnection.cursor()

    #load zone profiles from zones.json
    with open ("zones.json", "r") as file:
        data = json.load(file)
    zoneNames = {z["zoneNum"]: f"zone{z['zoneNum']}_{z['zoneName']}" for z in data["zones"]}


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
        """, (zoneNum, action, reason, datetime.datetime.now().isoformat())) #convert to string

    sqlConnection.commit()
    sqlConnection.close()