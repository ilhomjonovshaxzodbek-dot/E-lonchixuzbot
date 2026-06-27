from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import database as db
from config import ADMIN_ID, DARAJALAR
from keyboards.user_kb import main_menu, daraja_kb, sovga_tasdiq_kb, joy_ishlatish_kb

router = Router()

# ─── STATES ──────────────────────────────────────────

class SovgaState(StatesGroup):
    to_user = State()
    son = State()

class AdminYozState(StatesGroup):
    yozish = State()

# ─── START ───────────────────────────────────────────

@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.clear()
    user = message.from_user
    args = message.text.split()
    referral_by = None

    if len(args) > 1:
        try:
            referral_by = int(args[1].replace("ref", ""))
            if referral_by == user.id:
                referral_by = None
        except:
            referral_by = None

    existing = db.get_user(user.id)
    db.add_user(user.id, user.username, user.full_name, referral_by)

    if not existing and referral_by:
        try:
            from bot import bot
            await bot.send_message(referral_by, f"🎉 Sizning referral linkingiz orqali <b>{user.full_name}</b> botga kirdi!\n🎟️ +1 joy berildi!", parse_mode="HTML")
        except:
            pass

    await message.answer(
        f"👋 Salom, <b>{user.full_name}</b>!\n\n"
        f"🤖 <b>E'lonchi Bot</b>ga xush kelibsiz!\n"
        f"Quyidagi menyudan foydalaning 👇",
        reply_markup=main_menu(),
        parse_mode="HTML"
    )

# ─── JOYLARIM ────────────────────────────────────────

@router.message(F.text == "🎟️ Joylarim")
async def joylarim(message: Message):
    joylar = db.get_joylar(message.from_user.id)
    await message.answer(f"🎟️ Sizda <b>{joylar} ta joy</b> bor.", parse_mode="HTML")

# ─── REFERRAL ────────────────────────────────────────

@router.message(F.text == "🔗 Referral linkim")
async def referral(message: Message):
    user_id = message.from_user.id
    link = f"https://t.me/elonchixuzbot?start=ref{user_id}"
    await message.answer(
        f"🔗 <b>Sizning referral linkingiz:</b>\n\n"
        f"<code>{link}</code>\n\n"
        f"👥 Har bir do'stingiz uchun <b>1 joy</b> olasiz!",
        parse_mode="HTML"
    )

# ─── SOVGA ───────────────────────────────────────────

@router.message(F.text == "🎁 Sovg'a qilish")
async def sovga_start(message: Message, state: FSMContext):
    joylar = db.get_joylar(message.from_user.id)
    if joylar <= 0:
        await message.answer("❌ Sizda joy yo'q, sovg'a qila olmaysiz!")
        return
    await state.set_state(SovgaState.to_user)
    await message.answer(
        "🎁 Do'stingizning <b>username</b> yoki <b>ID</b> sini yuboring:\n\n"
        "<i>Misol: @username yoki 123456789</i>",
        parse_mode="HTML"
    )

@router.message(SovgaState.to_user)
async def sovga_to(message: Message, state: FSMContext):
    text = message.text.strip()
    to_user = None

    if text.startswith("@"):
        # username bo'yicha qidirish (DB da saqlangan bo'lsa)
        conn = db.get_conn()
        c = conn.cursor()
        c.execute("SELECT user_id FROM users WHERE username = ?", (text[1:],))
        row = c.fetchone()
        conn.close()
        if row:
            to_user = row[0]
    else:
        try:
            to_user = int(text)
        except:
            pass

    if not to_user:
        await message.answer("❌ Foydalanuvchi topilmadi! Qaytadan kiriting:")
        return

    if to_user == message.from_user.id:
        await message.answer("❌ O'zingizga sovg'a qila olmaysiz!")
        return

    await state.update_data(to_id=to_user)
    await state.set_state(SovgaState.son)

    joylar = db.get_joylar(message.from_user.id)
    await message.answer(
        f"🎟️ Nechta joy sovg'a qilasiz?\n"
        f"Sizda <b>{joylar} ta joy</b> bor.\n\n"
        f"Sonni yuboring:",
        parse_mode="HTML"
    )

@router.message(SovgaState.son)
async def sovga_son(message: Message, state: FSMContext):
    try:
        son = int(message.text.strip())
    except:
        await message.answer("❌ Raqam kiriting!")
        return

    joylar = db.get_joylar(message.from_user.id)
    if son <= 0:
        await message.answer("❌ 0 dan katta son kiriting!")
        return
    if son > joylar:
        await message.answer(f"❌ Sizda faqat {joylar} ta joy bor!")
        return

    data = await state.get_data()
    to_id = data["to_id"]

    await state.clear()
    await message.answer(
        f"🎁 <b>{son} ta joy</b> sovg'a qilmoqchisiz.\nTasdiqlaysizmi?",
        reply_markup=sovga_tasdiq_kb(to_id, son),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("sovga_ha_"))
async def sovga_ha(call: CallbackQuery):
    parts = call.data.split("_")
    to_id = int(parts[2])
    son = int(parts[3])

    from_id = call.from_user.id
    joylar = db.get_joylar(from_id)

    if son > joylar:
        await call.answer("❌ Yetarli joy yo'q!", show_alert=True)
        return

    db.sovga_joy(from_id, to_id, son)

    await call.message.edit_text(f"✅ <b>{son} ta joy</b> muvaffaqiyatli sovg'a qilindi!", parse_mode="HTML")

    try:
        from bot import bot
        from_user = call.from_user
        await bot.send_message(to_id, f"🎁 <b>{from_user.full_name}</b> sizga <b>{son} ta joy</b> sovg'a qildi!", parse_mode="HTML")
    except:
        pass

@router.callback_query(F.data == "sovga_yoq")
async def sovga_yoq(call: CallbackQuery):
    await call.message.edit_text("❌ Sovg'a bekor qilindi.")

# ─── BARCHA E'LONLAR ─────────────────────────────────

@router.message(F.text == "📋 Barcha E'lonlar")
async def barcha_elonlar(message: Message):
    elonlar = db.get_all_elonlar()
    if not elonlar:
        await message.answer("📋 Hozircha e'lonlar yo'q.")
        return

    text = "📋 <b>Barcha E'lonlar:</b>\n\n"
    for e in elonlar:
        elon_id = e[0]
        matn = e[1][:30] + "..." if len(e[1]) > 30 else e[1]
        kirganlar = e[6]
        limit = e[4]
        faol = e[9]
        status = "✅ Faol" if faol else "❌ Yopiq"
        text += f"#{elon_id} | {matn}\n👥 {kirganlar}/{limit} | {status}\n\n"

    await message.answer(text, parse_mode="HTML")

# ─── ADMIN BILAN BOG'LANISH ──────────────────────────

@router.message(F.text == "💬 Admin bilan bog'lanish")
async def admin_boglanish(message: Message, state: FSMContext):
    user_id = message.from_user.id
    harf_ishlatilgan, daraja = db.get_kunlik_harf(user_id)
    limit = DARAJALAR[daraja]["harf"]
    qolgan = limit - harf_ishlatilgan
    joylar = db.get_joylar(user_id)

    await state.set_state(AdminYozState.yozish)
    await message.answer(
        f"✅ Siz admin bilan bog'landingiz!\n"
        f"Xabaringizni yozing, admin javob beradi.\n\n"
        f"📊 Darajangiz: <b>{DARAJALAR[daraja]['nom']}</b> | <b>{qolgan}/{limit}</b> harf qoldi",
        reply_markup=daraja_kb(daraja, joylar),
        parse_mode="HTML"
    )

@router.message(AdminYozState.yozish)
async def admin_ga_yoz(message: Message, state: FSMContext):
    user_id = message.from_user.id
    matn = message.text or ""
    harf_son = len(matn)

    harf_ishlatilgan, daraja = db.get_kunlik_harf(user_id)
    limit = DARAJALAR[daraja]["harf"]

    if harf_ishlatilgan + harf_son > limit:
        qolgan = limit - harf_ishlatilgan
        await message.answer(
            f"❌ Kunlik limitingiz tugadi!\n"
            f"Qolgan: <b>{qolgan} ta harf</b>\n"
            f"Darajangizni oshiring yoki ertaga urinib ko'ring.",
            parse_mode="HTML"
        )
        return

    db.add_kunlik_harf(user_id, harf_son)

    user = message.from_user
    from bot import bot
    await bot.send_message(
        ADMIN_ID,
        f"💬 <b>Yangi xabar!</b>\n\n"
        f"👤 {user.full_name} (@{user.username})\n"
        f"🆔 ID: <code>{user.id}</code>\n\n"
        f"📝 {matn}",
        parse_mode="HTML"
    )

    harf_ishlatilgan2, daraja2 = db.get_kunlik_harf(user_id)
    qolgan = DARAJALAR[daraja2]["harf"] - harf_ishlatilgan2

    await message.answer(
        f"✅ Xabaringiz adminga yuborildi!\n"
        f"📊 Qolgan: <b>{qolgan} ta harf</b>",
        parse_mode="HTML"
    )

# ─── DARAJA TANLASH ──────────────────────────────────

@router.callback_query(F.data.startswith("daraja_"))
async def daraja_tanlash(call: CallbackQuery):
    user_id = call.from_user.id
    daraja = call.data.replace("daraja_", "")
    joylar = db.get_joylar(user_id)
    kerakli_joy = DARAJALAR[daraja]["joy"]
    _, joriy_daraja = db.get_kunlik_harf(user_id)

    if daraja == joriy_daraja:
        await call.answer("✅ Bu daraja allaqachon tanlangan!", show_alert=True)
        return

    if joylar < kerakli_joy:
        await call.answer("❌ Sizda yetarli joy yo'q!", show_alert=True)
        return

    db.update_daraja(user_id, daraja, kerakli_joy)
    harf_ishlatilgan, _ = db.get_kunlik_harf(user_id)
    limit = DARAJALAR[daraja]["harf"]
    qolgan = limit - harf_ishlatilgan

    await call.message.edit_text(
        f"✅ Siz admin bilan bog'landingiz!\n"
        f"Xabaringizni yozing, admin javob beradi.\n\n"
        f"📊 Darajangiz: <b>{DARAJALAR[daraja]['nom']}</b> | <b>{qolgan}/{limit}</b> harf qoldi",
        reply_markup=daraja_kb(daraja, db.get_joylar(user_id)),
        parse_mode="HTML"
    )
    await call.answer(f"✅ {DARAJALAR[daraja]['nom']} darajasi tanlandi!")

# ─── YORDAM ──────────────────────────────────────────

@router.message(F.text == "❓ Yordam")
async def yordam(message: Message):
    await message.answer(
        "❓ <b>Bot haqida ma'lumot:</b>\n\n"
        "🎟️ <b>Joylarim</b>\n"
        "— Sizda nechta joy borligini ko'rasiz\n\n"
        "🔗 <b>Referral linkim</b>\n"
        "— Havolangizni do'stlaringizga yuboring,\n"
        "har bir do'stingiz uchun 1 joy olasiz\n\n"
        "🎁 <b>Sovg'a qilish</b>\n"
        "— Joylaringizni do'stingizga sovg'a qiling\n\n"
        "📋 <b>Barcha E'lonlar</b>\n"
        "— Barcha faol va yopiq e'lonlarni ko'rasiz\n\n"
        "💬 <b>Admin bilan bog'lanish</b>\n"
        "— Adminga xabar yuboring (kunlik limit bor)\n"
        "Darajangizni oshirib ko'proq harf yozishingiz mumkin:\n"
        "  🆓 Standart — 166 harf/kun (bepul)\n"
        "  ⚡ Flash — 289 harf/kun (5 joy)\n"
        "  👑 Pro — 500 harf/kun (10 joy)\n\n"
        "❓ <b>Yordam</b>\n"
        "— Bot haqida batafsil ma'lumot",
        parse_mode="HTML"
    )
