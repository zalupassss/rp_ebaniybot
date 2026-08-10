import os
import random
import threading
import time
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask

# 🔑 Токен бота
TOKEN = "8892392566:AAE0rSE7QW21zfgZsKhIpf9NrU4OjxR52HY"
bot = telebot.TeleBot(TOKEN)

# Веб-сервер для хостинга (Render)
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is active!"

# 📚 База стандартных РП-команд
# 📚 База стандартных РП-команд
RP_COMMANDS = {
    "поцеловать": {
        "aliases": ["поцеловать", "/kiss", "!поцеловать", "поцелуй"],
        "target_text": "💋 <b>{sender}</b> целует <b>{target}</b>!",
        "solo_text": "💋 <b>{sender}</b> целует воздух... Кого-то явно не хватает!",
        "gifs": ["https://media1.tenor.com/m/GAr1rMm39pcAAAAC/anime-hug.gif"],
    },
    "обнять": {
        "aliases": ["обнять", "/hug", "!обнять"],
        "target_text": "🫂 <b>{sender}</b> крепко-крепко обнимает <b>{target}</b>!",
        "solo_text": "🤗 <b>{sender}</b> обнимает весь чат!",
        "gifs": ["https://media1.tenor.com/m/I1v_9vYjxyEAAAAC/hibike-euphonium.gif"],
    },
    "погладить": {
        "aliases": ["погладить", "/pat", "!погладить"],
        "target_text": "🫳 <b>{sender}</b> нежно гладит <b>{target}</b> по голове!",
        "solo_text": "🫳 <b>{sender}</b> гладит сам себя...",
        "gifs": ["https://media1.tenor.com/m/PkWttKcH1xMAAAAC/kobayashi-dragon.gif"],
    },
    "укусить": {
        "aliases": ["укусить", "/bite", "!укусить", "куснуть"],
        "target_text": "🦷 <b>{sender}</b> делает аккуратный «кусь» <b>{target}</b>!",
        "solo_text": "😬 <b>{sender}</b> делает «кусь» воздуха!",
        "gifs": ["https://media1.tenor.com/m/5mVQ3ffWUTgAAAAC/anime-bite.gif"],
    },
    "покормить": {
        "aliases": ["покормить", "/feed", "!покормить", "накормить"],
        "target_text": "🍲 <b>{sender}</b> вкусно кормит <b>{target}</b>! Теперь кто-то сыт и доволен 😊",
        "solo_text": "🍲 <b>{sender}</b> вкусно кушает! Приятного аппетита 😋",
        "gifs": ["https://media1.tenor.com/m/y_xVq9Ea-YUAAAAC/anime-acchi-kocchi.gif"],
    },
    "оставить засос": {
        "aliases": ["оставить засос", "засос", "!засос"],
        "target_text": "💋 <b>{sender}</b> оставляет страстный засос на шее <b>{target}</b>!",
        "solo_text": "💋 <b>{sender}</b> пытается оставить засос... но на ком?",
        "gifs": ["https://media1.tenor.com/m/5FOgNEcoaYMAAAAC/neck-kisses.gif"],
    },
    "флиртовать": {
        "aliases": ["флиртовать", "флирт", "/flirt", "!флирт"],
        "target_text": "😏 <b>{sender}</b> игриво флиртует с <b>{target}</b>~",
        "solo_text": "😏 <b>{sender}</b> тренирует навыки флирта перед зеркалом!",
        "gifs": ["https://media1.tenor.com/m/TlFyVb6dRqkAAAAC/anime-horusultra.gif"],
    
    "трахнуть": {
        "aliases": ["выебать", "/sex", "!трахнуть"],
        "target_text": "🔥 <b>{sender}</b> нежно трахнул <b>{target}</b>!",
        "solo_text": "🔥 <b>{sender}</b> но член не встал...",
        "gifs": ["https://media.tenor.com/SiL8iSajNNQAAAAi/hi.gif"],
    },
}

# 🛠 Базы данных в памяти
CHAT_CUSTOM_RP = {}        # {chat_id: {command_name: data_dict}}
USER_ADDING_STATE = {}     # {user_id: chat_id}
USERS_ECONOMY = {}         # {user_id: data_dict}

SHOP_ITEMS = {
    "ears": {"name": "🐾 Кошачьи ушки", "price": 100, "desc": "Эффект 'Милота': мурр..~ и x3 некокойна."},
    "ramen": {"name": "🍜 Рамен", "price": 50, "desc": "Эффект 'Даттебаё жгучесть': пассивный фарм на 1 час."},
    "rose": {"name": "🌹 Алая роза", "price": 150, "desc": "Эффект 'Романтика': романтичный префикс."},
    "crown": {"name": "👑 Корона", "price": 500, "desc": "Эффект 'Император': префикс 'Господин,'."}
}

def get_user_data(user_id):
    if user_id not in USERS_ECONOMY:
        USERS_ECONOMY[user_id] = {
            "coins": 100,
            "inventory": [],        # купленные товары
            "active_effects": [],   # включенные эффекты
            "purchase_cooldowns": {}, # {item_key: timestamp последнего приобретения}
            "ramen_expires_at": 0,  # таймер окончания рамена
            "last_passive_check": time.time(),
            "stats": {"hugs": 0, "kisses": 0, "actions": 0},
            "last_daily": 0
        }
    return USERS_ECONOMY[user_id]

# Расчет пассивного дохода от рамена при любом обращении пользователя
def update_passive_coins(u_data):
    now = time.time()
    # Проверяем не истек ли рамен
    if u_data["ramen_expires_at"] > now:
        elapsed = now - u_data["last_passive_check"]
        # 1 некокойн каждые 30 секунд
        earned = int(elapsed // 30)
        if earned > 0:
            u_data["coins"] += earned
            u_data["last_passive_check"] += earned * 30
    else:
        u_data["last_passive_check"] = now

# ==========================================
# ТЕКСТОВЫЕ КОМАНДЫ И ТРИГГЕРЫ
# ==========================================

@bot.message_handler(func=lambda m: m.text and m.text.lower().strip() in ["баланс", "монеты", "коинс"])
def show_balance(message):
    u_data = get_user_data(message.from_user.id)
    update_passive_coins(u_data)
    bot.send_message(
        message.chat.id,
        f"🪙 Баланс пользователя **{message.from_user.first_name}**: `{u_data['coins']} некокойнов`",
        parse_mode="Markdown",
        reply_to_message_id=message.message_id
    )

@bot.message_handler(func=lambda m: m.text and m.text.lower().strip() == "профиль")
def show_profile(message):
    user = message.from_user
    u_data = get_user_data(user.id)
    update_passive_coins(u_data)
    
    inv = ", ".join([SHOP_ITEMS[item]["name"] for item in u_data["inventory"]]) or "Пусто"
    
    # Сборка текста профиля
    text = (
        f"👤 **Профиль: {user.first_name}**\n\n"
        f"🪙 Баланс: `{u_data['coins']} некокойнов`\n"
        f"🎒 Инвентарь: {inv}\n"
    )
    
    # Статус рамена
    now = time.time()
    if u_data["ramen_expires_at"] > now:
        rem_min = int((u_data["ramen_expires_at"] - now) // 60)
        text += f"🍜 Рамен активен еще: `{rem_min} мин.`\n"
        
    text += (
        f"\n📊 Статистика РП:\n"
        f" • Всего действий: `{u_data['stats']['actions']}`\n"
        f" • Объятий: `{u_data['stats']['hugs']}`\n"
        f" • Поцелуев: `{u_data['stats']['kisses']}`\n\n"
        "🛠 **Управление эффектами:**\nнажимай на кнопки ниже, чтобы включить или выключить их:"
    )
    
    # Создаем инлайн-кнопки для каждого предмета из инвентаря
    markup = InlineKeyboardMarkup(row_width=1)
    for item_key in u_data["inventory"]:
        item_name = SHOP_ITEMS[item_key]["name"]
        is_active = item_key in u_data["active_effects"]
        status_icon = "🟢 ВКЛ" if is_active else "🔴 ВЫКЛ"
        markup.add(InlineKeyboardButton(f"{item_name} [{status_icon}]", callback_data=f"toggle_{item_key}"))
        
    if not u_data["inventory"]:
        markup.add(InlineKeyboardButton("🛍 В магазин", callback_data="goto_shop"))

    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=markup, reply_to_message_id=message.message_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("toggle_"))
def toggle_effect(call):
    user_id = call.from_user.id
    item_key = call.data.replace("toggle_", "", 1)
    u_data = get_user_data(user_id)
    
    if item_key not in u_data["inventory"]:
        bot.answer_callback_query(call.id, "У тебя нет этого предмета!", show_alert=True)
        return
        
    if item_key in u_data["active_effects"]:
        u_data["active_effects"].remove(item_key)
        bot.answer_callback_query(call.id, "Эффект выключен!")
    else:
        u_data["active_effects"].append(item_key)
        bot.answer_callback_query(call.id, "Эффект успешно активирован!")
        
    # Обновляем профиль с новыми кнопками
    # Вызываем логику генерации текста профиля заново через редактирование сообщения
    try:
        show_profile_edited(call.message, user_id)
    except:
        pass

def show_profile_edited(message, user_id):
    user = bot.get_chat(user_id) # или берем из message
    u_data = get_user_data(user_id)
    inv = ", ".join([SHOP_ITEMS[item]["name"] for item in u_data["inventory"]]) or "Пусто"
    
    text = (
        f"👤 **Профиль**\n\n"
        f"🪙 Баланс: `{u_data['coins']} некокойнов`\n"
        f"🎒 Инвентарь: {inv}\n"
    )
    now = time.time()
    if u_data["ramen_expires_at"] > now:
        rem_min = int((u_data["ramen_expires_at"] - now) // 60)
        text += f"🍜 Рамен активен еще: `{rem_min} мин.`\n"
        
    text += "\n🛠 **Управление эффектами:**"
    
    markup = InlineKeyboardMarkup(row_width=1)
    for item_key in u_data["inventory"]:
        item_name = SHOP_ITEMS[item_key]["name"]
        is_active = item_key in u_data["active_effects"]
        status_icon = "🟢 ВКЛ" if is_active else "🔴 ВЫКЛ"
        markup.add(InlineKeyboardButton(f"{item_name} [{status_icon}]", callback_data=f"toggle_{item_key}"))
        
    bot.edit_message_text(text, message.chat.id, message.message_id, parse_mode="Markdown", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text and m.text.lower().strip() == "магазин")
def show_shop(message):
    u_data = get_user_data(message.from_user.id)
    markup = InlineKeyboardMarkup(row_width=1)
    for key, item in SHOP_ITEMS.items():
        markup.add(InlineKeyboardButton(f"{item['name']} — {item['price']} 🪙", callback_data=f"buy_{key}"))
    
    bot.send_message(
        message.chat.id,
        "🛍 **Неко-Магазин товаров**\n\n(Купить каждый товар можно 1 раз в сутки):\nВыбирай позицию:",
        reply_markup=markup,
        parse_mode="Markdown"
    )

@bot.callback_query_handler(func=lambda call: call.data == "goto_shop")
def callback_goto_shop(call):
    show_shop(call.message)

@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
def buy_item(call):
    user_id = call.from_user.id
    item_key = call.data.replace("buy_", "", 1)
    u_data = get_user_data(user_id)
    
    if item_key not in SHOP_ITEMS:
        bot.answer_callback_query(call.id, "Товар не найден!")
        return
        
    item = SHOP_ITEMS[item_key]
    
    # Проверка кулдауна на покупку (1 раз в сутки / 86400 секунд)
    now = time.time()
    last_buy = u_data["purchase_cooldowns"].get(item_key, 0)
    if now - last_buy < 86400:
        hours_left = int((86400 - (now - last_buy)) // 3600)
        bot.answer_callback_query(call.id, f"Купить этот товар можно будет через {hours_left} ч. (кулдаун 1 день)", show_alert=True)
        return
        
    if u_data["coins"] < item["price"]:
        bot.answer_callback_query(call.id, f"Не хватает некокойнов! Нужно {item['price']} 🪙", show_alert=True)
        return
        
    u_data["coins"] -= item["price"]
    u_data["purchase_cooldowns"][item_key] = now
    
    # Обработка добавления в инвентарь или активации рамена
    if item_key == "ramen":
        # Рамен активирует таймер эффекта на 1 час
        u_data["ramen_expires_at"] = now + 3600
        if "ramen" not in u_data["inventory"]:
            u_data["inventory"].append("ramen")
        if "ramen" not in u_data["active_effects"]:
            u_data["active_effects"].append("ramen")
        bot.answer_callback_query(call.id, "🍜 Ты съел Рамен! Эффект 'Даттебаё' активирован на 1 час!", show_alert=True)
    else:
        if item_key not in u_data["inventory"]:
            u_data["inventory"].append(item_key)
        bot.answer_callback_query(call.id, f"Успешная покупка: {item['name']}!", show_alert=True)
        
    bot.edit_message_text(
        f"✅ Вы успешно приобрели **{item['name']}**!\nПроверить инвентарь и включить эффект можно написав слово `профиль`.",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda m: m.text and m.text.lower().strip() in ["награда", "/daily"])
def daily_reward(message):
    user_id = message.from_user.id
    u_data = get_user_data(user_id)
    update_passive_coins(u_data)
    now = time.time()
    
    if now - u_data["last_daily"] < 86400:
        left = int((86400 - (now - u_data["last_daily"])) // 3600)
        bot.send_message(message.chat.id, f"⏳ Ты уже забирал награду. Следующая будет доступна через {left} ч.", reply_to_message_id=message.message_id)
        return
        
    u_data["last_daily"] = now
    reward = 50
    u_data["coins"] += reward
    bot.send_message(message.chat.id, f"🎁 Ежедневная награда получена! Тебе начислено `{reward} некокойнов` 🪙", parse_mode="Markdown", reply_to_message_id=message.message_id)

@bot.message_handler(func=lambda m: m.text and m.text.lower().strip() in ["кастомрп", "кастом", "рппанель"])
def rp_panel_word(message):
    chat_id = message.chat.id
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("➕ Добавить РП-команду", callback_data="rp_menu_add"),
        InlineKeyboardButton("📜 Список кастомных команд", callback_data="rp_menu_list"),
        InlineKeyboardButton("🗑 Удалить кастомную команду", callback_data="rp_menu_del")
    )
    bot.send_message(
        chat_id,
        "🛠 **Панель кастомных РП-команд**\n\nВыбирай нужное действие:",
        reply_markup=markup,
        parse_mode="Markdown"
    )

# Управление кастомными РП-командами
@bot.callback_query_handler(func=lambda call: call.data.startswith("rp_menu_"))
def rp_menu_callback(call):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    data = call.data
    
    if data == "rp_menu_add":
        USER_ADDING_STATE[user_id] = chat_id
        bot.answer_callback_query(call.id)
        bot.send_message(
            chat_id,
            "✍️ **Создание новой РП-команды**\n\n"
            "Отправь в чат данные в формате:\n"
            "`название | текст_для_двоих | текст_одного | ссылка_на_гифку`",
            parse_mode="Markdown"
        )
    elif data == "rp_menu_list":
        bot.answer_callback_query(call.id)
        customs = CHAT_CUSTOM_RP.get(chat_id, {})
        if not customs:
            bot.send_message(chat_id, "📜 В этом чате нет кастомных команд.")
        else:
            lst = "\n".join([f"🔹 `{name}`" for name in customs.keys()])
            bot.send_message(chat_id, f"📜 **Кастомные команды:**\n\n{lst}", parse_mode="Markdown")
    elif data == "rp_menu_del":
        bot.answer_callback_query(call.id)
        customs = CHAT_CUSTOM_RP.get(chat_id, {})
        if not customs:
            bot.send_message(chat_id, "🗑 Удалять нечего.")
            return
        markup = InlineKeyboardMarkup(row_width=2)
        buttons = [InlineKeyboardButton(name, callback_data=f"rp_del_{name}") for name in customs.keys()]
        markup.add(*buttons)
        bot.send_message(chat_id, "🗑 **Выбери команду для удаления:**", reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith("rp_del_"))
def rp_delete_callback(call):
    chat_id = call.message.chat.id
    cmd_name = call.data.replace("rp_del_", "", 1)
    if chat_id in CHAT_CUSTOM_RP and cmd_name in CHAT_CUSTOM_RP[chat_id]:
        del CHAT_CUSTOM_RP[chat_id][cmd_name]
        bot.answer_callback_query(call.id, f"Команда '{cmd_name}' удалена!")
        bot.edit_message_text(f"🗑 Команда **{cmd_name}** удалена!", chat_id, call.message.message_id, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.from_user.id in USER_ADDING_STATE)
def process_new_rp(message):
    user_id = message.from_user.id
    chat_id = USER_ADDING_STATE.pop(user_id, None)
    if not chat_id or message.chat.id != chat_id or not message.text:
        return
    parts = message.text.split("|")
    if len(parts) < 4:
        bot.send_message(chat_id, "❌ Ошибка формата! Нужно 4 части через `|`.", parse_mode="Markdown")
        return
    name = parts[0].strip().lower()
    CHAT_CUSTOM_RP.setdefault(chat_id, {})[name] = {
        "aliases": [name],
        "target_text": parts[1].strip(),
        "solo_text": parts[2].strip(),
        "gifs": [parts[3].strip()]
    }
    bot.send_message(chat_id, f"✅ Кастомная команда `{name}` добавлена!", parse_mode="Markdown", reply_to_message_id=message.message_id)

# ==========================================
# ОБРАБОТЧИК РП КОМАНД + ФАРМ
# ==========================================
@bot.message_handler(func=lambda m: m.text and m.text.lower().strip() in ["команды", "помощь", "/help"])
def show_all_commands(message):
    text = (
        "📜 **Список всех команд:**\n\n"
        "🎭 **РП-команды:** поцеловать, обнять, погладить, укусить, покормить, оставить засос, флиртовать, трахнуть\n"
        "🪙 **Экономика:** баланс, профиль, магазин, награда\n"
        "🛠 **Кастом:** кастомрп (панель создания)"
    )
    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_to_message_id=message.message_id)

def get_rp_action(message_text, chat_id):
    if not message_text:
        return None
    text_low = message_text.lower().strip()
    if chat_id in CHAT_CUSTOM_RP:
        for action_key, data in CHAT_CUSTOM_RP[chat_id].items():
            for alias in data["aliases"]:
                if text_low.startswith(alias):
                    return data
    for action_key, data in RP_COMMANDS.items():
        for alias in data["aliases"]:
            if text_low.startswith(alias):
                return data
    return None

@bot.message_handler(func=lambda m: get_rp_action(m.text, m.chat.id) is not None)
def handle_rp(message):
    user = message.from_user
    u_data = get_user_data(user.id)
    update_passive_coins(u_data)
    
    # Фарм монет за РП (с учетом ушек: x3 если надеты)
    gain = 3 if "ears" in u_data["active_effects"] else 1
    u_data["coins"] += gain
    u_data["stats"]["actions"] += 1
    if "обнять" in message.text.lower():
        u_data["stats"]["hugs"] += 1
    elif "поцеловать" in message.text.lower() or "поцелуй" in message.text.lower():
        u_data["stats"]["kisses"] += 1

    action_data = get_rp_action(message.text, message.chat.id)
    sender = user.first_name

    if message.reply_to_message:
        target = message.reply_to_message.from_user.first_name
        text = action_data["target_text"].format(sender=sender, target=target)
    else:
        text = action_data["solo_text"].format(sender=sender)

    # Применение эффектов к тексту ответа (префиксы)
    prefix = ""
    if "ears" in u_data["active_effects"]:
        prefix += "мурр..~ "
    if "rose" in u_data["active_effects"]:
        prefix += "🌹 *с нежным трепетом* — "
    if "crown" in u_data["active_effects"]:
        prefix += "👑 Господин, "

    text = prefix + text

    gifs = action_data["gifs"]
    if gifs:
        gif_to_send = random.choice(gifs)
        formatted_text = f"{text}\n<a href='{gif_to_send}'>&#8204;</a>"
        bot.send_message(message.chat.id, text=formatted_text, parse_mode="HTML", reply_to_message_id=message.message_id)
    else:    
        bot.send_message(message.chat.id, text=text, parse_mode="HTML", reply_to_message_id=message.message_id)

# Пассивный фарм и префиксы для обычных сообщений
@bot.message_handler(func=lambda m: True)
def passive_farm_and_prefix(message):
    if message.text and not message.text.startswith('/'):
        user_id = message.from_user.id
        u_data = get_user_data(user_id)
        update_passive_coins(u_data)
        
        # Начисление за сообщение (ушки дают 3 вместо 1)
        gain = 3 if "ears" in u_data["active_effects"] else 1
        u_data["coins"] += gain

        # Если у пользователя включен какой-то префикс, можно опционально подменять или просто фиксировать
        # (Обычно сообщения пользователей бот не переписывает, но можно сделать автоответ или логирование, либо применить префикс к РП-ответам)

# ==========================================
# ЗАПУСК БОТА
# ==========================================

def run_bot():
    bot.infinity_polling()

if __name__ == "__main__":
    t = threading.Thread(target=run_bot)
    t.start()

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)