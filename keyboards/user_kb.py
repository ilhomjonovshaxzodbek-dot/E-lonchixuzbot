from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from config import DARAJALAR

# Bosh menyu
def main_menu():
    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🎟️ Joylarim"), KeyboardButton(text="🔗 Referral linkim")],
        [KeyboardButton(text="🎁 Sovg'a qilish"), KeyboardButton(text="📋 Barcha E'lonlar")],
        [KeyboardButton(text="💬 Admin bilan bog'lanish"), KeyboardButton(text="❓ Yordam")]
    ], resize_keyboard=True)
    return kb

# Daraja tugmalari (inline)
def daraja_kb(user_daraja, user_joylar):
    buttons = []
    
    standart_text = "🆓 Standart ✅" if user_daraja == "standart" else "🆓 Standart (Tanlangan)" if user_daraja == "standart" else "🆓 Standart"
    flash_text = "⚡ Flash — 5 joy ✅" if user_daraja == "flash" else "⚡ Flash — 5 joy"
    pro_text = "👑 Pro — 10 joy ✅" if user_daraja == "pro" else "👑 Pro — 10 joy"

    buttons.append([InlineKeyboardButton(
        text="🆓 Standart" + (" ✅" if user_daraja == "standart" else ""),
        callback_data="daraja_standart"
    )])
    buttons.append([InlineKeyboardButton(
        text="⚡ Flash — 5 joy" + (" ✅" if user_daraja == "flash" else ""),
        callback_data="daraja_flash"
    )])
    buttons.append([InlineKeyboardButton(
        text="👑 Pro — 10 joy" + (" ✅" if user_daraja == "pro" else ""),
        callback_data="daraja_pro"
    )])

    return InlineKeyboardMarkup(inline_keyboard=buttons)

# Sovg'a tasdiqlash
def sovga_tasdiq_kb(to_id, son):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Ha", callback_data=f"sovga_ha_{to_id}_{son}"),
            InlineKeyboardButton(text="❌ Yo'q", callback_data="sovga_yoq")
        ]
    ])

# E'lon kirish tugmasi
def elon_kirish_kb(elon_id, kanal_link):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ A'zo bo'lish", callback_data=f"elon_kir_{elon_id}")]
    ])

# Joy ishlatish tugmasi
def joy_ishlatish_kb(elon_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Ha", callback_data=f"joy_ha_{elon_id}"),
            InlineKeyboardButton(text="❌ Yo'q", callback_data="joy_yoq")
        ]
    ])

# Ortga tugmasi
def back_kb():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🔙 Ortga")]
    ], resize_keyboard=True)
