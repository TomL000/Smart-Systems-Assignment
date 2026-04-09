# importing libraries
from presentation import userMenu
import sqlite3
import json
import time

# # global variables
# zoneComparison: stores results of comparing readings to threshold to send to actuation
zoneComparison = {}


def humidityMonitor():
    #opening sql connection to humidity.db
    sqlConnection = sqlite3.connect('humidity.db')
    sqlCursor = sqlConnection.cursor()
    sqlCursor.execute("""
        SELECT *
        FROM humidity_readings
        ORDER BY id DESC
        LIMIT 4
    """)
    rows = sqlCursor.fetchall()
    rows.reverse()
    with open("zones.json", "r") as file:
        data = json.load(file)
    zones = data["zones"]
    # stores comparison results in zoneComparison dictionary
    for i, row in enumerate(rows):
        humidity = row[2]
        zone = zones[i]
        zoneNum = zone["zoneNum"]

        if int(humidity) < int(zone["minHumidity"]):
            zoneComparison[zoneNum] = "<"
        elif int(humidity) > int(zone["maxHumidity"]):
            zoneComparison[zoneNum] = ">"
        else:
            zoneComparison[zoneNum] = "="

    sqlConnection.close()

    # temporary printing comparison for feedback that program works
    print(zoneComparison)


# main code sequence
def main():
    userMenu()
    print("Press CTRL+C to pause humidity monitoring and return to menu.")
    # loops humidity monitoring function until user hits CTRL-C to return to menu, where they may quit, adjust or continue.
    while True:
        try:
            humidityMonitor()
            time.sleep(30)
        except KeyboardInterrupt:
            print("\nINTERRUPT\n")
            userMenu()

# executes main code
main()