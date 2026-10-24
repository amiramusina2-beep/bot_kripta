from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3

phone_router = Router()

# Главное меню покупки телефонов
@phone_router.callback_query(F.data == "buy_phone_menu")
async def show_phones(callback: CallbackQuery):
    conn = sqlite3.connect("bot_data.db")
    cursor = conn.cursor()
    
    # Создаем таблицы на всякий случай, если их еще нет в базе
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS phones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        model TEXT,
        price INTEGER,
        status TEXT DEFAULT 'available',
        owner_id INTEGER DEFAULT NULL
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_phones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        account_id INTEGER,
        model TEXT
    )
    """)
    conn.commit()
    
    # Достаем доступные телефоны из базы
    cursor.execute("SELECT id, model, price FROM phones WHERE status = 'available'")
    phones = cursor.fetchall()
    conn.close()
    
    if not phones:
        await callback.message.edit_text(
            "📱 <b>Магазин смартфонов</b>\n\nВ данный момент все телефоны с сим-картами раскуплены. Загляните позже!",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Назад в меню", callback_data="back_to_main")]
            ])
        )
        return
        
    keyboard = []
    for phone in phones:
        phone_id, model, price = phone
        keyboard.append([InlineKeyboardButton(text=f"📱 {model} — {price} ⭐", callback_data=f"select_phone_{phone_id}")])
        
    keyboard.append([InlineKeyboardButton(text="🔙 Назад в меню", callback_data="back_to_main")])
    
    await callback.message.edit_text(
        "📱 <b>Магазин смартфонов и сим-карт:</b>\nВыберите устройство, в которое хотите установить сим-карту:",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )

# Подтверждение покупки выбранного телефона
@phone_router.callback_query(F.data.startswith("select_phone_"))
async def confirm_phone_purchase(callback: CallbackQuery):
    phone_id = int(callback.data.split("_")[2])
    
    conn = sqlite3.connect("bot_data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT model, price FROM phones WHERE id = ? AND status = 'available'", (phone_id,))
    phone = cursor.fetchone()
    conn.close()
    
    if not phone:
        await callback.answer("❌ Этот телефон уже кто-то купил!", show_alert=True)
        return
        
    model, price = phone
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Подтвердить покупку", callback_data=f"buy_ph_ok_{phone_id}")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="buy_phone_menu")]
    ])
    
    await callback.message.edit_text(
        f"🛒 <b>Подтверждение покупки</b>\n\n"
        f"📱 Устройство: <b>{model}</b>\n"
        f"💵 Стоимость: <code>{price} stars</code>\n\n"
        f"Сим-карта будет автоматически вставлена в устройство после покупки.",
        parse_mode="HTML",
        reply_markup=keyboard
    )

# Обработка покупки, списание баланса и выдача в инвентарь
@phone_router.callback_query(F.data.startswith("buy_ph_ok_"))
async def process_phone_purchase(callback: CallbackQuery):
    phone_id = int(callback.data.split("_")[3])
    user_id = callback.from_user.id
    
    conn = sqlite3.connect("bot_data.db")
    cursor = conn.cursor()
    
    # 1. Получаем ID аккаунта пользователя и его баланс звёзд
    cursor.execute("SELECT id, stars FROM accounts WHERE user_id = ?", (user_id,))
    account = cursor.fetchone()
    
    if not account:
        conn.close()
        await callback.answer("❌ Сначала создайте профиль в боте!", show_alert=True)
        return
        
    account_id, balance = account
    
    # 2. Получаем данные телефона
    cursor.execute("SELECT model, price FROM phones WHERE id = ? AND status = 'available'", (phone_id,))
    phone = cursor.fetchone()
    
    if not phone:
        conn.close()
        await callback.answer("❌ Телефон уже недоступен.", show_alert=True)
        return
        
    model, price = phone
    
    # 3. Проверяем баланс
    if balance < price:
        conn.close()
        await callback.answer("❌ Недостаточно средств на балансе!", show_alert=True)
        return
        
    # 4. Проводим списание и привязку
    cursor.execute("UPDATE accounts SET stars = stars - ? WHERE id = ?", (price, account_id))
    cursor.execute("UPDATE phones SET status = 'sold', owner_id = ? WHERE id = ?\n", (account_id, phone_id))
    cursor.execute("INSERT INTO user_phones (account_id, model) VALUES (?, ?)", (account_id, model))
    
    conn.commit()
    conn.close()
    
    await callback.message.edit_text(
        f"🎉 <b>Поздравляем с покупкой!</b>\n\n"
        f"📱 Устройство: <b>{model}</b> успешно куплено!\n"
        f"📶 Сим-карта активирована и добавлена в ваш инвентарь.",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📱 Мои телефоны", callback_data="my_phones")],
            [InlineKeyboardButton(text="🔙 В главное меню", callback_data="back_to_main")]
        ])
    )

# Раздел просмотра купленных телефонов
@phone_router.callback_query(F.data == "my_phones")
async def show_my_phones(callback: CallbackQuery):
    user_id = callback.from_user.id
    conn = sqlite3.connect("bot_data.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM accounts WHERE user_id = ?", (user_id,))
    account = cursor.fetchone()
    
    if not account:
        conn.close()
        await callback.answer("❌ Профиль не найден", show_alert=True)
        return
        
    account_id = account[0]
    cursor.execute("SELECT model FROM user_phones WHERE account_id = ?", (account_id,))
    phones = cursor.fetchall()
    conn.close()
    
    if not phones:
        text = "📱 У вас пока нет купленных телефонов с сим-картами."
    else:
        text = "📱 <b>Ваши устройства и сим-карты:</b>\n\n"
        for idx, p in enumerate(phones, 1):
            text += f"{idx}. <b>{p[0]}</b>\n"
            
    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 В главное меню", callback_data="back_to_main")]
        ])
    )
