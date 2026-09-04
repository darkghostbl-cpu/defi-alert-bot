import requests
from datetime import datetime
import os 
import json
from zoneinfo import ZoneInfo

TOKEN_TELEGRAM = os.environ.get("TOKEN_TELEGRAM")
CHAT_ID = os.environ.get("CHAT_ID")

# Le prix en dessous duquel tu es liquidé sur Tectonic (regarde ta feuille Excel)
prix_liquidation = 0.037

# Fais l'appel à CoinGecko pour le CRO
reponse = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=crypto-com-chain,&vs_currencies=eur")
print(reponse.json())

# Récupère le prix actuel du CRO dans le JSON (clé : "crypto-com-chain")
prix_actuel = reponse.json()["crypto-com-chain"]["eur"]

print(prix_actuel)
marge = ((prix_actuel - prix_liquidation) / prix_actuel) * 100
if marge < 10:
    print(f"DANGER : marge de /{marge:.1f}% avant Liquidation")
elif marge < 30:
    print(f"Attention : marge de {marge:.1f}% avant Liquidation") 
else:
    print(f"OK : marge confortable de {marge:.1f}% avant Liquidation")

import requests

# Liste des cryptos à surveiller (IDs CoinGecKo)
cryptos = ["crypto-com-chain", "coinbase-wrapped-btc"]

 # Prix de Liquidation correspondant à chaque crypto, dans le même ordre
prix_liquidations = [0.037, 20850]  # complète pour bitcoin

# Un seul appel API pour toutes les cryptos d'un coup (regarde coment tu avais fait ca la dernière fois)
reponse = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=crypto-com-chain,coinbase-wrapped-btc&vs_currencies=eur")
donnees = reponse.json()

def calculer_marge(prix_actuel, prix_liquidation):
    marge = ((prix_actuel - prix_liquidation) / prix_actuel) * 100
    return marge
def envoyer_alerte(message):
    url = f"https://api.telegram.org/bot{TOKEN_TELEGRAM}/sendMessage"
    reponse = requests.get(url, params={"chat_id": CHAT_ID, "text": message})
    print("Statut Telegram:", reponse.status_code, reponse.text)

def sauvegarder_marge_aujourdhui(nom, marge):
    donnees = {}
    if os.path.exists("historique_marges.json"):
        with open("historique_marges.json", "r") as fichier:
            donnees = json.load(fichier)

    donnees[nom] = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "marge": marge
    }

    with open("historique_marges.json", "w") as fichier:
        json.dump(donnees, fichier) 
def marge_hier(nom):
    if not os.path.exists("historique_marges.json"):
        return None

    with open("historique_marges.json", "r") as fichier:
        donnees = json.load(fichier)

    if nom not in donnees:
        return None

    return donnees[nom]["marge"]

def creneaux_requis(marge_actuelle, nom):
    hier = marge_hier(nom)

    if hier is None:
        return [16]

    baisse = hier - marge_actuelle

    if baisse > 10:
        return [9, 16, 21]
    else:
        return [16]

def creneau_deja_envoye(nom, heure):
    if not os.path.exists("alertes_envoyees.json"):
        return False

    with open("alertes_envoyees.json", "r") as fichier:
        donnees = json.load(fichier)

    cle = nom + "_" + str(heure) + "_" + datetime.now().strftime("%Y-%m-%d")
    return cle in donnees


def marquer_creneau_envoye(nom, heure):
    donnees = {}
    if os.path.exists("alertes_envoyees.json"):
        with open("alertes_envoyees.json", "r") as fichier:
            donnees = json.load(fichier)

    cle = nom + "_" + str(heure) + "_" + datetime.now().strftime("%Y-%m-%d")
    donnees[cle] = True

    with open("alertes_envoyees.json", "w") as fichier:
        json.dump(donnees, fichier)

maintenant_paris = datetime.now(ZoneInfo("Europe/Paris"))
heure_actuelle = maintenant_paris.hour

for i in range(len(cryptos)):
    nom = cryptos[i]
    prix_actuel =donnees[nom]["eur"]
    prix_liquidation = prix_liquidations[i]

    marge = calculer_marge(prix_actuel, prix_liquidation)
    sauvegarder_marge_aujourdhui(nom, marge)

    if marge < 10:
        print(f"{nom} - DANGER : marge de {marge:.1f}%")
    elif marge < 30:
        print(f"{nom} - Attention : marge de {marge:.1f}%")
    else:
        print(f"{nom} - OK : marge confortablede {marge:.1f}%")
    creneaux = creneaux_requis(marge, nom)

    if heure_actuelle in creneaux and not creneau_deja_envoye(nom, heure_actuelle):
        envoyer_alerte(f"{nom} a une marge de {marge:.1f}% avant liquidation")
        marquer_creneau_envoye(nom, heure_actuelle)
       
reponse = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=crypto-com-chain,coinbase-wrapped-btc&vs_currencies=eur")

donnees = reponse.json()

with open("historique.txt", "a") as fichier:
    date_actuelle = datetime.now().strftime("%d/%m/%y %H:%M")
    fichier.write(f"--- {date_actuelle} ---\n")

    for i in range(len(cryptos)):
        nom = cryptos[i]
        prix_actuel = donnees[nom]["eur"]
        prix_liquidation = prix_liquidations[i]
        marge = calculer_marge(prix_actuel, prix_liquidation)
        fichier.write(f"{nom} : marge de {marge:.1f}%\n")
