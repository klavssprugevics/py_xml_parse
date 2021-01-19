import sqlite3
import xml.etree.ElementTree as ET
from os import walk


conn = sqlite3.connect("futbols")
cursor = conn.cursor()

data_origin = ".//data"
file_list = []

# Apstaiga datu direktoriju un apluko kadi file/direktorijas tur atrodas
for (dirpath, dirnames, filenames) in walk(data_origin):

    # Parbauda, vai file atbilst statistikas protokola failam ar .xml paplasinajumu
    for file in filenames:
        if file.startswith("futbols") and file.endswith(".xml"):
            file_list.append(dirpath + "\\" + file)


# Apstrada katru no atrastajiem protokola failiem
for protocol_file in file_list:
    
    print("Parsing file: " + protocol_file)
    
    tree = ET.parse(protocol_file)
    root = tree.getroot()
    
    
    # --- Mainigie, kas raksturo konkreto speli ---
    teams_playing = []
    sastavi_spele = []
    virstiesnesis = -1              # tiesnesa ID
    

    # ---------------------------------------------        
    

    # Nodefinee komandas
    for team in root.iter("Komanda"):
        
        team_name = team.get("Nosaukums")
        teams_playing.append(team_name)
        
        # Ja komanda ar atrasto nosaukumu nav DB, tad taa tiek pievienota.
        cursor.execute("INSERT OR IGNORE INTO Komanda (nosaukums) VALUES (?)", (team_name,))


    # Nodefinee speletajus
    for child in root:

        # Megina panemt "Speletaji" elementu no konkretaa child elementa
        player_list = child.find("Speletaji")

        # Japarbauda, vai "Speletaji" elements eksistee
        if not player_list:
            continue


        for player in player_list:
            
            loma = player.get("Loma")
            vards = player.get("Vards")
            uzvards = player.get("Uzvards")
            nr = player.get("Nr")

            cursor.execute("INSERT OR IGNORE INTO Speletajs (speletaja_nr, vards, uzvards, loma, komanda) VALUES (?, ?, ?, ?, ?)",
                           (nr, vards, uzvards, loma, child.get("Nosaukums")))


    # Nodefinee virstiesnesi
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

    for child in root:

        pamatsastavs_list = child.find("Pamatsastavs")

        if not pamatsastavs_list:
            continue

        # Saraksts ar speletaju numuriem, kas tiks ievietoti sastava
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

            # Palielina katra speletaju spelu skaitu par 1
            cursor.execute("UPDATE Speletajs SET spelu_skaits = spelu_skaits + 1 WHERE speletaja_nr = (?)", (player_nr[i],))

        sastavi_spele.append(ss_count + 1)
        # print("----------------------------")


    # Ievieto DB Speles ierakstu
    speles_datums = root.get("Laiks")
    speles_vieta = root.get("Skatitaji")
    speles_skatitaji = root.get("Vieta")
    print("Komandas:")
    print(teams_playing)
    print("Sastavi:")
    print(sastavi_spele)
    print("virstiesnesis:")
    print(virstiesnesis)
    print("linijtiesnesi:")
    print(linijtiesnesi)

    # Dabu kopejo spelu skaitu db, lai varetu izveidot unikalu id
    game_count = 0
    for row in cursor.execute("SELECT count(*) FROM Spele"):
        game_count = row[0] + 1


    # TODO: Parbaude, ka viena komanda nevar spelet 2x viena diena
    cursor.execute("INSERT INTO Spele (spele_id, datums, vieta, skatitaji, komanda1, sastavs1, komanda2, sastavs2, vt," +
                  " linijtiesnesis1, linijtiesnesis2) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                  (game_count, speles_datums, speles_vieta, speles_skatitaji, teams_playing[0], sastavi_spele[0],
                   teams_playing[1], sastavi_spele[1], virstiesnesis, linijtiesnesi[0], linijtiesnesi[1]))


    def time_to_seconds(time):
        min_sec = time.split(':')
        return int(min_sec[0]) * 60 + int(min_sec[1])

    # Pievieno sodus db
    for child in root:

        sodi_list = child.find("Sodi")

        if not sodi_list:
            continue

        # Dabu kopejo sodu skaitu, lai varetu izveidot unikalu id
        s_count = 0


        for sods in sodi_list:
            for row in cursor.execute("SELECT count(*) FROM Sods"):
                s_count = row[0] + 1

            nr = sods.get("Nr")
            laiks = time_to_seconds(sods.get("Laiks"))

            cursor.execute("INSERT INTO Sods (sods_id, laiks, speletajs, spele) VALUES (?, ?, ?, ?)", (s_count, laiks, nr, game_count))

            # Papildina speletaja sodu skaitu
            cursor.execute("UPDATE Speletajs SET sodu_skaits = sodu_skaits + 1 WHERE speletaja_nr = (?)", (nr,))

    # satures vartu skaitu abam komandam, lai veiktu apkopojumu
    rezultats = [0, 0]
    komanda_counter = 0
    papildlaiks = False

    # Apstrada vartu guvumus
    for child in root:

        varti_list = child.find("Varti")


        if not varti_list:
            continue

        # Dabu kopejo vartu skaitu, lai varetu izveidot unikalu id
        v_count = 0

        # Itere katram vartu guvumam
        for varti in varti_list:
            laiks = varti.get("Laiks")
            sitiens = varti.get("Sitiens")
            guvejs = varti.get("Nr")

            # ja varti guti pec 60:00, tad iestajies papildlaiks
            if time_to_seconds(laiks) > 3600:
                papildlaiks = True

            rezultats[komanda_counter] += 1

            for row in cursor.execute("SELECT count(*) FROM Varti"):
                v_count = row[0] + 1

            piespeles = []
            # Noskaidro piespeles
            for piespele in varti.iter("P"):
                piespeles.append(piespele.get("Nr"))

                # Papildina speletaja piespelu skaitu
                cursor.execute("UPDATE Speletajs SET piespelu_skaits = piespelu_skaits + 1 WHERE speletaja_nr = (?)", (piespele.get("Nr"),))

            # Izmanto query atkariba no piespelu skaita
            print(piespeles)
            if len(piespeles) == 0:
                cursor.execute("INSERT INTO Varti (varti_id, laiks, sitiens, guvejs, spele) VALUES (?, ?, ?, ?, ?)",
                               (v_count, laiks, sitiens, guvejs, game_count))
            elif len(piespeles) == 1:
                cursor.execute("INSERT INTO Varti (varti_id, laiks, sitiens, guvejs, piespele1, spele) VALUES (?, ?, ?, ?, ?, ?)",
                               (v_count, laiks, sitiens, guvejs, piespeles[0], game_count))
            elif len(piespeles) == 2:
                cursor.execute("INSERT INTO Varti (varti_id, laiks, sitiens, guvejs, piespele1, piespele2, spele) VALUES (?, ?, ?, ?, ?, ?, ?)",
                               (v_count, laiks, sitiens, guvejs, piespeles[0], piespeles[1], game_count))
            elif len(piespeles) == 3:
                cursor.execute("INSERT INTO Varti (varti_id, laiks, sitiens, guvejs, piespele1, piespele2, piespele3, spele) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                               (v_count, laiks, sitiens, guvejs, piespeles[0], piespeles[1], piespeles[2], game_count))


            # Papildina speletaja vartu skaitu
            cursor.execute("UPDATE Speletajs SET vartu_skaits = vartu_skaits + 1 WHERE speletaja_nr = (?)", (guvejs,))

        komanda_counter += 1

    # apstrada rezultatus un pieskaita komandas statistiku
    # print("Komandas spele: " + teams_playing[0] + " " + teams_playing[1])
    # print("Rezultats: " + str(rezultats[0]) + ":" + str(rezultats[1]))
    # print("Papildlaiks: " + str(papildlaiks))

    punkti_uzvaretajiem = 5
    punkti_zaudetajiem = 1

    if papildlaiks:
        punkti_uzvaretajiem = 3
        punkti_zaudetajiem = 2

    # Uzvar 1. komanda
    if rezultats[0] > rezultats[1]:
        cursor.execute("UPDATE Komanda SET punktu_sk = punktu_sk + (?) WHERE nosaukums = (?)", (punkti_uzvaretajiem, teams_playing[0]))
        cursor.execute("UPDATE Komanda SET punktu_sk = punktu_sk + (?) WHERE nosaukums = (?)", (punkti_zaudetajiem, teams_playing[1]))

        if papildlaiks:
            cursor.execute("UPDATE Komanda SET uzv_sk_pp = uzv_sk_pp + 1 WHERE nosaukums = (?)", (teams_playing[0],))
            cursor.execute("UPDATE Komanda SET zaud_sk_pp = zaud_sk_pp + 1 WHERE nosaukums = (?)", (teams_playing[1],))
        else:
            cursor.execute("UPDATE Komanda SET uzv_sk_pl = uzv_sk_pl + 1 WHERE nosaukums = (?)", (teams_playing[0],))
            cursor.execute("UPDATE Komanda SET zaud_sk_pl = zaud_sk_pl + 1 WHERE nosaukums = (?)", (teams_playing[1],))

    if rezultats[1] > rezultats[0]:
        cursor.execute("UPDATE Komanda SET punktu_sk = punktu_sk + (?) WHERE nosaukums = (?)", (punkti_uzvaretajiem, teams_playing[1]))
        cursor.execute("UPDATE Komanda SET punktu_sk = punktu_sk + (?) WHERE nosaukums = (?)", (punkti_zaudetajiem, teams_playing[0]))

        if papildlaiks:
            cursor.execute("UPDATE Komanda SET uzv_sk_pp = uzv_sk_pp + 1 WHERE nosaukums = (?)", (teams_playing[1],))
            cursor.execute("UPDATE Komanda SET zaud_sk_pp = zaud_sk_pp + 1 WHERE nosaukums = (?)", (teams_playing[0],))
        else:
            cursor.execute("UPDATE Komanda SET uzv_sk_pl = uzv_sk_pl + 1 WHERE nosaukums = (?)", (teams_playing[1],))
            cursor.execute("UPDATE Komanda SET zaud_sk_pl = zaud_sk_pl + 1 WHERE nosaukums = (?)", (teams_playing[0],))

    # Papildina vartu skaitu
    cursor.execute("UPDATE Komanda SET guto_vartu_sk = guto_vartu_sk + (?) WHERE nosaukums = (?)", (rezultats[0], teams_playing[0]))
    cursor.execute("UPDATE Komanda SET zaud_vartu_sk = zaud_vartu_sk + (?) WHERE nosaukums = (?)", (rezultats[1], teams_playing[0]))

    cursor.execute("UPDATE Komanda SET guto_vartu_sk = guto_vartu_sk + (?) WHERE nosaukums = (?)", (rezultats[1], teams_playing[1]))
    cursor.execute("UPDATE Komanda SET zaud_vartu_sk = zaud_vartu_sk + (?) WHERE nosaukums = (?)", (rezultats[0], teams_playing[1]))


print("Visas komandas:")
for row in cursor.execute('SELECT * FROM Komanda'):
    print(row)

# for row in cursor.execute('SELECT * FROM Varti'):
#     print(row)

print("Visas speles:")
for row in cursor.execute('SELECT * FROM Spele'):
    print(row)

# for row in cursor.execute('SELECT * FROM Speletaju_sastavs'):
#     print(row)


# for row in cursor.execute('SELECT * FROM Speletaji_sastava WHERE sastavs = (?)', (1,)):
#     print(row)

print("Visi tiesnesi:")
for row in cursor.execute('SELECT * FROM Tiesnesis'):
    print(row)

print("Visi speletaji")
for row in cursor.execute('SELECT * FROM Speletajs'):
    print(row)
#
# for row in cursor.execute('SELECT * FROM Sods'):
#     print(row)

# for row in cursor.execute('SELECT * FROM Komanda'):
#     print(row)


conn.commit()

