import sqlite3

conn = sqlite3.connect("futbols")
cursor = conn.cursor()


# Turnira tabula

for row in cursor.execute("SELECT nosaukums, punktu_sk, uzv_sk_pl, zaud_sk_pl, uzv_sk_pp, zaud_sk_pp, guto_vartu_sk, zaud_vartu_sk FROM Komanda ORDER BY punktu_sk DESC"):
    print(row)

# Turnira 10 rezultativakie speletaji

# for row in cursor.execute("SELECT vards, uzvards, ")