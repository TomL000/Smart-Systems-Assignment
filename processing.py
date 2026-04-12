# importing libraries
from doctest import DocTestCase

import sqlite3
import json

# # global variables
# zoneComparison: stores results of comparing readings to threshold to send to actuation
zoneComparison = {}


def humidityMonitor():
    #opening sql connection to humidity.db
    sqlConnection = sqlite3.connect('humidity.db')
    sqlCursor = sqlConnection.cursor()

    with open("zones.json", "r") as file:
        data = json.load(file)

    zones = data["zones"]

    tables = [
        "zone1_propagation",
        "zone2_vegetation",
        "zone3_flowering",
        "zone4_storage",
    ]

    # loops for each zone. each value in tables specifies the humidity.db table fetched from.
    for i, zone in enumerate(zones):
        zoneNum = zone["zoneNum"]
        tableNum = tables[i]

        sqlCursor.execute(f"""
            SELECT *
            FROM {tableNum}
            ORDER BY id DESC
            LIMIT 1
        """)

        row = sqlCursor.fetchone()
        #H# fail safe for empty table
        if row is None:
            print(f"No data yet for zone {zoneNum}, skipping.")
            continue
        #H#
        humidity = row[2]
        if int(humidity) < int(zone["minHumidity"]):
            zoneComparison[zoneNum] = "<"
        elif int(humidity) > int(zone["maxHumidity"]):
            zoneComparison[zoneNum] = ">"
        else:
            zoneComparison[zoneNum] = "="

    sqlConnection.close()

    # temporary printing comparison for feedback that program works
    print(zoneComparison)