import sqlite3

conn = sqlite3.connect("futbols")
cursor = conn.cursor()

sql_file = open("model.sql")
sql_as_string = sql_file.read()
cursor.executescript(sql_as_string)

conn.commit()