# COLLE TON TOKEN ICI ENTRE LES GUILLEMETS, juste ici en dessous
TOKEN = "8765870070:AAHEfC6-eIDlfdeO424G_e0KkkpWC0xY2uo"

import requests

print("J'attends un message... Va sur Telegram et envoie 'Salut' à ton bot Alerte DeFi")
input("Quand c'est fait, appuie sur Entrée ici...")

r = requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates").json()

if not r.get("ok"):
    print("Erreur token:", r)
    exit()

if not r["result"]:
    print("Je ne vois aucun message. Renvoie Salut à ton bot et relance.")
    exit()

for u in r["result"][-1:]:
    chat = u.get("message", {}).get("chat", {})
    print(f"\n>>> TON CHAT_ID EST: {chat.get('id')}")
    print(f"Copie ce nombre et mets le dans CHAT_ID")
