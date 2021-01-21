import sqlite3


conn = sqlite3.connect(".//database//futbols.db")
cursor = conn.cursor()

# Nolasa sql skripta failu, kas sastav tabulu izveides vaicajumus
sql_file = open(".//database//database_model.sql")
sql_as_string = sql_file.read()
cursor.executescript(sql_as_string)
conn.commit()