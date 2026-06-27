from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime

import database as db
from config import ADMIN_ID
from keyboards.admin_kb import admin_menu, elon_yaratish_kb, back_kb
from keyboards.user_kb import elon_kirish_kb, joy_ishlatish_kb

router = Router()

# ─── STATES ──────────────────────────────────────────

class ElonState(StatesGroup):
    matn = State()
    media = State()
    limit = State()
    boshlanish = State()
    tugash = State()
    menga_yozsin = State()

# ─── ADMIN FILTRI ─────────────────────────────────────

def is_admin(user_id):
    return user_id == ADMIN_ID

# ─── E'LON YARATISH ──────────────────────────────────

@router.message(F.text == "📢 E'lon yaratish")
async def elon_yaratish(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.clear()
    await state.update_data(
        matn=None, media_id=None, media_type=None,
        limit_son=0, boshlanish=None, tugash=None, menga_yozsin=0
    )
    await message.answer(
        "📢 <b>Yangi e'lon yaratish</b>\n\n"
        "Quyidagi bosqichlarni bajaring:",
        reply_markup=elon_yaratish_kb(),
        parse_mode="HTML"
    )

# ─── MATN ────────────────────────────────────────────

@router.message(F.text == "✍️ Matn kiritish")
async def matn_kiritish(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.set_state(ElonState.matn)
    await message.answer("✍️ E'lon matnini yuboring:", reply_markup=back_kb())

@router.message(ElonState.matn)
async def matn_qabul(message: Message, state: FSMContext):
    if message.text == "🔙 Ortga":
        await state.clear()
        await message.answer("⚙️ Admin panel", reply_markup=admin_menu())
        return
    await state.update_data(matn=message.text)
    await state.set_state(None)
    await message.answer("✅ Matn saqlandi!", reply_markup=elon_yaratish_kb())

# ─── MEDIA ───────────────────────────────────────────

@router.message(F.text == "🖼️ Rasm/Video qo'shish")
async def media_qoshish(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.set_state(ElonState.media)
    await message.answer("🖼️ Rasm yoki video yuboring:", reply_markup=back_kb())

@router.message(ElonState.media, F.photo)
async def media_rasm(message: Message, state: FSMContext):
    media_id = message.photo[-1].file_id
    await state.update_data(media_id=media_id, media_type="photo")
    await state.set_state(None)
    await message.answer("✅ Rasm saqlandi!", reply_markup=elon_yaratish_kb())

@router.message(ElonState.media, F.video)
async def media_video(message: Message, state: FSMContext):
    media_id = message.video.file_id
    await state.update_data(media_id=media_id, media_type="video")
    await state.set_state(None)
    await message.answer("✅ Video saqlandi!", reply_markup=elon_yaratish_kb())

@router.message(ElonState.media, F.document)
async def media_fayl(message: Message, state: FSMContext):
    media_id = message.document.file_id
    await state.update_data(media_id=media_id, media_type="document")
    await state.set_state(None)
    await message.answer("✅ Fayl saqlandi!", reply_markup=elon_yaratish_kb())

@router.message(ElonState.media)
async def media_xato(message: Message):
    if message.text == "🔙 Ortga":
        return
    await message.answer("❌ Faqat rasm, video yoki fayl yuboring!")

# ─── LIMIT ───────────────────────────────────────────

@router.message(F.text == "🔢 Limit belgilash")
async def limit_belgilash(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.set_state(ElonState.limit)
    await message.answer("🔢 Nechta odam kirishi mumkin? (Raqam yuboring):", reply_markup=back_kb())

@router.message(ElonState.limit)
async def limit_qabul(message: Message, state: FSMContext):
    if message.text == "🔙 Ortga":
        await state.set_state(None)
        await message.answer("📢 E'lon yaratish", reply_markup=elon_yaratish_kb())
        return
    try:
        limit = int(message.text.strip())
        if limit <= 0:
            raise ValueError
        await state.update_data(limit_son=limit)
        await state.set_state(None)
        await message.answer(f"✅ Limit {limit} ta qilib belgilandi!", reply_markup=elon_yaratish_kb())
    except:
        await message.answer("❌ Faqat musbat raqam kiriting!")

# ─── VAQT ────────────────────────────────────────────

@router.message(F.text == "📅 Vaqt belgilash")
async def vaqt_belgilash(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.set_state(ElonState.boshlanish)
    await message.answer(
        "📅 Boshlanish vaqtini kiriting:\n"
        "<i>Format: 27.06.2025 10:00</i>",
        reply_markup=back_kb(),
        parse_mode="HTML"
    )

@router.message(ElonState.boshlanish)
async def boshlanish_qabul(message: Message, state: FSMContext):
    if message.text == "🔙 Ortga":
        await state.set_state(None)
        await message.answer("📢 E'lon yaratish", reply_markup=elon_yaratish_kb())
        return
    try:
        dt = datetime.strptime(message.text.strip(), "%d.%m.%Y %H:%M")
        await state.update_data(boshlanish=dt.strftime("%Y-%m-%d %H:%M:%S"))
        await state.set_state(ElonState.tugash)
        await message.answer(
            "📅 Tugash vaqtini kiriting:\n"
            "<i>Format: 04.07.2025 23:59</i>",
            parse_mode="HTML"
        )
    except:
        await message.answer("❌ Format xato! Misol: 27.06.2025 10:00")

@router.message(ElonState.tugash)
async def tugash_qabul(message: Message, state: FSMContext):
    if message.text == "🔙 Ortga":
        await state.set_state(None)
        await message.answer("📢 E'lon yaratish", reply_markup=elon_yaratish_kb())
        return
    try:
        dt = datetime.strptime(message.text.strip(), "%d.%m.%Y %H:%M")
        await state.update_data(tugash=dt.strftime("%Y-%m-%d %H:%M:%S"))
        await state.set_state(None)
        await message.answer("✅ Vaqt belgilandi!", reply_markup=elon_yaratish_kb())
    except:
        await message.answer("❌ Format xato! Misol: 04.07.2025 23:59")

# ─── MENGA YOZSIN ────────────────────────────────────

@router.message(F.text.in_(["✉️ Menga yozsin: OFF", "✉️ Menga yozsin: ON"]))
async def menga_yozsin_toggle(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    data = await state.get_data()
    joriy = data.get("menga_yozsin", 0)
    yangi = 1 if joriy == 0 else 0
    await state.update_data(menga_yozsin=yangi)

    from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="✍️ Matn kiritish")],
        [KeyboardButton(text="🖼️ Rasm/Video qo'shish")],
        [KeyboardButton(text="🔢 Limit belgilash")],
        [KeyboardButton(text="📅 Vaqt belgilash")],
        [KeyboardButton(text=f"✉️ Menga yozsin: {'ON' if yangi else 'OFF'}")],
        [KeyboardButton(text="👁️ Ko'rinish (preview)")],
        [KeyboardButton(text="✅ Yuborish")],
        [KeyboardButton(text="🔙 Ortga")]
    ], resize_keyboard=True)

    status = "✅ Yoqildi" if yangi else "❌ O'chirildi"
    await message.answer(f"✉️ Menga yozsin: <b>{status}</b>", reply_markup=kb, parse_mode="HTML")

# ─── PREVIEW ─────────────────────────────────────────

@router.message(F.text == "👁️ Ko'rinish (preview)")
async def preview(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    data = await state.get_data()
    matn = data.get("matn") or "❌ Matn kiritilmagan"
    limit = data.get("limit_son", 0)
    boshlanish = data.get("boshlanish") or "Belgilanmagan"
    tugash = data.get("tugash") or "Belgilanmagan"
    menga_yozsin = "✅ Ha" if data.get("menga_yozsin") else "❌ Yo'q"
    media_type = data.get("media_type") or "Yo'q"

    await message.answer(
        f"👁️ <b>E'lon ko'rinishi:</b>\n\n"
        f"📝 Matn: {matn}\n"
        f"🖼️ Media: {media_type}\n"
        f"👥 Limit: {limit} ta\n"
        f"▶️ Boshlanish: {boshlanish}\n"
        f"⏹️ Tugash: {tugash}\n"
        f"✉️ Menga yozsin: {menga_yozsin}",
        parse_mode="HTML"
    )

# ─── YUBORISH ────────────────────────────────────────

@router.message(F.text == "✅ Yuborish")
async def elon_yuborish(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    data = await state.get_data()

    if not data.get("matn"):
        await message.answer("❌ Avval matn kiriting!")
        return
    if not data.get("limit_son"):
        await message.answer("❌ Avval limit belgilang!")
        return

    elon_id = db.add_elon(
        matn=data.get("matn"),
        media_id=data.get("media_id"),
        media_type=data.get("media_type"),
        limit_son=data.get("limit_son"),
        boshlanish=data.get("boshlanish"),
        tugash=data.get("tugash"),
        menga_yozsin=data.get("menga_yozsin", 0)
    )

    await state.clear()
    await message.answer(
        f"✅ <b>E'lon #{elon_id} yaratildi!</b>\n\n"
        f"Endi foydalanuvchilarga ulashishingiz mumkin.",
        reply_markup=admin_menu(),
        parse_mode="HTML"
    )

    # E'lonni foydalanuvchilarga yuborish
    users = db.get_all_users()
    elon = db.get_elon(elon_id)
    muvaffaq = 0
    xato = 0

    from bot import bot
    for user_id in users:
        try:
            await _send_elon(bot, user_id, elon)
            muvaffaq += 1
        except:
            xato += 1

    await message.answer(
        f"📢 E'lon yuborildi!\n"
        f"✅ Muvaffaqiyatli: <b>{muvaffaq}</b>\n"
        f"❌ Xato: <b>{xato}</b>",
        parse_mode="HTML"
    )

async def _send_elon(bot, user_id, elon):
    elon_id = elon[0]
    matn = elon[1]
    media_id = elon[2]
    media_type = elon[3]
    limit_son = elon[4]
    kirganlar = elon[6]

    caption = f"{matn}\n\n👥 {kirganlar}/{limit_son} kishi kirdi"
    kb = elon_kirish_kb(elon_id, None)

    if media_type == "photo":
        await bot.send_photo(user_id, media_id, caption=caption, reply_markup=kb, parse_mode="HTML")
    elif media_type == "video":
        await bot.send_video(user_id, media_id, caption=caption, reply_markup=kb, parse_mode="HTML")
    elif media_type == "document":
        await bot.send_document(user_id, media_id, caption=caption, reply_markup=kb, parse_mode="HTML")
    else:
        await bot.send_message(user_id, caption, reply_markup=kb, parse_mode="HTML")

# ─── E'LONGA KIRISH ──────────────────────────────────

@router.callback_query(F.data.startswith("elon_kir_"))
async def elon_kir(call: CallbackQuery):
    user_id = call.from_user.id
    elon_id = int(call.data.replace("elon_kir_", ""))
    elon = db.get_elon(elon_id)

    if not elon:
        await call.answer("❌ E'lon topilmadi!", show_alert=True)
        return

    if not elon[9]:
        await call.answer("❌ Bu e'lon yopiq!", show_alert=True)
        return

    # Allaqachon kirganmi?
    if db.kirgan_user(elon_id, user_id):
        await call.answer("✅ Siz allaqachon bu e'longa kirgansiz!", show_alert=True)
        return

    limit = elon[4]
    kirganlar = elon[6]
    joylar = db.get_joylar(user_id)

    # Limit to'ldimi?
    if kirganlar >= limit:
        if joylar > 0:
            await call.message.answer(
                f"❌ Kechirasiz, joy tugadi!\n"
                f"Lekin sizda <b>{joylar} ta joy</b> bor.\n"
                f"Joyingizdan ishlatamizmi?",
                reply_markup=joy_ishlatish_kb(elon_id),
                parse_mode="HTML"
            )
        else:
            await call.answer("❌ Kechirasiz, joy tugadi!", show_alert=True)
        return

    # Kirish
    db.add_kirgan(elon_id, user_id)

    # Menga yozsin
    if elon[8]:
        from bot import bot
        user = call.from_user
        await bot.send_message(
            ADMIN_ID,
            f"✅ <b>Yangi kirish!</b>\n\n"
            f"E'lon #{elon_id}\n"
            f"👤 {user.full_name} (@{user.username})\n"
            f"🆔 ID: <code>{user.id}</code>",
            parse_mode="HTML"
        )

    elon_yangi = db.get_elon(elon_id)
    await call.answer(f"✅ Muvaffaqiyatli kirdingiz! {elon_yangi[6]}/{limit}", show_alert=True)

# ─── JOY ISHLATISH ───────────────────────────────────

@router.callback_query(F.data.startswith("joy_ha_"))
async def joy_ha(call: CallbackQuery):
    user_id = call.from_user.id
    elon_id = int(call.data.replace("joy_ha_", ""))

    joylar = db.get_joylar(user_id)
    if joylar <= 0:
        await call.answer("❌ Sizda joy yo'q!", show_alert=True)
        return

    db.minus_joy(user_id, 1)
    db.add_kirgan(elon_id, user_id, joy_ishlatildi=1)

    elon = db.get_elon(elon_id)
    if elon and elon[8]:
        from bot import bot
        user = call.from_user
        await bot.send_message(
            ADMIN_ID,
            f"✅ <b>Joy orqali kirish!</b>\n\n"
            f"E'lon #{elon_id}\n"
            f"👤 {user.full_name} (@{user.username})\n"
            f"🆔 ID: <code>{user.id}</code>",
            parse_mode="HTML"
        )

    await call.message.edit_text("✅ Joyingiz ishlatildi, muvaffaqiyatli kirdingiz!")

@router.callback_query(F.data == "joy_yoq")
async def joy_yoq(call: CallbackQuery):
    await call.message.edit_text(
        "❌ Joy ishlatilmadi.\n"
        "Joy bo'shaganda qaytib urinib ko'ring!"
    )
