#H# Actuation Engine: recieves zoneComparison reading from processing.py and makes actuation decisions

#importing libraies
import sqlite3
import datetime
import json
from processing import zoneComparison

#wattage constants
watt_system_base = 10
watt_humidifier = 50
watt_dehumidifier = 40
watt_idle = 5
interval_seconds = 30 #matches main.py sleep interval

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

    #create wattage table if non-existant
    sqlCursor.execute("""
    CREATE TABLE IF NOT EXISTS logEnergy (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        zoneNum TEXT,
        action TEXT,
        wattsUsed REAL,
        energyKwh REAL
    );
    """)

    totalWatts = watt_system_base

    #actuation process for each reading
    for zoneNum, comparison in zoneComparison.items():
        #recieve zone information and transfer to 'zoneName' variable
        zoneName = zoneNames.get(zoneNum, f"zone{zoneNum}")

        #output action and reason for each reading
        if comparison == "<":
            action = "HUMIDIFER ON"
            reason = f"{zoneName} humidity below threshold"
            watts = watt_humidifier
        elif comparison == ">":
            action = "DEHUMIDIFIER ON"
            reason = f"{zoneName} humidity above range"
            watts = watt_dehumidifier
        else:
            action = "IDLE"
            reason = f"{zoneName} humidity within range"
            watts = watt_idle
        
        totalWatts += watts
        #convert watt seconds into kilowatt hours
        energyKwh = round ((watts * interval_seconds) / 3600000, 6)
        
        print(f"[ACTUATION] Zone {zoneNum}: {action} | {reason}")

        #log actuation into sql
        sqlCursor.execute("""
        INSERT INTO logActuation (zoneNum, action, reason, timestamp)
        VALUES (?, ?, ?, ?)
        """, (zoneNum, action, reason, datetime.datetime.now().isoformat())) #convert to string

        #log watts into sql
        sqlCursor.execute("""
        INSERT INTO logEnergy (timestamp, zoneNum, action, wattsUsed, energyKwh)
        VALUES (?, ?, ?, ?, ?)
        """, (datetime.datetime.now().isoformat(), zoneNum, action, watts, energyKwh))

    print(f"[ENERGY] Total system draw: {totalWatts}W")

    sqlConnection.commit()
    sqlConnection.close()