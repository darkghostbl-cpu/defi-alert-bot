# COLLE JUSTE TON TOKEN ICI, rien d'autre
TOKEN_TELEGRAM = "8765870070:AAHEfC6-eIDlfdeO424G_e0KkkpWC0xY2uo"

import requests, os, json
from datetime import datetime
from zoneinfo import ZoneInfo

TOKEN_TELEGRAM = os.environ.get("TOKEN_TELEGRAM") or TOKEN_TELEGRAM

cryptos = ["crypto-com-chain", "coinbase-wrapped-btc"]
prix_liquidations = [0.037, 20850]

def calculer_marge(prix_actuel, prix_liquidation):
    return ((prix_actuel - prix_liquidation) / prix_actuel) * 100

def trouver_chat_id_auto():
    try:
        r = requests.get(f"https://api.telegram.org/bot{TOKEN_TELEGRAM}/getUpdates", timeout=15).json()
        if r.get("result"):
            # prend le dernier chat qui a parlé au bot
            last = r["result"][-1]
            chat = last.get("message", {}).get("chat", {}) or last.get("channel_post", {}).get("chat", {})
            if chat.get("id"):
                print(f"CHAT_ID trouvé automatiquement: {chat.get('id')}")
                return str(chat.get("id"))
    except Exception as e:
        print(f"Erreur auto chat_id: {e}")
    return None

def envoyer_alerte(chat_id, message):
    url = f"https://api.telegram.org/bot{TOKEN_TELEGRAM}/sendMessage"
    requests.post(url, data={"chat_id": chat_id, "text": message})

# --- trouve le CHAT_ID tout seul ---
CHAT_ID = os.environ.get("CHAT_ID") or trouver_chat_id_auto()

if not CHAT_ID:
    print("Envoie 'Salut' à ton bot Alerte DeFi sur Telegram puis relance ce fichier")
    exit()

# --- bot normal ---
now = datetime.now(ZoneInfo("Europe/Paris"))
try:
    ids = ",".join(cryptos)
    prix_data = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=eur", timeout=15).json()
except:
    prix_data = {}

for i, nom in enumerate(cryptos):
    if nom not in prix_data: continue
    prix = prix_data[nom]["eur"]
    marge = calculer_marge(prix, prix_liquidations[i])
    print(f"{nom} - marge {marge:.1f}% - prix {prix}€")
    envoyer_alerte(CHAT_ID, f"{nom}: marge {marge:.1f}% - prix {prix}€")

print(f"Alerte envoyée à {CHAT_ID}")
