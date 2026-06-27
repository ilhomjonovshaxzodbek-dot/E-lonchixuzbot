from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# Admin bosh menyu
def admin_menu():
    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="📢 E'lon yaratish"), KeyboardButton(text="📋 E'lonlarim")],
        [KeyboardButton(text="📣 Reklama yuborish"), KeyboardButton(text="👥 Foydalanuvchilar")],
        [KeyboardButton(text="📈 Statistika"), KeyboardButton(text="⚙️ Sozlamalar")]
    ], resize_keyboard=True)
    return kb

# E'lon yaratish menyusi
def elon_yaratish_kb():
    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="✍️ Matn kiritish")],
        [KeyboardButton(text="🖼️ Rasm/Video qo'shish")],
        [KeyboardButton(text="🔢 Limit belgilash")],
        [KeyboardButton(text="📅 Vaqt belgilash")],
        [KeyboardButton(text="✉️ Menga yozsin: OFF")],
        [KeyboardButton(text="👁️ Ko'rinish (preview)")],
        [KeyboardButton(text="✅ Yuborish")],
        [KeyboardButton(text="🔙 Ortga")]
    ], resize_keyboard=True)
    return kb

# E'lonlar ro'yxati (inline)
def elonlar_list_kb(elonlar):
    buttons = []
    for elon in elonlar:
        elon_id, matn = elon[0], elon[1]
        faol = elon[9]
        status = "✅" if faol else "❌"
        qisqa = matn[:25] + "..." if len(matn) > 25 else matn
        buttons.append([InlineKeyboardButton(
            text=f"{status} #{elon_id} | {qisqa}",
            callback_data=f"elon_boshqar_{elon_id}"
        )])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# E'lon boshqarish (inline)
def elon_boshqar_kb(elon_id, faol):
    toggle_text = "🔴 O'chirish" if faol else "🟢 Yoqish"
    toggle_data = f"elon_off_{elon_id}" if faol else f"elon_on_{elon_id}"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=toggle_text, callback_data=toggle_data)],
        [InlineKeyboardButton(text="🔙 Ortga", callback_data="elonlar_ortga")]
    ])

# Foydalanuvchi boshqarish (inline)
def user_boshqar_kb(user_id, blocked):
    block_text = "🔓 Blokdan chiqarish" if blocked else "🚫 Bloklash"
    block_data = f"unblock_{user_id}" if blocked else f"block_{user_id}"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=block_text, callback_data=block_data)],
        [InlineKeyboardButton(text="🔙 Ortga", callback_data="users_ortga")]
    ])

# Reklama tasdiqlash
def reklama_tasdiq_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Yuborish", callback_data="reklama_yuborish"),
            InlineKeyboardButton(text="❌ Bekor", callback_data="reklama_bekor")
        ]
    ])

# Ortga tugmasi
def back_kb():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🔙 Ortga")]
    ], resize_keyboard=True)
