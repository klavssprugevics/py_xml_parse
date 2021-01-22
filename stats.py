import sqlite3
import plotly.graph_objects as go
from plotly.subplots import make_subplots

conn = sqlite3.connect(".//database//futbols.db")
cursor = conn.cursor()


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
for row in cursor.execute("SELECT nosaukums, punktu_sk, uzv_sk_pl, zaud_sk_pl, uzv_sk_pp, zaud_sk_pp, guto_vartu_sk, zaud_vartu_sk FROM Komanda ORDER BY punktu_sk DESC"):
    nosaukumi.append(row[0])
    punktu_sk.append(row[1])
    uzv_sk_pl.append(row[2])
    zaud_sk_pl.append(row[3])
    uzv_sk_pp.append(row[4])
    zaud_sk_pp.append(row[5])
    guto_vartu_sk.append(row[6])
    zaud_vartu_sk.append(row[7])
    vietas.append(counter)
    counter+=1


fig = make_subplots(rows=2, cols=1,
    vertical_spacing=0.00000001,
    specs=[[{"type": "table"}],
           [{"type": "table"}]],
    subplot_titles=("1. Tabula", "2. Tabula"),
    )

fig.update_layout(height=(len(vietas) + 2) * 100 + 200)

fig.add_trace(
    go.Table(
        header=dict(
            values = ["Vieta", "Nosaukums", "Punktu skaits", "Uzvarēto spēļu skaits pamatlaikā",
                      "Zaudēto spēļu skaits pamatlaikā", "Uzvarēto spēļu skaits papildlaikā",
                      "Zaudēto spēļu skaits papildlaikā", "Gūto vārtu skaits", "Zaudēto vārtu skaits"]
        ),
        cells=dict(
            values = [vietas, nosaukumi, punktu_sk, uzv_sk_pl, zaud_sk_pl, uzv_sk_pp, zaud_sk_pp,
                      guto_vartu_sk, zaud_vartu_sk]
        )
    ),
    row=1, col=1

)

vardi = []
uzvardi = []
komanda = []
speletaja_nr = []
vartu_skaits = []
piespelu_skaits = []
vietas= []
counter = 1


# Turnira 10 rezultativakie speletaji
for row in cursor.execute("SELECT vards, uzvards, komanda, speletaja_nr, vartu_skaits, piespelu_skaits FROM Speletajs ORDER BY vartu_skaits DESC, piespelu_skaits DESC LIMIT 10"):
    vardi.append(row[0])
    uzvardi.append(row[1])
    komanda.append(row[2])
    speletaja_nr.append(row[3])
    vartu_skaits.append(row[4])
    piespelu_skaits.append(row[5])
    vietas.append(counter)
    counter+=1


fig.add_trace(
    go.Table(
        header=dict(
            values=["Vieta", "Vārds", "Uzvārds", "Komanda", "Spēlētāja nr.", "Vārtu skaits", "Piespēļu skaits"]
        ),
        cells=dict(
            values=[vietas, vardi, uzvardi, komanda, speletaja_nr, vartu_skaits, piespelu_skaits]
        )
    ),
    row=2, col=1
)


game_list= []
for row in cursor.execute("SELECT Spele.spele_id, Spele.datums, Spele.vieta, Spele.komanda1, Spele.komanda2,"
                          "Spele.varti1, Spele.varti2, Spele.varti1 + Spele.varti2 AS vartu_skaits"
                          " FROM Spele ORDER BY vartu_skaits DESC, Spele.datums DESC"):
    game_list.append(row)
    print(row)

total_goal_list = []
total_player_list = []
for game in game_list:

    goal_list = []
    for goal in cursor.execute("SELECT * FROM Varti WHERE spele=(?)", (game[0],)):
        goal_list.append(goal)

    player_list = []
    for goal in goal_list:
        for player in cursor.execute("SELECT speletajs_id, speletaja_nr, vards, uzvards FROM Speletajs WHERE speletajs_id = (?)", (goal[3],)):
            player_list.append(player)

    total_goal_list.append(goal_list)
    total_player_list.append(player_list)

print(len(game_list))
print(len(total_player_list))
print(len(total_goal_list))



# fig.show()

with open('statistics.html', 'w') as f:
    f.write(fig.to_html(full_html=False, include_plotlyjs='cdn'))
