from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import database as db
from config import ADMIN_ID
from keyboards.admin_kb import (admin_menu, elonlar_list_kb, 
                                 elon_boshqar_kb, user_boshqar_kb, 
                                 reklama_tasdiq_kb, back_kb)

router = Router()

# ─── STATES ──────────────────────────────────────────

class ReklamaState(StatesGroup):
    matn = State()

class UserSearchState(StatesGroup):
    search = State()

# ─── ADMIN FILTRI ─────────────────────────────────────

def is_admin(user_id):
    return user_id == ADMIN_ID

# ─── ADMIN PANEL ─────────────────────────────────────

@router.message(Command("admin"))
async def admin_panel(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.clear()
    await message.answer("⚙️ <b>Admin panel</b>", reply_markup=admin_menu(), parse_mode="HTML")

# ─── STATISTIKA ──────────────────────────────────────

@router.message(F.text == "📈 Statistika")
async def statistika(message: Message):
    if not is_admin(message.from_user.id):
        return
    
    conn = db.get_conn()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users")
    total_users = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM users WHERE blocked = 0")
    active_users = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM elonlar")
    total_elonlar = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM elonlar WHERE faol = 1")
    faol_elonlar = c.fetchone()[0]
    conn.close()

    await message.answer(
        f"📈 <b>Statistika:</b>\n\n"
        f"👥 Jami foydalanuvchilar: <b>{total_users}</b>\n"
        f"✅ Faol foydalanuvchilar: <b>{active_users}</b>\n"
        f"📢 Jami e'lonlar: <b>{total_elonlar}</b>\n"
        f"🟢 Faol e'lonlar: <b>{faol_elonlar}</b>",
        parse_mode="HTML"
    )

# ─── E'LONLARIM ──────────────────────────────────────

@router.message(F.text == "📋 E'lonlarim")
async def elonlarim(message: Message):
    if not is_admin(message.from_user.id):
        return
    
    elonlar = db.get_all_elonlar()
    if not elonlar:
        await message.answer("📋 Hozircha e'lonlar yo'q.")
        return

    await message.answer(
        "📋 <b>Barcha e'lonlar:</b>",
        reply_markup=elonlar_list_kb(elonlar),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("elon_boshqar_"))
async def elon_boshqar(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        return
    
    elon_id = int(call.data.replace("elon_boshqar_", ""))
    elon = db.get_elon(elon_id)
    if not elon:
        await call.answer("E'lon topilmadi!", show_alert=True)
        return

    matn = elon[1]
    kirganlar = elon[6]
    limit = elon[4]
    faol = elon[9]
    status = "✅ Faol" if faol else "❌ Yopiq"

    await call.message.edit_text(
        f"📢 <b>E'lon #{elon_id}</b>\n\n"
        f"{matn}\n\n"
        f"👥 Kirganlar: <b>{kirganlar}/{limit}</b>\n"
        f"📊 Holati: <b>{status}</b>",
        reply_markup=elon_boshqar_kb(elon_id, faol),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("elon_off_"))
async def elon_off(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        return
    elon_id = int(call.data.replace("elon_off_", ""))
    db.toggle_elon(elon_id, 0)
    await call.answer("🔴 E'lon o'chirildi!")
    elon = db.get_elon(elon_id)
    await call.message.edit_text(
        f"📢 <b>E'lon #{elon_id}</b>\n\n"
        f"{elon[1]}\n\n"
        f"👥 Kirganlar: <b>{elon[6]}/{elon[4]}</b>\n"
        f"📊 Holati: <b>❌ Yopiq</b>",
        reply_markup=elon_boshqar_kb(elon_id, 0),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("elon_on_"))
async def elon_on(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        return
    elon_id = int(call.data.replace("elon_on_", ""))
    db.toggle_elon(elon_id, 1)
    await call.answer("🟢 E'lon yoqildi!")
    elon = db.get_elon(elon_id)
    await call.message.edit_text(
        f"📢 <b>E'lon #{elon_id}</b>\n\n"
        f"{elon[1]}\n\n"
        f"👥 Kirganlar: <b>{elon[6]}/{elon[4]}</b>\n"
        f"📊 Holati: <b>✅ Faol</b>",
        reply_markup=elon_boshqar_kb(elon_id, 1),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "elonlar_ortga")
async def elonlar_ortga(call: CallbackQuery):
    elonlar = db.get_all_elonlar()
    await call.message.edit_text(
        "📋 <b>Barcha e'lonlar:</b>",
        reply_markup=elonlar_list_kb(elonlar),
        parse_mode="HTML"
    )

# ─── FOYDALANUVCHILAR ────────────────────────────────

@router.message(F.text == "👥 Foydalanuvchilar")
async def foydalanuvchilar(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.set_state(UserSearchState.search)
    await message.answer(
        "👥 Foydalanuvchi ID yoki username kiriting:",
        reply_markup=back_kb()
    )

@router.message(UserSearchState.search)
async def user_search(message: Message, state: FSMContext):
    if message.text == "🔙 Ortga":
        await state.clear()
        await message.answer("⚙️ Admin panel", reply_markup=admin_menu())
        return

    text = message.text.strip()
    user = None

    conn = db.get_conn()
    c = conn.cursor()
    if text.startswith("@"):
        c.execute("SELECT * FROM users WHERE username = ?", (text[1:],))
    else:
        try:
            c.execute("SELECT * FROM users WHERE user_id = ?", (int(text),))
        except:
            pass
    user = c.fetchone()
    conn.close()

    if not user:
        await message.answer("❌ Foydalanuvchi topilmadi!")
        return

    await state.clear()
    blocked = user[9]
    status = "🚫 Bloklangan" if blocked else "✅ Faol"

    await message.answer(
        f"👤 <b>Foydalanuvchi:</b>\n\n"
        f"🆔 ID: <code>{user[1]}</code>\n"
        f"📛 Ism: {user[3]}\n"
        f"👤 Username: @{user[2]}\n"
        f"🎟️ Joylar: {user[5]}\n"
        f"⚡ Daraja: {user[6]}\n"
        f"📊 Holati: {status}",
        reply_markup=user_boshqar_kb(user[1], blocked),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("block_"))
async def block_user(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        return
    user_id = int(call.data.replace("block_", ""))
    db.block_user(user_id)
    await call.answer("🚫 Foydalanuvchi bloklandi!")
    await call.message.edit_reply_markup(reply_markup=user_boshqar_kb(user_id, True))

@router.callback_query(F.data.startswith("unblock_"))
async def unblock_user(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        return
    user_id = int(call.data.replace("unblock_", ""))
    db.unblock_user(user_id)
    await call.answer("✅ Foydalanuvchi blokdan chiqarildi!")
    await call.message.edit_reply_markup(reply_markup=user_boshqar_kb(user_id, False))

# ─── REKLAMA ─────────────────────────────────────────

@router.message(F.text == "📣 Reklama yuborish")
async def reklama_start(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.set_state(ReklamaState.matn)
    await message.answer(
        "📣 Reklama matnini yuboring (rasm/video bilan ham bo'lishi mumkin):",
        reply_markup=back_kb()
    )

@router.message(ReklamaState.matn)
async def reklama_matn(message: Message, state: FSMContext):
    if message.text == "🔙 Ortga":
        await state.clear()
        await message.answer("⚙️ Admin panel", reply_markup=admin_menu())
        return

    await state.update_data(message_id=message.message_id, chat_id=message.chat.id)

    users = db.get_all_users()
    await message.answer(
        f"📣 Reklama {len(users)} ta foydalanuvchiga yuboriladi.\nTasdiqlaysizmi?",
        reply_markup=reklama_tasdiq_kb()
    )

@router.callback_query(F.data == "reklama_yuborish")
async def reklama_yuborish(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id):
        return

    data = await state.get_data()
    await state.clear()

    users = db.get_all_users()
    muvaffaq = 0
    xato = 0

    from bot import bot
    for user_id in users:
        try:
            await bot.copy_message(user_id, data["chat_id"], data["message_id"])
            muvaffaq += 1
        except:
            xato += 1

    await call.message.edit_text(
        f"✅ Reklama yuborildi!\n\n"
        f"✅ Muvaffaqiyatli: <b>{muvaffaq}</b>\n"
        f"❌ Xato: <b>{xato}</b>",
        parse_mode="HTML"
    )

@router.callback_query(F.data == "reklama_bekor")
async def reklama_bekor(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text("❌ Reklama bekor qilindi.")
