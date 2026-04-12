# importing libraries
from presentation import userMenu
import time
import datetime
import sqlite3
from processing import humidityMonitor

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
    userMenu()
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