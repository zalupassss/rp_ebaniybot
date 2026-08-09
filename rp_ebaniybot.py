import os
import random
import threading
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask

# 🔑 Вставь сюда свой токен от @BotFather
TOKEN = "8892392566:AAE0rSE7QW21zfgZsKhIpf9NrU4OjxR52HY"
bot = telebot.TeleBot(TOKEN)

# Создаем мини-сайт для Render, чтобы хостинг понимал, что проект живой
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
    "засосать": {
        "aliases": ["засосать", "!засосать"],
        "target_text": "🔥 <b>{sender}</b> страстно засосался с <b>{target}</b>!",
        "solo_text": "😳 <b>{sender}</b> ищет, кого бы засосать...",
        "gifs": ["https://media1.tenor.com/m/9u2vmryDP-cAAAAC/horimiya-animes.gif"],
    },
    "укусить": {
        "aliases": ["укусить", "/bite", "!укусить", "куснуть"],
        "target_text": "🦷 <b>{sender}</b> делает аккуратный «кусь» <b>{target}</b>!",
        "solo_text": "😬 <b>{sender}</b> делает «кусь» воздуха!",
        "gifs": ["https://media1.tenor.com/m/5mVQ3ffWUTgAAAAC/anime-bite.gif"],
    },
    "трахнуть": {
        "aliases": ["трахнуть", "!трахнуть"],
        "target_text": "💥 <b>{sender}</b> трахнул <b>{target}</b>!",
        "solo_text": "⚡️ <b>{sender}</b> но член не встал...",
        "gifs": ["https://media1.tenor.com/m/9G1zsVIiV6UAAAAC/anime-bed.gif"],
    },
    "флиртовать": {
        "aliases": ["флиртовать", "/flirt", "!флиртовать"],
        "target_text": "😏 <b>{sender}</b> пофлиртовал с <b>{target}</b>!",
        "solo_text": "😏 <b>{sender}</b> красиво строит глазки... воздуху..",
        "gifs": ["https://media1.tenor.com/m/JBNgKsQdUmEAAAAC/anime.gif"],
    },
    "оставитьзасос": {
        "aliases": [
            "оставить засос",
            "оставить_засос",
            "!оставить засос",
            "засос",
        ],
        "target_text": "🧛 <b>{sender}</b> оставляет сочный засос на шее <b>{target}</b>!",
        "solo_text": "🧛 <b>{sender}</b> хищно засосал воздух...",
        "gifs": ["https://media1.tenor.com/m/5FOgNEcoaYMAAAAC/neck-kisses.gif"],
    },
    "покормить": {
        "aliases": ["покормить", "/feed", "!покормить", "накормить"],
        "target_text": "🍲 <b>{sender}</b> вкусно кормит <b>{target}</b>! Теперь кто-то сыт и доволен 😊",
        "solo_text": "🍲 <b>{sender}</b> вкусно кушает! Приятного аппетита 😋",
        "gifs": ["https://media1.tenor.com/m/y_xVq9Ea-YUAAAAC/anime-acchi-kocchi.gif"],
    },
}

# 🛠 Хранилище кастомных команд и состояний ввода
CHAT_CUSTOM_RP = {}  # {chat_id: {command_name: data_dict}}
USER_ADDING_STATE = {}  # {user_id: chat_id}

@bot.message_handler(func=lambda m: m.text and m.text.lower().strip() in ["команды", "/команды", "!команды", "рп команды"])
def show_commands(message):
    cmds_list = "\n".join([f"🔸 `{data['aliases'][0]}`" for key, data in RP_COMMANDS.items()])
    
    # Добавляем кастомные, если есть в этом чате
    chat_id = message.chat.id
    if chat_id in CHAT_CUSTOM_RP and CHAT_CUSTOM_RP[chat_id]:
        custom_list = "\n".join([f"🔹 `{name}` *(кастомная)*" for name in CHAT_CUSTOM_RP[chat_id].keys()])
        cmds_list += f"\n{custom_list}"
    
    text = (
        "📜 **Список доступных РП-команд:**\n\n"
        f"{cmds_list}\n\n"
        "💡 _Напиши любую команду в чат или в ответ на сообщение._\n"
        "🛠 _Управление своими командами: /rppanel_\n"
        "🎮 _Играть в крестики-нолики: /krestiki_"
    )
    
    bot.send_message(
        chat_id=message.chat.id, 
        text=text, 
        parse_mode="Markdown"
    )

# ==========================================
# ИНТЕРАКТИВНАЯ ПАНЕЛЬ КАСТОМНЫХ КОМАНД
# ==========================================

@bot.message_handler(commands=['rppanel', 'custom'])
def rp_panel(message):
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
            "`пнуть | 🥾 {sender} со всей дури пинает {target}! | 🥾 {sender} пинает воздух... | https://media1.tenor.com/m/GAr1rMm39pcAAAAC/anime-hug.gif`\n\n"
            "*(Просто напиши это в ответ на это сообщение или в чат)*",
            parse_mode="Markdown"
        )
    elif data == "rp_menu_list":
        bot.answer_callback_query(call.id)
        customs = CHAT_CUSTOM_RP.get(chat_id, {})
        if not customs:
            bot.send_message(chat_id, "📜 В этом чате пока нет кастомных команд. Создай первую через кнопку выше!")
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
    
    if not chat_id or message.chat.id != chat_id:
        return
        
    if not message.text:
        return
        
    parts = message.text.split("|")
    if len(parts) < 4:
        bot.send_message(chat_id, "❌ **Ошибка формата!** Нужно указать ровно 4 части через вертикальную черту `|`.\nНажми снова `/rppanel` и попробуй еще раз.", parse_mode="Markdown")
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
        f"✅ **Успешно!** Новая кастомная команда `{name}` добавлена.\nТеперь её можно использовать в чате!",
        parse_mode="Markdown",
        reply_to_message_id=message.message_id
    )

# ==========================================
# ОБРАБОТЧИК РП КОМАНД
# ==========================================

def get_rp_action(message_text, chat_id):
    if not message_text:
        return None
    text_low = message_text.lower().strip()
    
    # 1. Сначала проверяем кастомные команды этого чата
    if chat_id in CHAT_CUSTOM_RP:
        for action_key, data in CHAT_CUSTOM_RP[chat_id].items():
            for alias in data["aliases"]:
                if text_low.startswith(alias):
                    return data
                    
    # 2. Затем стандартные глобальные команды
    for action_key, data in RP_COMMANDS.items():
        for alias in data["aliases"]:
            if text_low.startswith(alias):
                return data
    return None

@bot.message_handler(func=lambda m: get_rp_action(m.text, m.chat.id) is not None)
def handle_rp(message):
    action_data = get_rp_action(message.text, message.chat.id)
    sender = message.from_user.first_name

    if message.reply_to_message:
        target = message.reply_to_message.from_user.first_name
        text = action_data["target_text"].format(
            sender=sender, target=target
        )
    else:
        text = action_data["solo_text"].format(sender=sender)

    gifs = action_data["gifs"]

    if gifs:
        gif_to_send = random.choice(gifs)
        formatted_text = f"{text}\n<a href='{gif_to_send}'>&#8204;</a>"
        
        bot.send_message(
            chat_id=message.chat.id,
            text=formatted_text,
            parse_mode="HTML",
            reply_to_message_id=message.message_id,
        )
    else:    
        bot.send_message(
            chat_id=message.chat.id,
            text=f"{text}\n\n<i>(Гифка ещё не привязана)</i>",
            parse_mode="HTML",
            reply_to_message_id=message.message_id,
        )

# ==========================================
# ИГРА: КРЕСТИКИ-НОЛИКИ
# ==========================================

ttt_games = {}

def get_ttt_keyboard(board):
    markup = InlineKeyboardMarkup(row_width=3)
    buttons = []
    for i in range(9):
        text = board[i] if board[i] != " " else "⬜"
        buttons.append(InlineKeyboardButton(text, callback_data=f"ttt_{i}"))
    markup.add(*buttons)
    return markup

def check_ttt_winner(b):
    win_combinations = [
        (0,1,2), (3,4,5), (6,7,8),  # горизонтали
        (0,3,6), (1,4,7), (2,5,8),  # вертикали
        (0,4,8), (2,4,6)            # диагонали
    ]
    for x, y, z in win_combinations:
        if b[x] == b[y] == b[z] and b[x] != " ":
            return b[x]
    if " " not in b:
        return "Draw"
    return None

@bot.message_handler(commands=['krestiki', 'ttt'])
def start_ttt(message):
    chat_id = message.chat.id
    ttt_games[chat_id] = {
        'board': [" "] * 9,
        'turn': '❌',
        'p1': message.from_user.id,
        'p1_name': message.from_user.first_name,
        'p2': None,
        'p2_name': None
    }
    
    bot.send_message(
        chat_id,
        f"🎮 **Крестики-Нолики**\n\nИгрок **{message.from_user.first_name}** ходит первым (❌).\nВторой игрок, нажми на любую клетку, чтобы вступить в игру (⭕)!",
        reply_markup=get_ttt_keyboard(ttt_games[chat_id]['board']),
        parse_mode="Markdown"
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("ttt_"))
def ttt_click(call):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    user_name = call.from_user.first_name

    if chat_id not in ttt_games:
        bot.answer_callback_query(call.id, "Эта игра уже завершена. Начните новую командой /krestiki!")
        return

    game = ttt_games[chat_id]
    idx = int(call.data.split("_")[1])

    if game['p2'] is None and user_id != game['p1']:
        game['p2'] = user_id
        game['p2_name'] = user_name

    current_symbol = game['turn']
    current_player_id = game['p1'] if current_symbol == '❌' else game['p2']

    if user_id != current_player_id:
        if user_id == game['p1'] or user_id == game['p2']:
            bot.answer_callback_query(call.id, "Сейчас не твой ход!")
        else:
            bot.answer_callback_query(call.id, "Игра уже идет между другими игроками!")
        return

    if game['board'][idx] != " ":
        bot.answer_callback_query(call.id, "Эта клетка уже занята!")
        return

    game['board'][idx] = current_symbol
    winner = check_ttt_winner(game['board'])

    if winner:
        board_markup = get_ttt_keyboard(game['board'])
        if winner == "Draw":
            text = "🤝 **Ничья!** Победила дружба."
        else:
            win_name = game['p1_name'] if winner == '❌' else game['p2_name']
            text = f"🎉 Победил(а) **{win_name}** ({winner})! Поздравляем!"
        
        bot.edit_message_text(text, chat_id, call.message.message_id, reply_markup=board_markup, parse_mode="Markdown")
        del ttt_games[chat_id]
    else:
        game['turn'] = '⭕' if current_symbol == '❌' else '❌'
        next_name = game['p2_name'] if game['turn'] == '⭕' else game['p1_name']
        next_str = next_name if next_name else "Второй игрок (⭕)"
        
        text = f"🎮 **Крестики-Нолики**\nСейчас ход: {game['turn']} (**{next_str}**)"
        bot.edit_message_text(text, chat_id, call.message.message_id, reply_markup=get_ttt_keyboard(game['board']), parse_mode="Markdown")

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