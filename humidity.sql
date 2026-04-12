-- jake's original prototype code to test the sql conenction, here for now

sqlCursor.execute("""
INSERT INTO log1 (name, time) VALUES (?, ?);
""", (name, time))

sqlConnection.commit()
sqlConnection.close()

conn = sqlite3.connect('humidity.db')
c = conn.cursor()
c.execute("SELECT * FROM log1;")
rows = c.fetchall()
for row in rows:
    print(row) 
