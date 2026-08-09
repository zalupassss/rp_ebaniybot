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

# 📚 База РП-команд
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
        "gifs": ["https://media1.tenor.com/m/TRuJrALdXnoAAAAC/lycoris-recoil-anime-feed.gif"],
    },
}

@bot.message_handler(func=lambda m: m.text and m.text.lower().strip() in ["команды", "/команды", "!команды", "рп команды"])
def show_commands(message):
    cmds_list = "\n".join([f"🔸 `{data['aliases'][0]}`" for key, data in RP_COMMANDS.items()])
    
    text = (
        "📜 **Список доступных РП-команд:**\n\n"
        f"{cmds_list}\n\n"
        "💡 _Напиши любую из этих команд просто в чат или в ответ (reply) на сообщение другого участника._\n"
        "🎮 _А еще можно сыграть в игру: /krestiki_"
    )
    
    bot.send_message(
        chat_id=message.chat.id, 
        text=text, 
        parse_mode="Markdown"
    )

def get_rp_action(message_text):
    if not message_text:
        return None
    text_low = message_text.lower().strip()
    for action_key, data in RP_COMMANDS.items():
        for alias in data["aliases"]:
            if text_low.startswith(alias):
                return data
    return None

@bot.message_handler(func=lambda m: get_rp_action(m.text) is not None)
def handle_rp(message):
    action_data = get_rp_action(message.text)
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
        
        # Без blockquote (нет значка цитаты), но со скрытой ссылкой для гифки
        formatted_text = f"{text}\n<a href='{gif_to_send}'>&#8204;</a>"
        
        bot.send_message(
            chat_id=message.chat.id,
            text=formatted_text,
            parse_mode="HTML",
            reply_to_message_id=message.message_id,  # Бот делает реплай на команду
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

    # Подключение второго игрока
    if game['p2'] is None and user_id != game['p1']:
        game['p2'] = user_id
        game['p2_name'] = user_name

    # Проверка хода
    current_symbol = game['turn']
    current_player_id = game['p1'] if current_symbol == '❌' else game['p2']

    if user_id != current_player_id:
        if user_id == game['p1'] or user_id == game['p2']:
            bot.answer_callback_query(call.id, "Сейчас не твой ход!")
        else:
            bot.answer_callback_query(call.id, "Игра уже идет между другими игроками!")
        return

    # Занята ли клетка
    if game['board'][idx] != " ":
        bot.answer_callback_query(call.id, "Эта клетка уже занята!")
        return

    # Записываем ход
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
        # Смена хода
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
    # Запускаем телеграм-бота в отдельном потоке
    t = threading.Thread(target=run_bot)
    t.start()

    # Запускаем веб-сервер для Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
