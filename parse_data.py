import sqlite3
import xml.etree.ElementTree as ET
conn = sqlite3.connect("futbols")
cursor = conn.cursor()

tree = ET.parse(".//XMLFirstRound//futbols0.xml")
root = tree.getroot()

# Komandas, kas paslaik spele
teams_playing = []

# Ievieto DB komandas, kas vel nav pievienotas
for team in root.iter("Komanda"):
    team_name = team.get("Nosaukums")
    teams_playing.append(team_name)
    cursor.execute("INSERT OR IGNORE INTO Komanda (nosaukums) VALUES (?)", (team_name,))


# Ievieto DB komandas speletajus, kuri vel nav pievienoti
for child in root:

    player_list = child.find("Speletaji")

    # Japarbauda, vai nav panemts child, kam neeksiste "Speletaji" child, piem. - "T"
    if not player_list:
        continue

    for player in player_list:
        loma = player.get("Loma")
        vards = player.get("Vards")
        uzvards = player.get("Uzvards")
        nr = player.get("Nr")

        cursor.execute("INSERT OR IGNORE INTO Speletajs (speletaja_nr, vards, uzvards, loma, komanda) VALUES (?, ?, ?, ?, ?)",
                       (nr, vards, uzvards, loma, child.get("Nosaukums")))


# Ievito DB tiesnesus, kuri vel nav pievienoti
for vt in root.iter("VT"):
    vards = vt.get("Vards")
    uzvards = vt.get("Uzvards")

    # Paskatas, vai tads tiesnesis jau eksiste
    t_exists = False
    for row in cursor.execute("SELECT count(*) FROM Tiesnesis WHERE vards = (?) AND uzvards = (?)", (vards, uzvards)):
        if row[0] != 0:
            t_exists = True

    # Papildina tiesnesu spelu skaitu
    if t_exists:
        cursor.execute("UPDATE Tiesnesis SET spelu_skaits = spelu_skaits + 1, vt_skaits = vt_skaits + 1 WHERE vards = (?) AND uzvards = (?)", (vards, uzvards))

    # Ja tiesnesis neeksiste, to pievieno
    if not t_exists:

        # Dabu kopejo tiesnesu skaitu, lai varetu izveidot unikalu id
        t_count = 0
        for row in cursor.execute("SELECT count(*) FROM Tiesnesis"):
            t_count = row[0]

        cursor.execute("INSERT INTO Tiesnesis (tiesnesis_id, vards, uzvards) VALUES (?, ?, ?)", (t_count + 1, vards, uzvards))
    # if len(tiesnesis) == 0:
        # print("no tiesnesis found with this name")
    # for row in ):
    #     print(row)
    # print(vards, uzvards)

# for lt in root.iter("T"):
#     vards = lt.get("Vards")
#     uzvards = lt.get("Uzvards")
#     print(vards, uzvards)


# for child in root:
#
#     linijtiesnesi = child.find("T")
#     virstiesnesis = child.find("VT")
#
#     if not linijtiesnesi and not virstiesnesis:
#         continue
#
#     for lt in linijtiesnesi:
#         vards = lt.get("Vards")
#         uzvards = lt.get("Uzvards")
#
#         print(vards)
#         print(uzvards)
#
#     for vt in virstiesnesis:
#         vards = lt.get("Vards")
#         uzvards = lt.get("Uzvards")
#
#         print(vards)
#         print(uzvards)


for row in cursor.execute('SELECT * FROM Tiesnesis'):
    print(row)
# for row in cursor.execute('SELECT * FROM Speletajs'):
#     print(row)
# for row in cursor.execute('SELECT * FROM Komanda'):
#     print(row)

conn.commit()