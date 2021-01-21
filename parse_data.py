import sqlite3
import xml.etree.ElementTree as ET
from os import walk


# Funkcija, kas parveido MM:SS formatu uz sekundem
def time_to_seconds(time):
    min_sec = time.split(':')
    return int(min_sec[0]) * 60 + int(min_sec[1])


conn = sqlite3.connect(".//database//futbols.db")
cursor = conn.cursor()

data_dir = ".//data"
file_list = []

# Apstaiga datu direktoriju un apluko kadi file/direktorijas tur atrodas
for (dirpath, dirnames, filenames) in walk(data_dir):

    # Parbauda, vai file atbilst statistikas protokola failam ar .xml paplasinajumu
    for file in filenames:
        if file.startswith("futbols") and file.endswith(".xml"):
            file_list.append(dirpath + "\\" + file)


# Apstrada katru no atrastajiem protokola failiem
for file in file_list:

    print("-------------------------------------------------")
    print("Parsing file: " + file)
    
    tree = ET.parse(file)
    root = tree.getroot()



    
    # --- Mainigie, kas raksturo konkreto speli ---

    game_id = 0             # unikalais speles id
    for row in cursor.execute("SELECT count(*) FROM Spele"):
        game_id = row[0] + 1

    game_date = root.get("Laiks")
    game_location = root.get("Skatitaji")
    game_spectator_count = root.get("Vieta")

    # satures vartu skaitu abam komandam, lai veiktu apkopojumu
    result = [0, 0]
    overtime = False

    teams_playing = []
    sastavi_spele = []
    virstiesnesis = -1      # tiesnesa ID
    # ---------------------------------------------


    # Nodefinee komandas
    for team in root.iter("Komanda"):
        
        team_name = team.get("Nosaukums")
        teams_playing.append(team_name)
        
        # Ja komanda ar atrasto nosaukumu nav DB, tad taa tiek pievienota.
        cursor.execute("INSERT OR IGNORE INTO Komanda (nosaukums) VALUES (?)", (team_name,))


    # Parbaude, ka komanda nevar 2x viena diena spelet
    team_already_played_today = False
    for row in cursor.execute("SELECT datums, komanda1, komanda2 FROM Spele"):
        if row[0] == game_date:
            if row[1] in teams_playing or row[2] in teams_playing:
                team_already_played_today = True

    if team_already_played_today:
        continue

    team_counter = 0
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

            player_exists = False

            for row in cursor.execute("SELECT count(*) FROM Speletajs WHERE speletaja_nr = (?) AND komanda = (?)",
                                      (nr, teams_playing[team_counter])):
                if row[0] != 0:
                    player_exists = True

            if player_exists:
                continue

            player_id = 0  # unikalais speles id
            for row in cursor.execute("SELECT count(*) FROM Speletajs"):
                player_id = row[0] + 1

            cursor.execute("INSERT INTO Speletajs (speletajs_id, speletaja_nr, vards, uzvards, loma, komanda) VALUES (?, ?, ?, ?, ?, ?)",
                           (player_id, nr, vards, uzvards, loma, child.get("Nosaukums")))


        team_counter += 1


    # TODO: FUNCTION FOR THIS!
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
            cursor.execute("INSERT INTO Tiesnesis (vards, uzvards) VALUES (?, ?)", (vards, uzvards))

        # Papildina tiesnesu spelu skaitu
        cursor.execute("UPDATE Tiesnesis SET spelu_skaits = spelu_skaits + 1, vt_skaits = vt_skaits + 1 WHERE vards = (?) AND uzvards = (?)", (vards, uzvards))

        # Iegust virstiesnesa id un saglaba to atmina
        for row in cursor.execute("SELECT tiesnesis_id FROM Tiesnesis WHERE vards = (?) AND uzvards = (?)", (vards, uzvards)):
            virstiesnesis = row[0]


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
            cursor.execute("INSERT INTO Tiesnesis (vards, uzvards) VALUES (?, ?)", (vards, uzvards))

        # Papildina tiesnesu spelu skaitu
        cursor.execute("UPDATE Tiesnesis SET spelu_skaits = spelu_skaits + 1 WHERE vards = (?) AND uzvards = (?)", (vards, uzvards))

        # Iegust linijtiesnesu id un saglaba to atmina
        for row in cursor.execute("SELECT tiesnesis_id FROM Tiesnesis WHERE vards = (?) AND uzvards = (?)", (vards, uzvards)):
            linijtiesnesi.append(row[0])


    team_counter = 0
    # Izveido speletaju sastavus
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

        if mainas_list:
            for maina in mainas_list:
                new_nr = maina.get("Nr2")
                player_nr.append(new_nr)
                main_player.append(0)

        # Izveido jaunu sastavu ar unikalu id
        sastavs_id = 0
        for row in cursor.execute("SELECT count(*) FROM Speletaju_sastavs"):
            sastavs_id = row[0] + 1

        cursor.execute("INSERT INTO Speletaju_sastavs (speletaju_sastavs_id) VALUES (?)", (sastavs_id,))

        # Savieno visus speletajus ar izveidoto speletaju sastavu
        for i in range(0, len(player_nr)):
            cursor.execute("INSERT INTO Speletaji_sastava (speletajs, sastavs, pamatsastavs) VALUES (?, ?, ?)",
                           (player_nr[i], sastavs_id, main_player[i]))

            # Palielina katra speletaju spelu skaitu par 1
            cursor.execute("UPDATE Speletajs SET spelu_skaits = spelu_skaits + 1 WHERE speletaja_nr = (?) AND komanda = (?)", (player_nr[i], teams_playing[team_counter]))

        sastavi_spele.append(sastavs_id)
        team_counter += 1


    cursor.execute("INSERT INTO Spele (spele_id, datums, vieta, skatitaji, komanda1, sastavs1, komanda2, sastavs2, vt," +
                  " linijtiesnesis1, linijtiesnesis2) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                  (game_id, game_date, game_location, game_spectator_count, teams_playing[0], sastavi_spele[0],
                   teams_playing[1], sastavi_spele[1], virstiesnesis, linijtiesnesi[0], linijtiesnesi[1]))

    # Nodefinee sodus
    team_counter = 0
    for child in root:

        sodi_list = child.find("Sodi")

        if not sodi_list:
            continue

        # Izveido unikalu id
        sods_id = 0
        for sods in sodi_list:
            for row in cursor.execute("SELECT count(*) FROM Sods"):
                sods_id = row[0] + 1

            nr = sods.get("Nr")
            laiks = time_to_seconds(sods.get("Laiks"))

            cursor.execute("INSERT INTO Sods (sods_id, laiks, speletajs, spele) VALUES (?, ?, ?, ?)", (sods_id, laiks, nr, game_id))

            # Papildina speletaja sodu skaitu
            cursor.execute("UPDATE Speletajs SET sodu_skaits = sodu_skaits + 1 WHERE speletaja_nr = (?) AND komanda = (?)", (nr, teams_playing[team_counter]))

        team_counter += 1


    # Apstrada vartu guvumus
    team_counter = 0
    for child in root:

        goal_list = child.find("Varti")

        if not goal_list:
            team_counter += 1
            continue

        # Dabu kopejo vartu skaitu, lai varetu izveidot unikalu id
        goal_id = 0

        # Itere katram vartu guvumam
        for goal in goal_list:
            laiks = goal.get("Laiks")
            sitiens = goal.get("Sitiens")
            guvejs = goal.get("Nr")

            # ja varti guti pec 60:00, tad iestajies overtime
            if time_to_seconds(laiks) > 3600:
                overtime = True

            result[team_counter] += 1

            for row in cursor.execute("SELECT count(*) FROM Varti"):
                goal_id = row[0] + 1

            piespeles = []

            # Noskaidro piespeles
            for piespele in goal.iter("P"):
                piespeles.append(piespele.get("Nr"))

                # Papildina speletaja piespelu skaitu
                cursor.execute("UPDATE Speletajs SET piespelu_skaits = piespelu_skaits + 1 WHERE speletaja_nr = (?) AND komanda = (?)", (piespele.get("Nr"), teams_playing[team_counter]))

            # Izmanto query atkariba no piespelu skaita
            if len(piespeles) == 0:
                cursor.execute("INSERT INTO Varti (varti_id, laiks, sitiens, guvejs, spele) VALUES (?, ?, ?, ?, ?)",
                               (goal_id, laiks, sitiens, guvejs, game_id))
            elif len(piespeles) == 1:
                cursor.execute("INSERT INTO Varti (varti_id, laiks, sitiens, guvejs, piespele1, spele) VALUES (?, ?, ?, ?, ?, ?)",
                               (goal_id, laiks, sitiens, guvejs, piespeles[0], game_id))
            elif len(piespeles) == 2:
                cursor.execute("INSERT INTO Varti (varti_id, laiks, sitiens, guvejs, piespele1, piespele2, spele) VALUES (?, ?, ?, ?, ?, ?, ?)",
                               (goal_id, laiks, sitiens, guvejs, piespeles[0], piespeles[1], game_id))
            elif len(piespeles) == 3:
                cursor.execute("INSERT INTO Varti (varti_id, laiks, sitiens, guvejs, piespele1, piespele2, piespele3, spele) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                               (goal_id, laiks, sitiens, guvejs, piespeles[0], piespeles[1], piespeles[2], game_id))

            # Papildina speletaja vartu skaitu
            cursor.execute("UPDATE Speletajs SET vartu_skaits = vartu_skaits + 1 WHERE speletaja_nr = (?) AND komanda = (?)", (guvejs, teams_playing[team_counter]))

        team_counter += 1


    # apstrada rezultatus un pieskaita komandas statistiku
    print("Komandas spele: " + teams_playing[0] + " " + teams_playing[1])
    print("result: " + str(result[0]) + ":" + str(result[1]))
    print("overtime: " + str(overtime))


    points_for_winner = 5
    points_for_loser = 1

    if overtime:
        points_for_winner = 3
        points_for_loser = 2


    # Uzvar 1. komanda
    if result[0] > result[1]:
        cursor.execute("UPDATE Komanda SET punktu_sk = punktu_sk + (?) WHERE nosaukums = (?)", (points_for_winner, teams_playing[0]))
        cursor.execute("UPDATE Komanda SET punktu_sk = punktu_sk + (?) WHERE nosaukums = (?)", (points_for_loser, teams_playing[1]))

        if overtime:
            cursor.execute("UPDATE Komanda SET uzv_sk_pp = uzv_sk_pp + 1 WHERE nosaukums = (?)", (teams_playing[0],))
            cursor.execute("UPDATE Komanda SET zaud_sk_pp = zaud_sk_pp + 1 WHERE nosaukums = (?)", (teams_playing[1],))
        else:
            cursor.execute("UPDATE Komanda SET uzv_sk_pl = uzv_sk_pl + 1 WHERE nosaukums = (?)", (teams_playing[0],))
            cursor.execute("UPDATE Komanda SET zaud_sk_pl = zaud_sk_pl + 1 WHERE nosaukums = (?)", (teams_playing[1],))

    else:
        cursor.execute("UPDATE Komanda SET punktu_sk = punktu_sk + (?) WHERE nosaukums = (?)", (points_for_winner, teams_playing[1]))
        cursor.execute("UPDATE Komanda SET punktu_sk = punktu_sk + (?) WHERE nosaukums = (?)", (points_for_loser, teams_playing[0]))

        if overtime:
            cursor.execute("UPDATE Komanda SET uzv_sk_pp = uzv_sk_pp + 1 WHERE nosaukums = (?)", (teams_playing[1],))
            cursor.execute("UPDATE Komanda SET zaud_sk_pp = zaud_sk_pp + 1 WHERE nosaukums = (?)", (teams_playing[0],))
        else:
            cursor.execute("UPDATE Komanda SET uzv_sk_pl = uzv_sk_pl + 1 WHERE nosaukums = (?)", (teams_playing[1],))
            cursor.execute("UPDATE Komanda SET zaud_sk_pl = zaud_sk_pl + 1 WHERE nosaukums = (?)", (teams_playing[0],))


    # Papildina vartu skaitu
    cursor.execute("UPDATE Komanda SET guto_vartu_sk = guto_vartu_sk + (?) WHERE nosaukums = (?)", (result[0], teams_playing[0]))
    cursor.execute("UPDATE Komanda SET zaud_vartu_sk = zaud_vartu_sk + (?) WHERE nosaukums = (?)", (result[1], teams_playing[0]))

    cursor.execute("UPDATE Komanda SET guto_vartu_sk = guto_vartu_sk + (?) WHERE nosaukums = (?)", (result[1], teams_playing[1]))
    cursor.execute("UPDATE Komanda SET zaud_vartu_sk = zaud_vartu_sk + (?) WHERE nosaukums = (?)", (result[0], teams_playing[1]))

    # Ieraksta gala rezultatu speles tabula
    cursor.execute("UPDATE Spele SET varti1 = (?), varti2 = (?), papildlaiks = (?) WHERE spele_id = (?)", (result[0], result[1], int(overtime), game_id))


conn.commit()
