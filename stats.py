import sqlite3

conn = sqlite3.connect(".//database//futbols.db")
cursor = conn.cursor()


# TODO: Row numbers everywhere
# Turnira tabula

for row in cursor.execute("SELECT nosaukums, punktu_sk, uzv_sk_pl, zaud_sk_pl, uzv_sk_pp, zaud_sk_pp, guto_vartu_sk, zaud_vartu_sk FROM Komanda ORDER BY punktu_sk DESC"):
    print(row)

print("---------------------------------------------")
# Turnira 10 rezultativakie speletaji
for row in cursor.execute("SELECT vards, uzvards, komanda, speletaja_nr, vartu_skaits, piespelu_skaits FROM Speletajs ORDER BY vartu_skaits DESC, piespelu_skaits DESC LIMIT 10"):
    print(row)

# print("---------------------------------------------")
# for row in cursor.execute("SELECT * FROM Tiesnesis"):
#     print(row)