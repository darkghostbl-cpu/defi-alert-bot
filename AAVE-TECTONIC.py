# 1. COLLE TON TOKEN ET TON CHAT_ID ICI (entre guillemets)
TOKEN_TELEGRAM = "COLLE_TON_NOUVEAU_TOKEN_ICI"
CHAT_ID = "8765870070:AAHEfC6-eIDlfdeO424G_e0KkkpWC0xY2uo"  # tu l'auras avec le petit fichier

# 2. Le reste c'est ton bot complet, tu touches à rien en dessous
import requests, os, json
from datetime import datetime
from zoneinfo import ZoneInfo

# Si tu as mis les variables d'environnement, elles écrasent ce qui est au dessus
TOKEN_TELEGRAM = os.environ.get("TOKEN_TELEGRAM") or TOKEN_TELEGRAM
CHAT_ID = os.environ.get("CHAT_ID") or CHAT_ID

cryptos = ["crypto-com-chain", "coinbase-wrapped-btc"]
prix_liquidations = [0.037, 20850]

FICHIER_MARGES = "historique_marges.json"
FICHIER_ALERTES = "alertes_envoyees.json"
FICHIER_LOG = "historique.txt"

def calculer_marge(prix_actuel, prix_liquidation):
    return ((prix_actuel - prix_liquidation) / prix_actuel) * 100

def envoyer_alerte(message):
    if not TOKEN_TELEGRAM or not CHAT_ID or "COLLE_" in TOKEN_TELEGRAM:
        print("Mets ton TOKEN et CHAT_ID en haut du fichier")
        return
    url = f"https://api.telegram.org/bot{TOKEN_TELEGRAM}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": message})

def sauvegarder_marge(nom, marge):
    d = {}
    if os.path.exists(FICHIER_MARGES):
        try:
            with open(FICHIER_MARGES, "r") as f: d = json.load(f)
        except: d = {}
    d[nom] = {"date": datetime.now().strftime("%Y-%m-%d"), "marge": marge}
    with open(FICHIER_MARGES, "w") as f: json.dump(d, f, indent=2)

def marge_hier(nom):
    if not os.path.exists(FICHIER_MARGES): return None
    try:
        with open(FICHIER_MARGES, "r") as f: return json.load(f).get(nom, {}).get("marge")
    except: return None

def creneaux_requis(marge_actuelle, nom):
    hier = marge_hier(nom)
    if hier is None: return [16]
    return [9,16,21] if (hier - marge_actuelle) > 10 else [16]

def deja_envoye(nom, h):
    if not os.path.exists(FICHIER_ALERTES): return False
    try:
        with open(FICHIER_ALERTES, "r") as f:
            return f"{nom}_{h}_{datetime.now().strftime('%Y-%m-%d')}" in json.load(f)
    except: return False

def marquer_envoye(nom, h):
    d = {}
    if os.path.exists(FICHIER_ALERTES):
        try:
            with open(FICHIER_ALERTES, "r") as f: d = json.load(f)
        except: d = {}
    d[f"{nom}_{h}_{datetime.now().strftime('%Y-%m-%d')}"] = True
    with open(FICHIER_ALERTES, "w") as f: json.dump(d, f, indent=2)

# --- LANCEMENT ---
now = datetime.now(ZoneInfo("Europe/Paris"))
heure = now.hour

try:
    ids = ",".join(cryptos)
    prix_data = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=eur", timeout=15).json()
except: prix_data = {}

for i, nom in enumerate(cryptos):
    if nom not in prix_data: continue
    prix = prix_data[nom]["eur"]
    marge = calculer_marge(prix, prix_liquidations[i])
    cr = creneaux_requis(marge, nom)
    if heure in cr and not deja_envoye(nom, heure):
        envoyer_alerte(f"{nom}: marge {marge:.1f}% - prix {prix}€")
        marquer_envoye(nom, heure)
    sauvegarder_marge(nom, marge)
    print(f"{nom} - {marge:.1f}%")

# Log avec auto-nettoyage pour ne plus remplir le disque
if os.path.exists(FICHIER_LOG):
    with open(FICHIER_LOG, "r") as f: lines = f.readlines()
    if len(lines) > 500:
        with open(FICHIER_LOG, "w") as f: f.writelines(lines[-200:])

with open(FICHIER_LOG, "a") as f:
    f.write(f"--- {now.strftime('%d/%m/%y %H:%M')} ---\n")
    for i, nom in enumerate(cryptos):
        if nom in prix_data:
            marge = calculer_marge(prix_data[nom]['eur'], prix_liquidations[i])
            f.write(f"{nom} : {marge:.1f}%\n")
