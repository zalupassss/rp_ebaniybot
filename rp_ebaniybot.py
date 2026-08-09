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
        "target_text": "💋 **{sender}** целует **{target}**!",
        "solo_text": "💋 **{sender}** целует воздух... Кого-то явно не хватает!",
        "gifs": ["https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExMmF2bjhuN3M2cTUxMHhlbms2M3Y0NnMwMzZyOHJ1OWpnNXZzdWhoNiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/NDV8xXN4VRf8CiMAx5/giphy.gif"],
    },
    "обнять": {
        "aliases": ["обнять", "/hug", "!обнять"],
        "target_text": "🫂 **{sender}** крепко-крепко обнимает **{target}**!",
        "solo_text": "🤗 **{sender}** обнимает весь чат!",
        "gifs": ["https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExdGg5YXlrZXN3aXdubG5sMmR1ZHVoZ2x3YWQwdXhnZjQzbjljZWg4cSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/svXXBgduBsJ1u/giphy.gif"],
    },
    "погладить": {
        "aliases": ["погладить", "/pat", "!погладить"],
        "target_text": "🫳 **{sender}** нежно гладит **{target}** по голове!",
        "solo_text": "🫳 **{sender}** гладит сам себя...",
        "gifs": ["https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExaHVkazJ3ajB1MnZscnhkZXhrdmNoeXllaHBuY2Y3MWs3aHV1bmwzNyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/5tmRHwTlHAA9WkVxTU/giphy.gif"],
    },
    "засосать": {
        "aliases": ["засосать", "!засосать"],
        "target_text": "🔥 **{sender}** страстно засосался с **{target}**!",
        "solo_text": "😳 **{sender}** ищет, кого бы засосать...",
        "gifs": ["https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExb2dkem8wYTE1Y25laGwwc3Q3dXE5MmI3dnp5cmxnZG95ZW0xMDBzOSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/MQVpBqASxSlFu/giphy.gif"],
    },
    "укусить": {
        "aliases": ["укусить", "/bite", "!укусить", "куснуть"],
        "target_text": "🦷 **{sender}** делает аккуратный «кусь» **{target}**!",
        "solo_text": "😬 **{sender}** делает «кусь» воздуха!",
        "gifs": ["https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExc2FzeHFmaGtjZm1veXVwdzEzdWozd2hiZnRlNjhra3J4Y2ZzbDFhaCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/l0Iy0QdzD3AA6bgIg/giphy.gif"],
    },
    "трахнуть": {
        "aliases": ["трахнуть", "!трахнуть"],
        "target_text": "💥 **{sender}** трахнул **{target}**!",
        "solo_text": "⚡️ **{sender}** но член не встал...",
        "gifs": ["https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExMjZodmFrbzV3cXJqYTBxaTZvZXh2M201ZTZjZWxqemx4eTRqbzZnMiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/rFYcBg4JuDDP2/giphy.gif"],
    },
    "флиртовать": {
        "aliases": ["флиртовать", "/flirt", "!флиртовать"],
        "target_text": "😏 **{sender}** пофлиртовал с **{target}**!",
        "solo_text": "😏 **{sender}** красиво строит глазки... воздуху..",
        "gifs": ["https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExcGpmb2Flb3V3dGw0aWY0eXh6c3hrM3pwY3hpZDVzeTFiZG9lZDRvZSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/P787NFr8HnP3NvFz89/giphy.gif"],
    },
    "засосать_в_шею": {
        "aliases": [
            "засосать в шею",
            "засосать_в_шею",
            "!засосать в шею",
            "укусить в шею",
        ],
        "target_text": "🧛 **{sender}** оставляет сочный засос на шее **{target}**!",
        "solo_text": "🧛 **{sender}** хищно засосал воздух...",
        "gifs": ["https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHUxdGZ0NmZrNmltNm12YTNmMDV1YWVqa2s0MGt6c3QwNmg1d3BjcyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/WynnqxhdFEPYY/giphy.gif"],
    },
    "покормить": {
        "aliases": ["покормить", "/feed", "!покормить", "накормить"],
        "target_text": "🍲 **{sender}** вкусно кормит **{target}**! Теперь кто-то сыт и доволен 😊",
        "solo_text": "🍲 **{sender}** вкусно кушает! Приятного аппетита 😋",
        "gifs": ["https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExYjB1OHRpMWZ4NmJtcnVpMDlraWhreTljNGpqYTR6OHRia3hrYnVqdiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/POl4x8sulgMF2ZrBrz/giphy.gif"],
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
        
        # Используем send_animation для автовоспроизведения гифки
        bot.send_animation(
            chat_id=message.chat.id,
            animation=gif_to_send,
            caption=text, # Текст становится подписью под гифкой
            parse_mode="Markdown", # Используем Markdown, чтобы работали ** **
            reply_to_message_id=message.message_id,
        )
    else:   
        bot.send_message(
            chat_id=message.chat.id,
            text=f"{text}\n\n_(Гифка ещё не привязана)_",
            parse_mode="Markdown",
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
