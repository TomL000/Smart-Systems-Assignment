# importing libraries
from presentation import userMenu
import time
import datetime
import sqlite3
from processing import humidityMonitor
#H#
import json #add json integration
#add actuation
from actuation import actuate
#adding simulation layer start-up
import threading
import Simulation #DEV ONLY - simulates deployed sensor feed

def startSimulation():
    # DEV ONLY - Launches simulation as background thread to seed database with readings
    dev_thread = threading.Thread(target=Simulation.run, daemon=True)
    dev_thread.start()
    time.sleep(12) #allow simulation to populate
    #H#

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

    userMenu()
    startSimulation()
    print("Press CTRL+C to pause humidity monitoring and return to menu.")
    # loops humidity monitoring function until user hits CTRL-C to return to menu, where they may quit, adjust or continue.
    while True:
        try:
            humidityMonitor()
            actuate()
            time.sleep(30)
        except KeyboardInterrupt:
            print("\nINTERRUPT\n")
            sqlConnection = sqlite3.connect('humidity.db')
            sqlCursor = sqlConnection.cursor()
            sqlCursor.execute("""
            INSERT INTO logActions (action, timestamp)
            VALUES (?, ?);
            """, (
                "Interrupt", datetime.datetime.now().isoformat()
            ))
            sqlConnection.commit()
            sqlConnection.close()
            userMenu()

# executes main code
main()