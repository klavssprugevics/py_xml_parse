import sqlite3
import xml.etree.ElementTree as ET
conn = sqlite3.connect("futbols")
cursor = conn.cursor()

tree = ET.parse(".//XMLFirstRound//futbols0.xml")
root = tree.getroot()

# Komandas, kas paslaik spele
komandas_spele = []

# Ievieto DB komandas, kas vel nav pievienotas
for team in root.iter("Komanda"):
    team_name = team.get("Nosaukums")
    komandas_spele.append(team_name)
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
virstiesnesis = -1
for vt in root.iter("VT"):
    vards = vt.get("Vards")
    uzvards = vt.get("Uzvards")

    # Paskatas, vai tads tiesnesis jau eksiste
    t_exists = False
    for row in cursor.execute("SELECT count(*) FROM Tiesnesis WHERE vards = (?) AND uzvards = (?)", (vards, uzvards)):
        if row[0] != 0:
            t_exists = True

    # Ja tiesnesis neeksiste, to pievieno
    if not t_exists:

        # Dabu kopejo tiesnesu skaitu, lai varetu izveidot unikalu id
        t_count = 0
        for row in cursor.execute("SELECT count(*) FROM Tiesnesis"):
            t_count = row[0]

        cursor.execute("INSERT INTO Tiesnesis (tiesnesis_id, vards, uzvards) VALUES (?, ?, ?)", (t_count + 1, vards, uzvards))

    # Papildina tiesnesu spelu skaitu
    cursor.execute("UPDATE Tiesnesis SET spelu_skaits = spelu_skaits + 1, vt_skaits = vt_skaits + 1 WHERE vards = (?) AND uzvards = (?)", (vards, uzvards))

    # Iegust virstiesnesa id un saglaba to atmina
    for row in cursor.execute("SELECT tiesnesis_id FROM Tiesnesis WHERE vards = (?) AND uzvards = (?)", (vards, uzvards)):
        virstiesnesis = row[0]

# TODO: Refactor ka funkciju, kura norada vai konkreta persona ir virstiesnesis spele
# Process loti lidzigs ar tiesnesiem
linijtiesnesi = []
for lt in root.iter("T"):
    vards = lt.get("Vards")
    uzvards = lt.get("Uzvards")

    # Paskatas, vai tads tiesnesis jau eksiste
    t_exists = False
    for row in cursor.execute("SELECT count(*) FROM Tiesnesis WHERE vards = (?) AND uzvards = (?)", (vards, uzvards)):
        if row[0] != 0:
            t_exists = True

    # Ja tiesnesis neeksiste, to pievieno
    if not t_exists:

        # Dabu kopejo tiesnesu skaitu, lai varetu izveidot unikalu id
        t_count = 0
        for row in cursor.execute("SELECT count(*) FROM Tiesnesis"):
            t_count = row[0]

        cursor.execute("INSERT INTO Tiesnesis (tiesnesis_id, vards, uzvards) VALUES (?, ?, ?)", (t_count + 1, vards, uzvards))

    # Papildina tiesnesu spelu skaitu
    cursor.execute("UPDATE Tiesnesis SET spelu_skaits = spelu_skaits + 1 WHERE vards = (?) AND uzvards = (?)", (vards, uzvards))

    # Iegust linijtiesnesu id un saglaba to atmina
    for row in cursor.execute("SELECT tiesnesis_id FROM Tiesnesis WHERE vards = (?) AND uzvards = (?)", (vards, uzvards)):
        linijtiesnesi.append(row[0])

# Izveido divas speletaju sastavus, kas tiks pievienoti konkretajai spelei
sastavi_spele = []

for child in root:

    pamatsastavs_list = child.find("Pamatsastavs")

    if not pamatsastavs_list:
        continue

    # Saraksts ar speletaju nummuriem, kas tiks ievietoti sastava
    player_nr = []

    # Saraksts, kas atbilst player_nr sarakstam un satur bool vertibu, vai speletajs ir pamatsastava
    main_player = []

    for player in pamatsastavs_list:
        nr = player.get("Nr")
        player_nr.append(nr)
        main_player.append(1)

    mainas_list = child.find("Mainas")

    if not mainas_list:
        continue

    for maina in mainas_list:
        new_nr = maina.get("Nr2")
        player_nr.append(new_nr)
        main_player.append(0)

    # print(player_nr)
    # print(main_player)

    # Dabu kopejo sastavu skaitu db, lai varetu izveidot unikalu id
    ss_count = 0
    for row in cursor.execute("SELECT count(*) FROM Speletaju_sastavs"):
        ss_count = row[0]

    # Izveido speletaju sastava ierakstu DB
    cursor.execute("INSERT INTO Speletaju_sastavs (speletaju_sastavs_id) VALUES (?)", (ss_count + 1,))

    # Savieno visus speletajus ar izveidoto speletaju sastavu
    for i in range(0, len(player_nr)):
        cursor.execute("INSERT INTO Speletaji_sastava (speletajs, sastavs, pamatsastavs) VALUES (?, ?, ?)",
                       (player_nr[i], ss_count + 1, main_player[i]))

    sastavi_spele.append(ss_count + 1)
    # print("----------------------------")


# Ievieto DB Speles ierakstu
speles_datums = root.get("Laiks")
speles_vieta = root.get("Skatitaji")
speles_skatitaji = root.get("Vieta")
# print(komandas_spele)
# print(sastavi_spele)
# print(virstiesnesis)
# print(linijtiesnesi)

# Dabu kopejo spelu skaitu db, lai varetu izveidot unikalu id
game_count = 0
for row in cursor.execute("SELECT count(*) FROM Spele"):
    game_count = row[0] + 1

# TODO: Parbaude, ka viena komanda nevar spelet 2x viena diena
cursor.execute("INSERT INTO Spele (spele_id, datums, vieta, skatitaji, komanda1, sastavs1, komanda2, sastavs2, vt," +
              " linijtiesnesis1, linijtiesnesis2) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
              (game_count, speles_datums, speles_vieta, speles_skatitaji, komandas_spele[0], sastavi_spele[0],
               komandas_spele[1], sastavi_spele[1], virstiesnesis, linijtiesnesi[0], linijtiesnesi[1]))


# for row in cursor.execute('SELECT * FROM Spele'):
#     print(row)

# for row in cursor.execute('SELECT * FROM Speletaju_sastavs'):
#     print(row)


# for row in cursor.execute('SELECT * FROM Speletaji_sastava WHERE sastavs = (?)', (1,)):
#     print(row)

# for row in cursor.execute('SELECT * FROM Tiesnesis'):
#     print(row)
# for row in cursor.execute('SELECT * FROM Speletajs'):
#     print(row)
# for row in cursor.execute('SELECT * FROM Komanda'):
#     print(row)

conn.commit()