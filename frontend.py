import tkinter as tk #gui
from tkinter import Tk
import sqlite3
import json
import datetime
import threading
import Simulation
from processing import humidityMonitor, zoneComparison
from actuation import actuate

#colour palette
BG_MAIN = "#1e1e2e" #navy blue
BG_PANEL = "#2a2a3e" #lighter navy blue
FG_TEXT = "#cdd6f4" #white blue tint
FG_HEADER = "#89b4fa" #baby blue
FG_ALERT = "#f38ba8" #light pink
FG_OK = "#a6e3a1" #light green
FG_WARN = "#fab387" #light orange

#set window properties
class HumidityApp:
    def __init__(self, root): #initialise window properties
        self.root = root #stores the main window in the class to be called by other methods
        self.root.title("Humidizone Management System")
        self.root.configure(bg=BG_MAIN) #set background colour
        self.root.geometry("700x600") #set window size
        #set states
        self.systemRunning = False
        self.adminLoggedIn = False

        #build UI
        self.buildHeader()
        self.buildReadingsPanel()
        self.buildActuationPanel()
        self.buildButtonPanel()
        
    def buildHeader(self):
        #top section: title & system status
        frame = tk.Frame(self.root, bg=BG_MAIN) #create frame in main window
        frame.pack(fill="x", padx=20, pady=10) #'.pack()' calls the layout manager, 'fill="x"' streches the frame horizontally, sets padding by pixels
        tk.Label(frame, text="HUMIDIZONE MANAGEMENT SYSTEM", #set label
            font=("Helvetica", 16, "bold"), #set font, size, and accent
            bg=BG_MAIN, fg=FG_HEADER).pack() #set colour: background & foreground
        #dynamic status label, off by default
        self.statusLabel = tk.Label(frame, text="System Offline",
            font=("Helvetica", 10),
            bg=BG_MAIN, fg=FG_ALERT)
        self.statusLabel.pack()
        #login button
        self.loginButton = tk.Button(frame, text="Login as admin",
            command=self.adminLogin,
            bg=BG_PANEL, fg=FG_TEXT,
            font=("Helvetica", 9))
        self.loginButton.pack()

    def buildReadingsPanel(self):
        #middle section: live humidity per zone
        frame = tk.LabelFrame(self.root, text="Live Readings",
            bg=BG_PANEL, fg=FG_HEADER,
            font=("Helvetica", 11, "bold"))
        frame.pack(fill="x", padx=20, pady=5)
        self.readingsFrame = frame
        self.readingLabels = {} #stores label references by zoneNum

        #build rows per zone from zone.json
        with open("zones.json", "r") as f:
            data = json.load(f)
        for zone in data ["zones"]:
            zoneNum = zone["zoneNum"]
            zoneName = f"zone{zoneNum}_{zone['zoneName']}"
            row = tk.Frame(frame, bg=BG_PANEL)
            row.pack(fill="x", padx=10, pady=2)
            #zone name labels
            tk.Label(row, text=f"Zone {zoneNum} | {zoneName}",
                width=30, anchor="w",
                bg=BG_PANEL, fg=FG_TEXT,
                font=("Helvetica", 10)).pack(side="left")
            #dynamic humidity level label - updated by updateReadings()
            label = tk.Label(row, text="-- %",
                bg=BG_PANEL, fg=FG_TEXT,
                font=("Helvetica", 10, "bold"))
            label.pack(side="left")
            self.readingLabels[zoneNum] = label
            
    def buildActuationPanel(self):
        #lower middle section: actuator state per zone
        frame = tk.LabelFrame(self.root, text="Actuation Status",
            bg=BG_PANEL, fg=FG_HEADER,
            font=("Helvetica", 11, "bold"))
        frame.pack(fill="x", padx=20, pady=5)
        self.actuationFrame = frame
        self.actuationLabels = {} #stores label references by zoneNum

        #build rows per zone from zone.json
        with open("zones.json", "r") as f:
            data = json.load(f)
        for zone in data["zones"]:
            zoneNum = zone["zoneNum"]
            row = tk.Frame(frame, bg=BG_PANEL)
            row.pack(fill="x", padx=10, pady=2)
            tk.Label(row, text=f"zone {zoneNum}:",
                width=10, anchor="w",
                bg=BG_PANEL, fg=FG_TEXT,
                font=("Helvetica", 10)).pack(side="left")
            #dynamic humidity level label - updated by updateReadings()
            label = tk.Label(row, text="OFFLINE",
                bg=BG_PANEL, fg=FG_ALERT,
                font=("Helvetica", 10, "bold"))
            label.pack(side="left")
            self.actuationLabels[zoneNum] = label #stores references for later updates

    def buildButtonPanel(self):
        #bottom section: control buttons
        frame = tk.Frame(self.root, bg=BG_MAIN)
        frame.pack(fill="x", padx=20, pady=10)
        tk.Button(frame, text="Start System",
            command=self.startSystem, #calls startSystem() on click
            bg=FG_OK, fg=BG_MAIN,
            font=("Helvetica", 10, "bold"),
            width=15).grid(row=0, column=0, padx=5, pady=5)
        tk.Button(frame, text="Stop System",
            command=self.stopSystem, #calls stopSystem() on click
            bg=FG_ALERT, fg=BG_MAIN,
            font=("Helvetica", 10, "bold"),
            width=15).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(frame, text="Quit",
            command=self.root.quit, #closes window on click
            bg=BG_PANEL, fg=FG_TEXT,
            font=("Helvetica", 10),
            width=15).grid(row=0, column=2, padx=5, pady=5)
                
    def startSystem(self): #when user clicks start system
        if not self.systemRunning: #prevents the system starting twice if clicked again
            self.systemRunning = True #updates system flag to running
            self.statusLabel.config(text="System Online", fg=FG_OK) #update status label
            dev_thread = threading.Thread(target=Simulation.run,daemon=True) #creates a background thread that runs 'Simulation.run()', 'daemon=True' stops the thread when window closes
            dev_thread.start() #starts thread
            self.root.after(12000, self.updateReadings) #waits 12 seconds before populating readings giving the simulation enough time to access the database

    def stopSystem(self): #when user clicks stop system
        self.systemRunning = False
        self.statusLabel.config(text="Systems Offline", fg=FG_ALERT)
        #reset all actuation labels to offline
        for label in self.actuationLabels.values():
            label.config(text="OFFLINE", fg=FG_ALERT)
                
    def updateReadings(self): 
        if not self.systemRunning:
            return
        
        #connect to databse
        sqlConnection = sqlite3.connect('humidity.db')
        sqlCursor = sqlConnection.cursor()

        with open("zones.json", "r") as f:
            data = json.load(f)

        #fetch readings from database
        for zone in data["zones"]:
            zoneNum = zone["zoneNum"]
            tableName = f"zone{zoneNum}_{zone['zoneName']}"
            sqlCursor.execute(f"SELECT humidity FROM {tableName} ORDER BY id DESC LIMIT 1")
            row = sqlCursor.fetchone()
            if row:
                humidity = row[0]
                minH = int(zone["minHumidity"])
                maxH = int(zone["maxHumidity"])
                #green if in-range, red if out
                colour = FG_OK if minH <= humidity <= maxH else FG_ALERT
                self.readingLabels[zoneNum].config(text=f"{humidity}%", fg=colour)

        sqlConnection.close()

        #monitoring and actuation logic
        humidityMonitor() #updates zoneComparison
        actuate() #logs actuation and energy to database

        #update actuation status labels from zoneComparison
        for zoneNum, comparison in zoneComparison.items():
            if comparison == "<":
                text, colour = "HUMIDIFIER ON", FG_WARN
            elif comparison == ">":
                text, colour = "DEHUMIDIFIER ON", FG_WARN
            else:
                text, colour = "IDLE", FG_OK
            self.actuationLabels[zoneNum].config(text=text, fg=colour)

        #schedule update in 30 seconds
        self.root.after(30000, self.updateReadings)

    #password auth checker
    def checkPassword(self, entered):
        with open("password.txt", "r") as f:
            password = f.read().strip()
        return entered == password

    def adminLogin(self):
        #popup dialog for admin
        dialog = tk.Toplevel(self.root)
        dialog.title("Admin Login")
        dialog.configure(bg=BG_MAIN)
        dialog.geometry("300x150")
        dialog.resizable(False, False)

        tk.Label(dialog, text="enter admin password",
            bg=BG_MAIN, fg=FG_TEXT,
            font=("Helvetica", 10)).pack(pady=10)
        
        passwordEntry = tk.Entry(dialog, show="*",
            bg=BG_PANEL, fg=FG_TEXT,
            font=("Helvetica", 10))
        passwordEntry.pack(pady=5)

        def attempt():
            if self.checkPassword(passwordEntry.get()):
                self.adminLoggedIn = True
                self.loginButton.config(text="Admin Logged In", fg=FG_OK)
                self.buildAdminPanel()
                dialog.destroy()
            else:
                tk.Label(dialog, text="Incorrect password",
                    bg=BG_MAIN, fg=FG_ALERT,
                    font=("Helvetica", 9)).pack()

        tk.Button(dialog, text="Login",
            command=attempt,
            bg=FG_OK, fg=BG_MAIN,
            font=("Helvetica", 10, "bold"),
            width=10).pack(pady=5)

    def adminLogout(self):
        self.adminLoggedIn = False
        self.loginButton.config(text="Login as Admin", fg=FG_TEXT)
        #remove admin panel from window
        self.adminPanel.destroy()

    def buildAdminPanel(self):
        #only called after successful auth
        self.adminPanel = tk.LabelFrame(self.root, text="Admin Controls",
            bg=BG_PANEL, fg=FG_HEADER,
            font=("Helvetica", 11, "bold"))
        self.adminPanel.pack(fill="x", padx=20, pady=5)
        tk.Button(self.adminPanel, text="Adjust Thresholds",
            command=self.adjustThresholds,
            bg=FG_WARN, fg=BG_MAIN,
            font=("Helvetica", 10, "bold"),
            width=18).grid(row=0, column=0, padx=5, pady=5)
        tk.Button(self.adminPanel, text="Manual Override",
            command=self.manualOverride,
            bg=FG_WARN, fg=BG_MAIN,
            font=("Helvetica", 10, "bold"),
            width=18).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(self.adminPanel, text="Logout",
            command=self.adminLogout,
            bg=BG_PANEL, fg=FG_TEXT,
            font=("Helvetica", 10),
            width=10).grid(row=0, column=2, padx=5, pady=5)
    
    def adjustThresholds(self):
        dialog = tk.Toplevel(self.root) #pop-up menu as child
        dialog.title("Adjust Thresholds")
        dialog.configure(bg=BG_MAIN)
        dialog.geometry("500x300")
        dialog.resizable(False, False) #non-sizable

        with open("zones.json", "r") as f:
            data = json.load(f)

        entries = {}  #stores entries by zoneNum

        #header row
        tk.Label(dialog, text="Zone", width=20, anchor="w",
            bg=BG_MAIN, fg=FG_HEADER,
            font=("Helvetica", 10, "bold")).grid(row=0, column=0, padx=10, pady=5)
        tk.Label(dialog, text="Min %", width=10,
            bg=BG_MAIN, fg=FG_HEADER,
            font=("Helvetica", 10, "bold")).grid(row=0, column=1, padx=5)
        tk.Label(dialog, text="Max %", width=10,
            bg=BG_MAIN, fg=FG_HEADER,
            font=("Helvetica", 10, "bold")).grid(row=0, column=2, padx=5)

        #build a row per zone with current values
        for i, zone in enumerate(data["zones"]):
            zoneNum = zone["zoneNum"]
            zoneName = f"zone{zoneNum}_{zone['zoneName']}"
            tk.Label(dialog, text=zoneName, width=20, anchor="w",
                bg=BG_MAIN, fg=FG_TEXT,
                font=("Helvetica", 10)).grid(row=i+1, column=0, padx=10, pady=3)

            minEntry = tk.Entry(dialog, width=10,
                bg=BG_PANEL, fg=FG_TEXT,
                font=("Helvetica", 10))
            minEntry.insert(0, zone["minHumidity"])
            minEntry.grid(row=i+1, column=1, padx=5)

            maxEntry = tk.Entry(dialog, width=10,
                bg=BG_PANEL, fg=FG_TEXT,
                font=("Helvetica", 10))
            maxEntry.insert(0, zone["maxHumidity"])
            maxEntry.grid(row=i+1, column=2, padx=5)

            entries[zoneNum] = (minEntry, maxEntry)

        #feedback label for validation errors
        feedbackLabel = tk.Label(dialog, text="",
            bg=BG_MAIN, fg=FG_ALERT,
            font=("Helvetica", 9))
        feedbackLabel.grid(row=len(data["zones"])+1, column=0, columnspan=3, pady=5)

        def save():
            #update sql with new zones
            with open("zones.json", "r") as f:
                data = json.load(f)

            sqlConnection = sqlite3.connect('humidity.db')
            sqlCursor = sqlConnection.cursor()
            sqlCursor.execute("""
            CREATE TABLE IF NOT EXISTS logAdjust (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                zoneNum TEXT,
                previousMin REAL,
                newMin REAL,
                previousMax REAL,
                newMax REAL,
                timestamp TEXT
            )""")

            for zone in data["zones"]:
                zoneNum = zone["zoneNum"]
                minVal = entries[zoneNum][0].get()
                maxVal = entries[zoneNum][1].get()

                #validate inputs
                if not minVal.isdigit() or not maxVal.isdigit():
                    feedbackLabel.config(text=f"Zone {zoneNum}: values must be numbers")
                    sqlConnection.close()
                    return
                if int(minVal) >= int(maxVal):
                    feedbackLabel.config(text=f"Zone {zoneNum}: min must be less than max")
                    sqlConnection.close()
                    return
                if int(minVal) < 0 or int(maxVal) > 100:
                    feedbackLabel.config(text=f"Zone {zoneNum}: values must be between 0-100")
                    sqlConnection.close()
                    return

                #log previous and new values
                sqlCursor.execute("""
                INSERT INTO logAdjust (zoneNum, previousMin, newMin, previousMax, newMax, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
                """, (zoneNum, zone["minHumidity"], minVal,
                    zone["maxHumidity"], maxVal,
                    datetime.datetime.now().isoformat()))

                #update values
                zone["minHumidity"] = int(minVal)
                zone["maxHumidity"] = int(maxVal)

            with open("zones.json", "w") as f:
                json.dump(data, f, indent=4)

            sqlConnection.commit()
            sqlConnection.close()
            dialog.destroy()

        tk.Button(dialog, text="Save",
            command=save,
            bg=FG_OK, fg=BG_MAIN,
            font=("Helvetica", 10, "bold"),
            width=10).grid(row=len(data["zones"])+2, column=0, columnspan=3, pady=10)

    def manualOverride(self):
        pass

def main():
    root = tk.Tk() #create window
    app = HumidityApp(root) #initialise app
    root.mainloop() #start event loop
    
if __name__ == "__main__":
    main()
            