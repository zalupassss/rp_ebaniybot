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
}

# 🛠 Базы данных в памяти
CHAT_CUSTOM_RP = {}        # {chat_id: {command_name: data_dict}}
USER_ADDING_STATE = {}     # {user_id: chat_id}
USERS_ECONOMY = {}         # {user_id: {"coins": 0, "inventory": [], "stats": {"hugs": 0, "kisses": 0, "actions": 0}, "last_daily": 0}}
SHOP_ITEMS = {
    "ears": {"name": "🐾 Кошачьи ушки", "price": 100, "desc": "Милый аксессуар в твой профиль."},
    "ramen": {"name": "🍜 Рамен быстрого приготовления", "price": 50, "desc": "Сытный перекус для бодрости."},
    "rose": {"name": "🌹 Алая роза", "price": 150, "desc": "Красивый цветок для подарков."},
    "crown": {"name": "👑 Корона властелина чата", "price": 500, "desc": "Элитный статус главного тусовщика."}
}

def get_user_data(user_id):
    if user_id not in USERS_ECONOMY:
        USERS_ECONOMY[user_id] = {
            "coins": 50,  # Стартовый бонус
            "inventory": [],
            "stats": {"hugs": 0, "kisses": 0, "actions": 0},
            "last_daily": 0
        }
    return USERS_ECONOMY[user_id]

# ==========================================
# ТЕКСТОВЫЕ ТРИГГЕРЫ: профиль, баланс, магазин, кастомрп
# ==========================================

@bot.message_handler(func=lambda m: m.text and m.text.lower().strip() in ["баланс", "монеты", "коинс"])
def show_balance(message):
    u_data = get_user_data(message.from_user.id)
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
    inv = ", ".join([SHOP_ITEMS[item]["name"] for item in u_data["inventory"]]) or "Пусто"
    
    text = (
        f"👤 **Профиль: {user.first_name}**\n\n"
        f"🪙 Баланс: `{u_data['coins']} некокойнов`\n"
        f"🎒 Инвентарь: {inv}\n"
        f"📊 Статистика РП:\n"
        f" • Всего действий: `{u_data['stats']['actions']}`\n"
        f" • Объятий: `{u_data['stats']['hugs']}`\n"
        f" • Поцелуев: `{u_data['stats']['kisses']}`"
    )
    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_to_message_id=message.message_id)

@bot.message_handler(func=lambda m: m.text and m.text.lower().strip() == "магазин")
def show_shop(message):
    markup = InlineKeyboardMarkup(row_width=1)
    for key, item in SHOP_ITEMS.items():
        markup.add(InlineKeyboardButton(f"{item['name']} — {item['price']} 🪙", callback_data=f"buy_{key}"))
    
    bot.send_message(
        message.chat.id,
        "🛍 **Неко-Магазин товаров**\n\nВыбирай позицию, чтобы приобрести её за некокойны:",
        reply_markup=markup,
        parse_mode="Markdown"
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
def buy_item(call):
    user_id = call.from_user.id
    item_key = call.data.replace("buy_", "", 1)
    u_data = get_user_data(user_id)
    
    if item_key not in SHOP_ITEMS:
        bot.answer_callback_query(call.id, "Товар не найден!")
        return
        
    item = SHOP_ITEMS[item_key]
    if item_key in u_data["inventory"]:
        bot.answer_callback_query(call.id, "У тебя уже есть этот предмет!", show_alert=True)
        return
        
    if u_data["coins"] < item["price"]:
        bot.answer_callback_query(call.id, f"Не хватает некокойнов! Нужно {item['price']} 🪙", show_alert=True)
        return
        
    u_data["coins"] -= item["price"]
    u_data["inventory"].append(item_key)
    bot.answer_callback_query(call.id, f"Успешная покупка: {item['name']}!", show_alert=True)
    bot.edit_message_text(
        f"✅ Вы успешно приобрели **{item['name']}**!\nПроверить инвентарь можно написав слово `профиль`.",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda m: m.text and m.text.lower().strip() in ["награда", "/daily"])
def daily_reward(message):
    user_id = message.from_user.id
    u_data = get_user_data(user_id)
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
        "🛠 **Панель кастомных РП-команд**\n\nВыбирай нужное действие с помощью кнопок ниже:",
        reply_markup=markup,
        parse_mode="Markdown"
    )

# ==========================================
# УПРАВЛЕНИЕ КАСТОМНЫМИ КОМАНДАМИ (КНОПКИ)
# ==========================================

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
            "Отправь в чат одним сообщением данные в таком формате:\n"
            "`название | текст_для_двоих | текст_одного | ссылка_на_гифку`\n\n"
            "📌 **Пример:**\n"
            "`пнуть | 🥾 {sender} со всей дури пинает {target}! | 🥾 {sender} пинает воздух... | https://media1.tenor.com/m/GAr1rMm39pcAAAAC/anime-hug.gif`",
            parse_mode="Markdown"
        )
    elif data == "rp_menu_list":
        bot.answer_callback_query(call.id)
        customs = CHAT_CUSTOM_RP.get(chat_id, {})
        if not customs:
            bot.send_message(chat_id, "📜 В этом чате пока нет кастомных команд. Создай первую через меню `кастомрп`!")
        else:
            lst = "\n".join([f"🔹 `{name}`" for name in customs.keys()])
            bot.send_message(chat_id, f"📜 **Кастомные команды этого чата:**\n\n{lst}", parse_mode="Markdown")
    elif data == "rp_menu_del":
        bot.answer_callback_query(call.id)
        customs = CHAT_CUSTOM_RP.get(chat_id, {})
        if not customs:
            bot.send_message(chat_id, "🗑 Удалять нечего — в чате нет кастомных команд.")
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
        bot.edit_message_text(f"🗑 Кастомная команда **{cmd_name}** успешно удалена!", chat_id, call.message.message_id, parse_mode="Markdown")
    else:
        bot.answer_callback_query(call.id, "Команда не найдена.")

@bot.message_handler(func=lambda m: m.from_user.id in USER_ADDING_STATE)
def process_new_rp(message):
    user_id = message.from_user.id
    chat_id = USER_ADDING_STATE.pop(user_id, None)
    
    if not chat_id or message.chat.id != chat_id or not message.text:
        return
        
    parts = message.text.split("|")
    if len(parts) < 4:
        bot.send_message(chat_id, "❌ **Ошибка формата!** Нужно указать ровно 4 части через вертикальную черту `|`.", parse_mode="Markdown")
        return
        
    name = parts[0].strip().lower()
    target_text = parts[1].strip()
    solo_text = parts[2].strip()
    gif_url = parts[3].strip()
    
    if chat_id not in CHAT_CUSTOM_RP:
        CHAT_CUSTOM_RP[chat_id] = {}
        
    CHAT_CUSTOM_RP[chat_id][name] = {
        "aliases": [name],
        "target_text": target_text,
        "solo_text": solo_text,
        "gifs": [gif_url]
    }
    
    bot.send_message(
        chat_id,
        f"✅ **Успешно!** Новая кастомная команда `{name}` добавлена.",
        parse_mode="Markdown",
        reply_to_message_id=message.message_id
    )

# ==========================================
# ОБРАБОТЧИК РП КОМАНД + ФАРМ МОНЕТ
# ==========================================

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
    
    # Фарм за РП действие
    u_data["coins"] += 2
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

    gifs = action_data["gifs"]
    if gifs:
        gif_to_send = random.choice(gifs)
        formatted_text = f"{text}\n<a href='{gif_to_send}'>&#8204;</a>"
        bot.send_message(message.chat.id, text=formatted_text, parse_mode="HTML", reply_to_message_id=message.message_id)
    else:    
        bot.send_message(message.chat.id, text=f"{text}\n\n<i>(Гифка не привязана)</i>", parse_mode="HTML", reply_to_message_id=message.message_id)

# Пассивный фарм за обычные сообщения
@bot.message_handler(func=lambda m: True)
def passive_farm(message):
    if message.text and not message.text.startswith('/'):
        u_data = get_user_data(message.from_user.id)
        u_data["coins"] += 1  # 1 некокойн за обычное сообщение

# ==========================================
# ЗАПУСК БОТА
# ==========================================

def run_bot():
    bot.infinity_polling()

if __name__ == "__main__":
    t = threading.Thread(target=run_bot)
    t.start()

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.00.0.0", port=port)