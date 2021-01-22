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




fig1 = go.Figure(
    data=[
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
        )
    ]
)

fig1.update_layout(
    title="1. vaicājums"
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


fig2 = go.Figure(
    data=[
        go.Table(
            header=dict(
                values=["Vieta", "Vārds", "Uzvārds", "Komanda", "Spēlētāja nr.", "Vārtu skaits", "Piespēļu skaits"]
            ),
           cells=dict(
               values=[vietas, vardi, uzvardi, komanda, speletaja_nr, vartu_skaits, piespelu_skaits]
           )
        )
    ]
)

fig2.update_layout(
    title="2. vaicājums",
)
# fig.show()

with open('statistics.html', 'w') as f:
    f.write(fig1.to_html(full_html=False, include_plotlyjs='cdn'))
    f.write(fig2.to_html(full_html=False, include_plotlyjs='cdn'))


# print("---------------------------------------------")
# for row in cursor.execute("SELECT * FROM Tiesnesis"):
#     print(row)