import requests, os
from datetime import datetime
from zoneinfo import ZoneInfo

TOKEN_TELEGRAM = os.environ.get("TOKEN_TELEGRAM")
CHAT_ID_SECRET = os.environ.get("CHAT_ID")

cryptos = ["crypto-com-chain", "coinbase-wrapped-btc"]
prix_liquidations = [0.037, 20850]  # prix de liquidation en $ si tu veux tout en $

def calculer_marge(p, liq):
    return ((p - liq) / p) * 100

def trouver_chat_id_auto():
    try:
        r = requests.get(f"https://api.telegram.org/bot{TOKEN_TELEGRAM}/getUpdates", timeout=15).json()
        if r.get("result"):
            chat = r["result"][-1].get("message", {}).get("chat", {})
            return str(chat.get("id"))
    except:
        return None
    return None

def envoyer_alerte(chat_id, msg):
    url = f"https://api.telegram.org/bot{TOKEN_TELEGRAM}/sendMessage"
    requests.post(url, data={"chat_id": chat_id, "text": msg})

if not TOKEN_TELEGRAM:
    print("TOKEN_TELEGRAM manquant")
    exit(1)

chat_id = CHAT_ID_SECRET or trouver_chat_id_auto()
if not chat_id:
    print("Envoie Salut puis relance")
    exit(0)

print(f"CHAT_ID: {chat_id}")

try:
    ids = ",".join(cryptos)
    prix_data = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd", timeout=15).json()
    print(f"Prix USD: {prix_data}")
except Exception as e:
    print(f"Erreur prix: {e}")
    prix_data = {}

for i, nom in enumerate(cryptos):
    if nom not in prix_data: continue
    prix = prix_data[nom]["usd"]
    marge = calculer_marge(prix, prix_liquidations[i])
    print(f"{nom} - {marge:.1f}% - ${prix}")
    envoyer_alerte(chat_id, f"{nom}: marge {marge:.1f}% - prix ${prix}")

print(f"Alerte envoyée à {chat_id}")
