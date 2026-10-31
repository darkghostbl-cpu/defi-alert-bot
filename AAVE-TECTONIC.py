import os, requests

TOKEN = os.environ.get("8765870070:AAHEfC6-eIDlfdeO424G_e0KkkpWC0xY2uo")
if not TOKEN:
    TOKEN = input("Colle ton nouveau TOKEN ici: ").strip()

print("\nJ'attends un message... Va sur Telegram et envoie 'Salut' à ton bot Alerte DeFi")
input("Appuie sur Entrée quand c'est fait...")

r = requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates").json()

if not r.get("ok"):
    print("Erreur:", r)
    exit()

if not r["result"]:
    print("Je ne vois aucun message. Envoie bien 'Salut' à ton bot d'abord.")
    exit()

for u in r["result"]:
    msg = u.get("message") or u.get("channel_post") or {}
    chat = msg.get("chat", {})
    print(f"\n>>> CHAT_ID trouvé: {chat.get('id')}  (nom: {chat.get('first_name') or chat.get('title')})")
    print("C'est ça que tu dois mettre dans CHAT_ID")

