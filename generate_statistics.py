# Klavs Sprugevics - ks20064

import sqlite3
import plotly.graph_objects as go
from plotly.subplots import make_subplots

conn = sqlite3.connect(".//database//futbols.db")
cursor = conn.cursor()

# Tabulu izstrades workflow:
# Izveido sarakstus, kas satures vertibas, kas jaraksta katraa kolonnaa
# No db iznem nepieciesamas vertibas un veic kaut kadas manipulacijas, ja nepieciesams
# Izveido subplot, kas tiek pievienots galvenai figure
# Figure tiek displayota un ari saglabata kaa .html fails


# Nodefinee figure
fig = make_subplots(
    rows=4, cols=1,
    vertical_spacing=0.03,
    specs=[[{"type": "table"}],
           [{"type": "table"}],
           [{"type": "table"}],
           [{"type": "table"}]],
    subplot_titles=("<b>Turnīra tabula</b>",
                    "<b>Rezultatīvākie spēlētāji (top 10)</b>",
                    "<b>Spēles ar visvairāk gūtajiem vārtiem</b>",
                    "<b>Pieredzējjušāko tiesnešu saraksts</b>"),
)

fig.update_layout(height=1800)


# Turnira tabula

nosaukumi = []
punktu_sk = []
uzv_sk_pl = []
zaud_sk_pl = []
uzv_sk_pp = []
zaud_sk_pp = []
guto_vartu_sk = []
zaud_vartu_sk = []
vietas = []
counter = 1

for row in cursor.execute("SELECT nosaukums, punktu_sk, uzv_sk_pl, zaud_sk_pl, uzv_sk_pp, zaud_sk_pp, guto_vartu_sk, "
                          "zaud_vartu_sk FROM Komanda ORDER BY punktu_sk DESC"):
    nosaukumi.append("<b>" + row[0] + "</b>")
    punktu_sk.append(row[1])
    uzv_sk_pl.append(row[2])
    zaud_sk_pl.append(row[3])
    uzv_sk_pp.append(row[4])
    zaud_sk_pp.append(row[5])
    guto_vartu_sk.append(row[6])
    zaud_vartu_sk.append(row[7])
    vietas.append(counter)
    counter += 1


# Ievieto atrastas vertibas subplota
fig.add_trace(
    go.Table(
        header=dict(
        values=["Vieta", "Nosaukums", "Punktu skaits", "Uzvarēto spēļu skaits pamatlaikā",
                "Zaudēto spēļu skaits pamatlaikā", "Uzvarēto spēļu skaits papildlaikā",
                "Zaudēto spēļu skaits papildlaikā", "Gūto vārtu skaits", "Zaudēto vārtu skaits"]
        ),
        cells=dict(
            values=[vietas, nosaukumi, punktu_sk, uzv_sk_pl, zaud_sk_pl, uzv_sk_pp, zaud_sk_pp,
                    guto_vartu_sk, zaud_vartu_sk],
        ),
    ),
    row=1, col=1
)


# Turnira 10 rezultativakie speletaji

vardi = []
uzvardi = []
komanda = []
speletaja_nr = []
vartu_skaits = []
piespelu_skaits = []
vietas = []
counter = 1

for row in cursor.execute("SELECT vards, uzvards, komanda, speletaja_nr, vartu_skaits, piespelu_skaits FROM Speletajs "
                          "ORDER BY vartu_skaits DESC, piespelu_skaits DESC LIMIT 10"):
    vardi.append("<b>" + row[0] + "</b>")
    uzvardi.append("<b>" + row[1] + "</b>")
    komanda.append(row[2])
    speletaja_nr.append(row[3])
    vartu_skaits.append(row[4])
    piespelu_skaits.append(row[5])
    vietas.append(counter)
    counter += 1


fig.add_trace(
    go.Table(
        header=dict(
            values=["Vieta", "Vārds", "Uzvārds", "Komanda", "Spēlētāja nr.", "Vārtu skaits", "Piespēļu skaits"]
        ),
        cells=dict(
            values=[vietas, vardi, uzvardi, komanda, speletaja_nr, vartu_skaits, piespelu_skaits],
            height=20
        )
    ),
    row=2, col=1
)


# Speles ar visvairak gutajiem vartiem

datumi = []
vietas = []
komandas = []
rezultats = []
vartu_skaits = []
varti = []
game_list = []
total_goal_list = []
total_player_list = []

# Iegust info par spelem
for row in cursor.execute("SELECT Spele.spele_id, Spele.datums, Spele.vieta, Spele.komanda1, Spele.komanda2,"
                          "Spele.varti1, Spele.varti2, Spele.varti1 + Spele.varti2 AS vartu_skaits"
                          " FROM Spele ORDER BY vartu_skaits DESC, Spele.datums DESC"):

    game_list.append(row)
    datumi.append(row[1])
    vietas.append(row[2])
    komandas.append("<b>" + row[3] + "</b>" + " | " + "<b>" + row[4] + "</b>")
    rezultats.append(str(row[5]) + ":" + str(row[6]))
    vartu_skaits.append(row[7])

# Iegust info par speletajiem spelee un vinu gutajiem vartiem
for game in game_list:

    goal_list = []
    for goal in cursor.execute("SELECT * FROM Varti WHERE spele=(?)", (game[0],)):
        goal_list.append(goal)

    player_list = []
    for goal in goal_list:
        for player in cursor.execute(
                "SELECT speletajs_id, speletaja_nr, vards, uzvards FROM Speletajs WHERE speletajs_id = (?)",
                (goal[3],)):
            player_list.append(player)

    total_goal_list.append(goal_list)
    total_player_list.append(player_list)


for i in range(0, len(game_list)):

    goals_in_game = ""

    for j in range(0, len(total_goal_list[i])):
        goals_in_game += total_goal_list[i][j][1] + " " + total_player_list[i][j][2] + " " + \
                total_player_list[i][j][3] + " (" + str(total_player_list[i][j][1]) + ") " + \
                total_goal_list[i][j][2] + "<br>"

    varti.append(goals_in_game)

fig.add_trace(
    go.Table(
        header=dict(
            values=["Datums", "Vieta", "Komandas", "Rezultāts", "Vārtu skaits", "Vārti"]
        ),
        cells=dict(
            values=[datumi, vietas, komandas, rezultats, vartu_skaits, varti],
        )
    ),
    row=3, col=1
)


# Tiesnesu tabula

tiesnesu_saraksts = []
vardi = []
uzvardi = []
spelu_skaits = []
vt_skaits = []
lt_skaits = []
total_game_list = []


# Iegust tiesnesus
for row in cursor.execute(
        "SELECT tiesnesis_id, vards, uzvards, spelu_skaits, vt_skaits, spelu_skaits - vt_skaits AS linij_skaits "
        "FROM Tiesnesis ORDER BY spelu_skaits DESC"):
    tiesnesu_saraksts.append(row)
    vardi.append("<b>" + row[1] + "</b>")
    uzvardi.append("<b>" + row[2] + "</b>")
    spelu_skaits.append(row[3])
    vt_skaits.append(row[4])
    lt_skaits.append(row[5])


# Iegust speles kuras piedalijas tiesnesis
for tiesnesis in tiesnesu_saraksts:

    tiesn_id = tiesnesis[0]
    game_list = []
    sodu_count_list = []
    for game in cursor.execute("SELECT spele_id, komanda1, komanda2 FROM Spele WHERE vt = (?)", (tiesn_id,)):
        game_list.append(game)

    for game in game_list:
        for sods in cursor.execute("SELECT COUNT(*) FROM Sods WHERE spele = (?)", (game[0],)):
            sodu_count_list.append(sods[0])

    games = ""

    if len(game_list) == 0:
        games = "SPĒĻU NAV"

    for i in range(0, len(game_list)):
        games += "<b>" + game_list[i][1] + "</b>" + " | " + "<b>" + game_list[i][2] + "</b>" + " sodu skaits: " + str(
            sodu_count_list[i]) + "<br>"

    total_game_list.append(games)


fig.add_trace(
    go.Table(
        header=dict(
            values=["Spēļu skaits", "Vārds", "Uzvārds", "Spēles kā virstiesnesis", "Spēles kā līnijtiesnesis",
                    "Spēles kā VT"]
        ),
        cells=dict(
            values=[spelu_skaits, vardi, uzvardi, vt_skaits, lt_skaits, total_game_list],
        )
    ),
    row=4, col=1
)

fig.show()

with open(".//output//statistics.html", 'w') as f:
    f.write(fig.to_html(full_html=False, include_plotlyjs='cdn'))
