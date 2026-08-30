import requests
from datetime import datetime

import os 

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

for i in range(len(cryptos)):
    nom = cryptos[i]
    prix_actuel =donnees[nom]["eur"]
    prix_liquidation = prix_liquidations[i]

    marge = calculer_marge(prix_actuel, prix_liquidation)

    if marge < 10:
        print(f"{nom} - DANGER : marge de {marge:.1f}%")
        envoyer_alerte(f"DANGER : {nom} a une marge de {marge:.1f}% avant liquidation !")
    elif marge < 30:
        print(f"{nom} - Attention : marge de {marge:.1f}%")
        envoyer_alerte(f"ATTENTION : {nom} a une marge de {marge:.1f}% avant liquidation")
    else:
        print(f"{nom} - OK : marge confortablede {marge:.1f}%")
       
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
