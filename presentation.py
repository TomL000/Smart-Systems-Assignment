# Importing libraries
import sqlite3
import time
import sys
import json
import datetime


# displays program name to user. feel free to rename or adjust
print("# # # HUMIDITY MANAGEMENT SYSTEM # # #\n")


def humidityAdjustment():
    # receives and validates user input for zone to adjust
    zoneToAdjust = str(input("Please enter the zone you would like to adjust (1-4): "))
    if not zoneToAdjust.isdigit():
        print("Error - Selected zone must be a number")
        return
    if int(zoneToAdjust) < 1 or int(zoneToAdjust) > 4:
        print("Error - Must select a zone between 1-4 (Inclusive)")
        return
    # receives and validates user input for minimum humidity value
    minAdjust = str(input("Please enter the minimum humidity threshold (0-99): "))
    if not minAdjust.isdigit():
        print("Error - Selected minimum humidity threshold must be a number")
        return
    if int(minAdjust) < 0 or int(minAdjust) > 99:
        print("Error - Selected minimum humidity threshold must be a number between 0-99 (Inclusive)")
        return
    # receives and validates user input for maximum humidity value
    maxAdjust = str(input("Please enter the maximum humidity threshold (1-100): "))
    if not maxAdjust.isdigit():
        print("Error - Selected maximum humidity threshold must be a number")
        return
    if int(maxAdjust) < 1 or int(maxAdjust) > 100:
        print("Error - Selected maximum humidity threshold must be a number between 1-100 (Inclusive)")
        return

    # writes user inputs to  the relevant zone in the zones.json file
    with open("zones.json", "r") as file:
        data = json.load(file)
    zones = data["zones"]
    minPrevious = 0
    maxPrevious = 0
    for zone in zones:
        if zone["zoneNum"] == zoneToAdjust:
            minPrevious = zone["minHumidity"]
            maxPrevious = zone["maxHumidity"]
            zone["minHumidity"] = minAdjust
            zone["maxHumidity"] = maxAdjust
            break
    with open("zones.json", "w") as file:
        json.dump(data, file)
    print("\nAdjustment saved.\n")

    # Create/open humidity database, create/open log1 table
    sqlConnection = sqlite3.connect('humidity.db')
    sqlCursor = sqlConnection.cursor()
    sqlCursor.execute("""
    CREATE TABLE IF NOT EXISTS log1 (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        zoneNum TEXT,
        previousMin REAL,
        newMin REAL,
        previousMax REAL,
        newMax REAL,
        timestamp TEXT
    );
    """)

    # insert previous & new humidity thresholds & timestamp to log table
    sqlCursor.execute("""
    INSERT INTO log1 (zoneNum, previousMin, newMin, previousMax, newMax, timestamp)
    VALUES (?, ?, ?, ?, ?, ?);
    """, (
        zoneToAdjust, minPrevious, minAdjust, maxPrevious, maxAdjust, datetime.datetime.now().isoformat()
    ))

    sqlConnection.commit()
    sqlConnection.close()
    #
    time.sleep(2)


# prints current max & min humidity values of each zone from zones.json to terminal
def displayZones():
    with open("zones.json", "r") as file:
        data = json.load(file)
    zones = data["zones"]
    print("Current Zone Humidity Thresholds:\n")
    for zone in zones:
        print(f"Zone {zone['zoneNum']}: "
              f"Min Humidity = {zone['minHumidity']}%, "
              f"Max Humidity = {zone['maxHumidity']}%\n")


# function displaying functional menu to user
def userMenu():
    while True:
        print("1 - Adjust Humidity Threshold \n2 - Begin Humidity Management System\n3 - View Current Humidity Thresholds\n4 - Quit")
        menuInput = str(input("Please select an option from the above list (1-4): "))
        # allows user to adjust a zones min/max humidity thresholds
        if menuInput == "1":
            humidityAdjustment()

        # exits menu while loop and moves on to running automated humidity management system
        elif menuInput == "2":
            print("Starting system . . . .")
            time.sleep(2)
            break
        # prints current max & min humidity values of each zone to terminal
        elif menuInput == "3":
            displayZones()
            #write code to print current max/min humidity values
        # quits the program
        elif menuInput == "4":
            print("Quitting system . . . .")
            # save and close humidity.db
            time.sleep(2)
            sys.exit()