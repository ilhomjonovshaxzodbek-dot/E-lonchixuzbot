import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

# Daraja limitleri (kunlik harf)
DARAJALAR = {
    "standart": {"harf": 166, "joy": 0, "nom": "🆓 Standart"},
    "flash":    {"harf": 289, "joy": 5, "nom": "⚡ Flash"},
    "pro":      {"harf": 500, "joy": 10, "nom": "👑 Pro"},
}
