# importing libraries
from presentation import userMenu
import time
import datetime
import sqlite3
from processing import humidityMonitor
#H# adding simulation layer start-up
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

    #H# Resolving zone sequencing issue by creating tables in main.py
    sqlConnection = sqlite3.connect('humidity.db')
    sqlCursor = sqlConnection.cursor()
    zone_tables = [
        "zone1_propagation",
        "zone2_vegetation",
        "zone3_flowering",
        "zone4_storage"
    ]
    for zone in zone_tables:
        sqlCursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {zone} (
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